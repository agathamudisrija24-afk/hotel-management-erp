from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import *
from app.core.security import hash_password,verify_password,token
from app.api.deps import current_user, optional_current_user, require, can_access_hotel
from app.services.booking import available_rooms,create_booking
api=APIRouter()
class Register(BaseModel): email: EmailStr; password: str=Field(min_length=8); name: str
class Login(BaseModel): email: EmailStr; password: str
class ProfileUpdate(BaseModel): name: str = Field(min_length=1, max_length=150); phone: str = Field(default="", max_length=30)
@api.post('/auth/register',status_code=201)
def register(body:Register,db:Session=Depends(get_db)):
    if db.query(User).filter_by(email=body.email.lower()).first(): raise HTTPException(409,"Email already registered")
    user=User(email=body.email.lower(),name=body.name,password_hash=hash_password(body.password)); db.add(user); db.flush(); role=db.query(Role).filter_by(name="customer").first(); db.add(UserRole(user_id=user.id,role_id=role.id)); db.commit(); return {"id":user.id,"email":user.email}
@api.post('/auth/login')
def login(body:Login,db:Session=Depends(get_db)):
    user=db.query(User).filter_by(email=body.email.lower()).first()
    if not user or not verify_password(body.password,user.password_hash): raise HTTPException(401,"Invalid credentials")
    role=db.query(Role).join(UserRole).filter(UserRole.user_id==user.id).first(); return {"access_token":token(user.id,role.name if role else "customer"),"token_type":"bearer","user":{"id":user.id,"name":user.name,"email":user.email,"role":role.name if role else "customer"}}
@api.get('/auth/me')
def me(user=Depends(current_user),db:Session=Depends(get_db)):
    roles=[r.name for r in db.query(Role).join(UserRole).filter(UserRole.user_id==user.id)]
    return {"id":user.id,"name":user.name,"email":user.email,"phone":user.phone,"roles":roles,"created_at":user.created_at}
@api.patch('/auth/me')
def update_me(body: ProfileUpdate, user=Depends(current_user), db: Session=Depends(get_db)):
    user.name, user.phone = body.name.strip(), body.phone.strip()
    db.commit()
    return me(user, db)
@api.post('/auth/logout',status_code=204)
def logout(): return None
def hotel_summary(x, db):
    room_types = [{"id": r.id, "name": r.name, "rate": str(r.base_rate), "capacity": r.capacity, "available_rooms": len([room for room in r.rooms if room.status == "available"])} for r in x.room_types]
    images = db.query(HotelImage).filter_by(hotel_id=x.id).all()
    amenities = db.query(HotelAmenity).filter_by(hotel_id=x.id).all()
    return {"id": x.id, "name": x.name, "city": x.city, "address": x.address, "description": x.description, "rating": str(x.rating), "hotel_type": x.hotel_type, "images": [{"url": image.url, "alt": image.alt} for image in images], "services": [{"name": amenity.name, "description": amenity.description} for amenity in amenities], "room_types": room_types}


@api.get('/hotels')
def hotels(city:str|None=None,q:str|None=None,min_price:Decimal|None=None,max_price:Decimal|None=None,min_rating:Decimal|None=None,service:str|None=None,hotel_type:str|None=None,sort:str="name",page:int=1,size:int=12,db:Session=Depends(get_db)):
    query = db.query(Hotel).filter_by(published=True)
    if city: query = query.filter(Hotel.city.ilike(f'%{city}%'))
    if q: query = query.filter((Hotel.name.ilike(f'%{q}%')) | (Hotel.city.ilike(f'%{q}%')))
    if min_rating is not None: query = query.filter(Hotel.rating >= min_rating)
    if hotel_type: query = query.filter(Hotel.hotel_type.ilike(f'%{hotel_type}%'))
    items = query.all()
    if service:
        items = [hotel for hotel in items if any(service.lower() in amenity.name.lower() for amenity in db.query(HotelAmenity).filter_by(hotel_id=hotel.id))]
    def starting_price(hotel): return min((room.base_rate for room in hotel.room_types), default=Decimal("0"))
    if min_price is not None: items = [hotel for hotel in items if starting_price(hotel) >= min_price]
    if max_price is not None: items = [hotel for hotel in items if starting_price(hotel) <= max_price]
    if sort == "price_asc": items.sort(key=starting_price)
    elif sort == "price_desc": items.sort(key=starting_price, reverse=True)
    elif sort == "rating_desc": items.sort(key=lambda hotel: hotel.rating, reverse=True)
    else: items.sort(key=lambda hotel: hotel.name)
    total = len(items)
    items = items[(page - 1) * size:page * size]
    return {"items": [hotel_summary(hotel, db) for hotel in items], "total": total, "page": page}
