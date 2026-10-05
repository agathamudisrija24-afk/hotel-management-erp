from datetime import datetime, timezone, timedelta
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.models import Room, RoomType, RoomBlock, Booking, BookingRoom, BookingStatusHistory, BookingPriceItem
ACTIVE={"held","pending_payment","confirmed","checked_in"}
def validate_dates(check_in,check_out):
    if check_in >= check_out or check_in < datetime.now(timezone.utc).date(): raise HTTPException(422,"Choose future check-in and later check-out dates")
def available_rooms(db: Session, room_type_id: str, check_in, check_out):
    validate_dates(check_in,check_out)
    rooms=db.scalars(select(Room).where(Room.room_type_id==room_type_id,Room.status=="available").with_for_update()).all()
    result=[]
    for room in rooms:
        blocked=db.query(RoomBlock).filter(RoomBlock.room_id==room.id,RoomBlock.start_date<check_out,RoomBlock.end_date>check_in).first()
        taken=db.query(BookingRoom).join(Booking).filter(BookingRoom.room_id==room.id,Booking.check_in<check_out,Booking.check_out>check_in,Booking.status.in_(ACTIVE), (Booking.hold_expires_at.is_(None)) | (Booking.hold_expires_at>datetime.now(timezone.utc))).first()
        if not blocked and not taken: result.append(room)
    return result
def create_booking(db,user,hotel_id,room_type_id,check_in,check_out,guests,key):
    existing=db.query(Booking).filter_by(idempotency_key=key).first() if key else None
    if existing: return existing
    validate_dates(check_in,check_out); rt=db.get(RoomType,room_type_id)
    if not rt or rt.hotel_id!=hotel_id: raise HTTPException(404,"Room type not found")
    if guests > rt.capacity: raise HTTPException(422, f"{rt.name} accommodates up to {rt.capacity} guests")
    rooms=available_rooms(db,room_type_id,check_in,check_out)
    if not rooms: raise HTTPException(409,"No room is available for those dates")
    nights=(check_out-check_in).days; rate=Decimal(rt.base_rate); total=rate*nights
    import secrets
    booking=Booking(reference="HM-"+secrets.token_hex(4).upper(),user_id=user.id,hotel_id=hotel_id,check_in=check_in,check_out=check_out,guests=guests,status="pending_payment",total=total,hold_expires_at=datetime.now(timezone.utc)+timedelta(minutes=15),idempotency_key=key)
    db.add(booking); db.flush(); db.add(BookingRoom(booking_id=booking.id,room_id=rooms[0].id,nightly_rate=rate)); db.add(BookingPriceItem(booking_id=booking.id,label=f"{nights} night(s)",amount=total)); db.add(BookingStatusHistory(booking_id=booking.id,status="pending_payment",actor_id=user.id)); return booking