@api.get('/hotels/{hotel_id}')
def hotel(hotel_id:str,db:Session=Depends(get_db)):
    x=db.get(Hotel,hotel_id)
    if not x or not x.published: raise HTTPException(404,"Hotel not found")
    result = hotel_summary(x, db)
    result["room_types"] = [{"id": r.id, "name": r.name, "description": r.description, "capacity": r.capacity, "rate": str(r.base_rate), "available_rooms": len([room for room in r.rooms if room.status == "available"])} for r in x.room_types]
    return result
@api.get('/availability')
def availability(room_type_id:str,check_in:str,check_out:str,db:Session=Depends(get_db)):
    from datetime import date
    rooms=available_rooms(db,room_type_id,date.fromisoformat(check_in),date.fromisoformat(check_out)); return {"available":len(rooms)}
class BookingIn(BaseModel): hotel_id:str; room_type_id:str; check_in:str; check_out:str; guests:int=1
@api.post('/bookings',status_code=201)
def booking(body:BookingIn,idempotency_key:str|None=Header(default=None),user=Depends(current_user),db:Session=Depends(get_db)):
    from datetime import date
    b=create_booking(db,user,body.hotel_id,body.room_type_id,date.fromisoformat(body.check_in),date.fromisoformat(body.check_out),body.guests,idempotency_key); db.commit(); return booking_out(b)
def booking_out(b, db: Session | None = None):
    hotel = db.get(Hotel, b.hotel_id) if db else None
    lines = []
    if db:
        for line in b.rooms:
            room = db.get(Room, line.room_id)
            room_type = db.get(RoomType, room.room_type_id) if room else None
            if room_type: lines.append({"room_type": room_type.name, "room_number": room.number, "nightly_rate": str(line.nightly_rate)})
    payment = db.query(Payment).filter_by(booking_id=b.id).order_by(Payment.created_at.desc()).first() if db else None
    return {"id":b.id,"reference":b.reference,"status":b.status,"total":str(b.total),"check_in":str(b.check_in),"check_out":str(b.check_out),"guests":b.guests,"created_at":b.created_at,"hold_expires_at":b.hold_expires_at,"hotel": {"id": hotel.id, "name": hotel.name, "city": hotel.city, "image_url": (db.query(HotelImage).filter_by(hotel_id=hotel.id).first() or HotelImage(url="", hotel_id=hotel.id)).url} if hotel else None,"rooms":lines,"payment_status":payment.status if payment else "not_started"}
@api.get('/bookings')
def bookings(user=Depends(current_user),db:Session=Depends(get_db)): return {"items":[booking_out(b, db) for b in db.query(Booking).filter_by(user_id=user.id).order_by(Booking.created_at.desc())]}
@api.get('/bookings/{booking_id}')
def get_booking(booking_id:str,user=Depends(current_user),db:Session=Depends(get_db)):
    b=db.get(Booking,booking_id)
    if not b or b.user_id!=user.id: raise HTTPException(404,"Booking not found")
    return booking_out(b, db)
@api.post('/bookings/{booking_id}/cancel')
def cancel(booking_id:str,user=Depends(current_user),db:Session=Depends(get_db)):
    b=db.get(Booking,booking_id)
    if not b or b.user_id!=user.id: raise HTTPException(404,"Booking not found")
    if b.status not in {"pending_payment","confirmed"}: raise HTTPException(409,"Booking cannot be cancelled")
    b.status="cancelled"; db.add(BookingStatusHistory(booking_id=b.id,status="cancelled",actor_id=user.id)); payment=db.query(Payment).filter_by(booking_id=b.id,status="paid").first()
    if payment: db.add(Refund(payment_id=payment.id,amount=payment.amount,status="succeeded",provider_refund_id="mock-refund-"+payment.id[:8]))
    db.commit(); return booking_out(b, db)
@api.post('/payments/initiate')
def initiate(booking_id:str,idempotency_key:str|None=Header(default=None),user=Depends(current_user),db:Session=Depends(get_db)):
    b=db.get(Booking,booking_id)
    if not b or b.user_id!=user.id or b.status!="pending_payment": raise HTTPException(409,"Booking is not payable")
    existing=db.query(Payment).filter_by(idempotency_key=idempotency_key).first() if idempotency_key else None
    if existing: return {"payment_id":existing.id,"provider":"mock","checkout_token":existing.provider_payment_id}
    p=Payment(booking_id=b.id,provider="mock",provider_payment_id="mock_"+b.id[:12],amount=b.total,status="created",idempotency_key=idempotency_key); db.add(p); db.commit(); return {"payment_id":p.id,"provider":"mock","checkout_token":p.provider_payment_id}
@api.post('/payments/{payment_id}/verify')
def verify(payment_id:str,user=Depends(current_user),db:Session=Depends(get_db)):
    p=db.get(Payment,payment_id); b=db.get(Booking,p.booking_id) if p else None
    if not p or not b or b.user_id!=user.id: raise HTTPException(404,"Payment not found")
    if p.status=="paid": return {"status":"paid","booking":booking_out(b)}
    if b.hold_expires_at and b.hold_expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc): raise HTTPException(409,"Inventory hold expired")
    p.status="paid"; b.status="confirmed"; b.hold_expires_at=None; db.add(BookingStatusHistory(booking_id=b.id,status="confirmed",actor_id=user.id)); db.add(Invoice(booking_id=b.id,number="INV-"+b.reference,amount=b.total)); db.commit(); return {"status":"paid","booking":booking_out(b)}
@api.post('/payments/webhook')
async def webhook(request:Request):
    # Razorpay integration verifies X-Razorpay-Signature before any state update; mock has no external webhook.
    return {"accepted":True}
@api.post('/staff/bookings/{booking_id}/{action}')
def stay_action(booking_id:str,action:str,user=Depends(require("admin","receptionist")),db:Session=Depends(get_db)):
    b=db.get(Booking,booking_id)
    if not b or action not in {"check-in","check-out"}: raise HTTPException(404,"Stay not found")
    if action=="check-in" and b.status=="confirmed": b.status="checked_in"; db.add(Stay(booking_id=b.id,checked_in_at=datetime.now(timezone.utc)))
    elif action=="check-out" and b.status=="checked_in": b.status="checked_out"; stay=db.query(Stay).filter_by(booking_id=b.id).first(); stay.checked_out_at=datetime.now(timezone.utc)
    else: raise HTTPException(409,"Invalid stay transition")
    db.add(BookingStatusHistory(booking_id=b.id,status=b.status,actor_id=user.id)); db.commit(); return booking_out(b)
@api.get('/admin/reports/summary')
def report(user=Depends(require("admin")),db:Session=Depends(get_db)): return {"hotels":db.query(Hotel).count(),"bookings":db.query(Booking).count(),"revenue":str(sum((p.amount for p in db.query(Payment).filter_by(status="paid")),Decimal("0")))}

class PasswordChange(BaseModel): current_password: str; new_password: str = Field(min_length=8)
class ServiceIn(BaseModel): hotel_id: str; booking_id: str|None=None; type: str = Field(pattern="^(room_service|housekeeping|maintenance|extra)$"); priority: str = Field(default="normal",pattern="^(low|medium|high|normal|urgent)$"); description: str = Field(min_length=3,max_length=2000); category: str = Field(default="",max_length=100); room_number: str = Field(default="",max_length=30); preferred_time: str = Field(default="",max_length=80)
class ServiceUpdate(BaseModel): status: str|None = Field(default=None,pattern="^(open|pending|accepted|assigned|in_progress|completed|rejected|cancelled)$"); assigned_to: str|None=None
class OrderItemIn(BaseModel): food_item_id: str; quantity: int=Field(gt=0,le=20)
class OrderIn(BaseModel): hotel_id:str; booking_id:str|None=None; items:list[OrderItemIn]=Field(min_length=1)
class ReviewIn(BaseModel): booking_id:str; rating:int=Field(ge=1,le=5); body:str=Field(min_length=3,max_length=2000); cleanliness_rating:int=Field(default=5,ge=1,le=5); staff_rating:int=Field(default=5,ge=1,le=5); comfort_rating:int=Field(default=5,ge=1,le=5); dining_rating:int|None=Field(default=None,ge=1,le=5)
class GuestFeedbackIn(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    category: str = Field(pattern="^(website_experience|booking_experience|room_hotel_services|payment|technical_issue|feature_request|other)$")
    rating: int = Field(ge=1, le=5)
    message: str = Field(min_length=3, max_length=5000)
    suggestions: str = Field(default="", max_length=2000)
class ComplaintIn(BaseModel): hotel_id:str; body:str=Field(min_length=3,max_length=3000)
class NotificationRead(BaseModel): read:bool=True

@api.post('/auth/change-password',status_code=204)
def change_password(body:PasswordChange,user=Depends(current_user),db:Session=Depends(get_db)):
    if not verify_password(body.current_password,user.password_hash): raise HTTPException(400,"Current password is incorrect")
    user.password_hash=hash_password(body.new_password)
    for session in db.query(RefreshToken).filter_by(user_id=user.id,revoked=False): session.revoked=True
    db.commit(); return None

@api.get('/notifications')
def notifications(unread_only:bool=False,user=Depends(current_user),db:Session=Depends(get_db)):
    q=db.query(Notification).filter_by(user_id=user.id)
    if unread_only: q=q.filter_by(read=False)
    return {"items":[{"id":n.id,"type":n.type,"body":n.body,"read":n.read,"created_at":n.created_at} for n in q.order_by(Notification.created_at.desc())]}

@api.patch('/notifications/{notification_id}')
def mark_notification(notification_id:str,body:NotificationRead,user=Depends(current_user),db:Session=Depends(get_db)):
    n=db.get(Notification,notification_id)
    if not n or n.user_id!=user.id: raise HTTPException(404,"Notification not found")
    n.read=body.read; db.commit(); return {"id":n.id,"read":n.read}

@api.post('/services',status_code=201)
def create_service(body:ServiceIn,user=Depends(current_user),db:Session=Depends(get_db)):
    if not db.get(Hotel,body.hotel_id): raise HTTPException(404,"Hotel not found")
    room_number=body.room_number
    if body.booking_id:
        booking=db.get(Booking,body.booking_id)
        if not booking or booking.user_id!=user.id or booking.hotel_id!=body.hotel_id: raise HTTPException(403,"Booking does not belong to this account")
        if not room_number and booking.rooms:
            room=db.get(Room,booking.rooms[0].room_id)
            room_number=room.number if room else ""
    s=ServiceRequest(hotel_id=body.hotel_id,booking_id=body.booking_id,requested_by=user.id,type=body.type,priority=body.priority,description=body.description,category=body.category,room_number=room_number,preferred_time=body.preferred_time,status="open")
    db.add(s); db.flush(); db.add(ServiceRequestHistory(service_request_id=s.id,status="open",actor_id=user.id)); db.add(Notification(user_id=user.id,type="service",body="Service request created")); db.commit(); return service_out(s,db)
def service_out(s,db=None):
    histories=sorted(s.history,key=lambda h:h.created_at) if hasattr(s,"history") and s.history else (db.query(ServiceRequestHistory).filter_by(service_request_id=s.id).order_by(ServiceRequestHistory.created_at.desc()).all() if db else [])
    booking=db.get(Booking,s.booking_id) if db and s.booking_id else None
    hotel=db.get(Hotel,s.hotel_id) if db else None
    return {"id":s.id,"hotel_id":s.hotel_id,"hotel_name":hotel.name if hotel else "","booking_id":s.booking_id,"booking_reference":booking.reference if booking else "","type":s.type,"category":s.category,"priority":s.priority,"status":s.status,"assigned_to":s.assigned_to,"description":s.description,"room_number":s.room_number,"preferred_time":s.preferred_time,"created_at":s.created_at,"updated_at":histories[0].created_at if histories else s.created_at}
@api.get('/services')
def list_services(mine:bool=True,user=Depends(current_user),db:Session=Depends(get_db)):
    if mine: return {"items":[service_out(s,db) for s in db.query(ServiceRequest).filter(ServiceRequest.requested_by==user.id).order_by(ServiceRequest.created_at.desc()).all()]}
    roles={r.name for r in db.query(Role).join(UserRole).filter(UserRole.user_id==user.id)}
    if not roles & {"admin","housekeeping","receptionist"}: raise HTTPException(403,"Insufficient permission")
    return {"items":[service_out(s,db) for s in db.query(ServiceRequest).all()]}
@api.get('/services/{service_id}')
def get_service(service_id:str,user=Depends(current_user),db:Session=Depends(get_db)):
    s=db.get(ServiceRequest,service_id)
    if not s or s.requested_by!=user.id: raise HTTPException(404,"Service request not found")
    return service_out(s,db)
@api.post('/services/{service_id}/cancel')
def cancel_service(service_id:str,user=Depends(current_user),db:Session=Depends(get_db)):
    s=db.get(ServiceRequest,service_id)
    if not s or s.requested_by!=user.id: raise HTTPException(404,"Service request not found")
    if s.status not in {"pending","open"}: raise HTTPException(409,"Only pending requests can be cancelled")
    s.status="cancelled"; db.add(ServiceRequestHistory(service_request_id=s.id,status="cancelled",actor_id=user.id)); db.commit(); return service_out(s,db)
@api.patch('/services/{service_id}')
def update_service(service_id:str,body:ServiceUpdate,user=Depends(require("admin","housekeeping","receptionist")),db:Session=Depends(get_db)):
    s=db.get(ServiceRequest,service_id)
    if not s: raise HTTPException(404,"Service request not found")
    if not can_access_hotel(db,user,s.hotel_id,{"housekeeping","receptionist"}): raise HTTPException(403,"Not assigned to this hotel")
    if body.assigned_to: s.assigned_to=body.assigned_to
    if body.status:
        if body.status not in {"accepted","assigned","in_progress","completed","rejected","cancelled","open","pending"}: raise HTTPException(422,"Invalid request status")
        s.status=body.status; db.add(ServiceRequestHistory(service_request_id=s.id,status=s.status,actor_id=user.id))
    db.commit(); return service_out(s)

@api.get('/restaurant/menu')
def menu(hotel_id:str,category:str|None=None,vegetarian:bool|None=None,db:Session=Depends(get_db)):
    categories=db.query(FoodCategory).filter_by(hotel_id=hotel_id).all()
    if category: categories = [item for item in categories if item.name.lower() == category.lower()]
    def category_out(c):
        query = db.query(FoodItem).filter_by(category_id=c.id)
        if vegetarian is not None: query = query.filter_by(vegetarian=vegetarian)
        return {"id": c.id, "name": c.name, "items": [{"id": x.id, "name": x.name, "description": x.description, "price": str(x.price), "vegetarian": x.vegetarian, "image_url": x.image_url, "available": x.available} for x in query.all()]}
    return {"items": [category_out(c) for c in categories]}
@api.post('/restaurant/orders',status_code=201)
def order_food(body:OrderIn,user=Depends(current_user),db:Session=Depends(get_db)):
    if body.booking_id:
        b=db.get(Booking,body.booking_id)
        if not b or b.user_id!=user.id or b.hotel_id!=body.hotel_id: raise HTTPException(403,"Booking does not belong to this account")
    order=RestaurantOrder(hotel_id=body.hotel_id,booking_id=body.booking_id,status="new",total=0); db.add(order); db.flush(); total=Decimal('0')
    for line in body.items:
        item=db.get(FoodItem,line.food_item_id)
        if not item or not item.available: raise HTTPException(409,"Menu item unavailable")
        amount=Decimal(item.price)*line.quantity; total+=amount; db.add(RestaurantOrderItem(order_id=order.id,item_name=item.name,unit_price=item.price,quantity=line.quantity))
    order.total=total; db.add(Notification(user_id=user.id,type="restaurant",body="Restaurant order received")); db.commit(); return order_out(order)
def order_out(o): return {"id":o.id,"hotel_id":o.hotel_id,"booking_id":o.booking_id,"status":o.status,"total":str(o.total)}
@api.get('/restaurant/orders')
def orders(user=Depends(current_user),db:Session=Depends(get_db)):
    return {"items":[order_out(o) for o in db.query(RestaurantOrder).join(Booking,RestaurantOrder.booking_id==Booking.id).filter(Booking.user_id==user.id).all()]}
@api.patch('/restaurant/orders/{order_id}/{status}')
def update_order(order_id:str,status:str,user=Depends(require("admin","restaurant")),db:Session=Depends(get_db)):
    if status not in {"accepted","preparing","ready","delivered","cancelled"}: raise HTTPException(422,"Invalid order status")
    o=db.get(RestaurantOrder,order_id)
    if not o: raise HTTPException(404,"Order not found")
    if not can_access_hotel(db,user,o.hotel_id,{"restaurant"}): raise HTTPException(403,"Not assigned to this hotel")
    o.status=status; db.commit(); return order_out(o)

@api.post('/reviews',status_code=201)
def review(body:ReviewIn,user=Depends(current_user),db:Session=Depends(get_db)):
    b=db.get(Booking,body.booking_id)
    if not b or b.user_id!=user.id or b.status!="checked_out": raise HTTPException(403,"Only completed stays can be reviewed")
    if db.query(Review).filter_by(booking_id=b.id).first(): raise HTTPException(409,"Review already submitted")
    r=Review(booking_id=b.id,user_id=user.id,rating=body.rating,body=body.body,cleanliness_rating=body.cleanliness_rating,staff_rating=body.staff_rating,comfort_rating=body.comfort_rating,dining_rating=body.dining_rating); db.add(r); db.commit(); return {"id":r.id,"rating":r.rating}
@api.get('/reviews')
def my_reviews(user=Depends(current_user),db:Session=Depends(get_db)):
    result=[]
    for r in db.query(Review).filter_by(user_id=user.id).order_by(Review.created_at.desc()).all():
        b=db.get(Booking,r.booking_id); h=db.get(Hotel,b.hotel_id) if b else None
        result.append({"id":r.id,"booking_id":r.booking_id,"booking_reference":b.reference if b else "","hotel_name":h.name if h else "","rating":r.rating,"cleanliness_rating":r.cleanliness_rating,"staff_rating":r.staff_rating,"comfort_rating":r.comfort_rating,"dining_rating":r.dining_rating,"body":r.body,"created_at":r.created_at})
    return {"items":result}
@api.post('/feedback',status_code=201)
def submit_feedback(body:GuestFeedbackIn,user=Depends(optional_current_user),db:Session=Depends(get_db)):
    name = (user.name if user else body.name).strip()
    email = (user.email if user else str(body.email)).strip().lower()
    message = body.message.strip()
    suggestions = body.suggestions.strip()
    if not name or not message:
        raise HTTPException(422,"Name and feedback message are required")
    if len(message) < 3:
        raise HTTPException(422,"Feedback message must be at least 3 characters")
    item=GuestFeedback(user_id=user.id if user else None,name=name,email=email,category=body.category,rating=body.rating,message=message,suggestions=suggestions)
    db.add(item)
    db.commit()
    return {"id":item.id,"status":"received"}
@api.get('/admin/feedback')
def admin_feedback(user=Depends(require("admin")),db:Session=Depends(get_db)):
    items=db.query(GuestFeedback).order_by(GuestFeedback.created_at.desc()).all()
    return {"items":[{"id":item.id,"name":item.name,"email":item.email,"category":item.category,"rating":item.rating,"message":item.message,"suggestions":item.suggestions,"created_at":item.created_at} for item in items]}
@api.post('/complaints',status_code=201)
def complaint(body:ComplaintIn,user=Depends(current_user),db:Session=Depends(get_db)):
    if not db.get(Hotel,body.hotel_id): raise HTTPException(404,"Hotel not found")
    c=Complaint(user_id=user.id,hotel_id=body.hotel_id,body=body.body); db.add(c); db.commit(); return {"id":c.id,"status":c.status}
@api.get('/complaints')
def complaints(user=Depends(current_user),db:Session=Depends(get_db)):
    return {"items":[{"id":c.id,"hotel_id":c.hotel_id,"body":c.body,"status":c.status} for c in db.query(Complaint).filter_by(user_id=user.id)]}
