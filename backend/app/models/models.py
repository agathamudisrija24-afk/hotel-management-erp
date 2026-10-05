import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, DateTime, Date, ForeignKey, Numeric, Integer, Boolean, Text, JSON, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)
class Entity(Base):
    __abstract__=True
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
class User(Entity):
    __tablename__="users"
    email: Mapped[str]=mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255)); name: Mapped[str]=mapped_column(String(150)); phone: Mapped[str]=mapped_column(String(30), default="")
    active: Mapped[bool]=mapped_column(Boolean, default=True); verified: Mapped[bool]=mapped_column(Boolean, default=False)
    roles: Mapped[list["UserRole"]]=relationship(back_populates="user", cascade="all, delete-orphan")
class Role(Entity):
    __tablename__="roles"; name: Mapped[str]=mapped_column(String(40), unique=True)
class UserRole(Entity):
    __tablename__="user_roles"; user_id: Mapped[str]=mapped_column(ForeignKey("users.id")); role_id: Mapped[str]=mapped_column(ForeignKey("roles.id")); hotel_id: Mapped[str]=mapped_column(ForeignKey("hotels.id"), nullable=True)
    user: Mapped[User]=relationship(back_populates="roles"); __table_args__=(UniqueConstraint("user_id","role_id","hotel_id"),)
class Hotel(Entity):
    __tablename__="hotels"; name: Mapped[str]=mapped_column(String(200), index=True); city: Mapped[str]=mapped_column(String(120), index=True); address: Mapped[str]=mapped_column(Text); description: Mapped[str]=mapped_column(Text, default=""); timezone: Mapped[str]=mapped_column(String(64), default="UTC"); published: Mapped[bool]=mapped_column(Boolean, default=False); rating: Mapped[Decimal]=mapped_column(Numeric(2,1), default=Decimal("4.5")); hotel_type: Mapped[str]=mapped_column(String(60), default="Hotel")
    room_types: Mapped[list["RoomType"]]=relationship(back_populates="hotel", cascade="all, delete-orphan")
class HotelImage(Entity): __tablename__="hotel_images"; hotel_id: Mapped[str]=mapped_column(ForeignKey("hotels.id")); url: Mapped[str]=mapped_column(Text); alt: Mapped[str]=mapped_column(String(200), default="")
class HotelAmenity(Entity): __tablename__="hotel_amenities"; hotel_id: Mapped[str]=mapped_column(ForeignKey("hotels.id")); name: Mapped[str]=mapped_column(String(100)); description: Mapped[str]=mapped_column(String(240), default="")
class HotelPolicy(Entity): __tablename__="hotel_policies"; hotel_id: Mapped[str]=mapped_column(ForeignKey("hotels.id")); title: Mapped[str]=mapped_column(String(100)); body: Mapped[str]=mapped_column(Text)
class RoomType(Entity):
    __tablename__="room_types"; hotel_id: Mapped[str]=mapped_column(ForeignKey("hotels.id")); name: Mapped[str]=mapped_column(String(120)); description: Mapped[str]=mapped_column(Text,default=""); capacity: Mapped[int]=mapped_column(Integer); base_rate: Mapped[Decimal]=mapped_column(Numeric(12,2)); hotel: Mapped[Hotel]=relationship(back_populates="room_types"); rooms: Mapped[list["Room"]]=relationship(back_populates="room_type")
class Room(Entity):
    __tablename__="rooms"; room_type_id: Mapped[str]=mapped_column(ForeignKey("room_types.id")); number: Mapped[str]=mapped_column(String(30)); status: Mapped[str]=mapped_column(String(30),default="available"); room_type: Mapped[RoomType]=relationship(back_populates="rooms"); __table_args__=(UniqueConstraint("room_type_id","number"),)
class RoomAmenity(Entity): __tablename__="room_amenities"; room_type_id: Mapped[str]=mapped_column(ForeignKey("room_types.id")); name: Mapped[str]=mapped_column(String(100))
class RoomImage(Entity): __tablename__="room_images"; room_type_id: Mapped[str]=mapped_column(ForeignKey("room_types.id")); url: Mapped[str]=mapped_column(Text)
class RoomRatePlan(Entity): __tablename__="room_rate_plans"; room_type_id: Mapped[str]=mapped_column(ForeignKey("room_types.id")); name: Mapped[str]=mapped_column(String(100)); rate: Mapped[Decimal]=mapped_column(Numeric(12,2))
class RoomRateRule(Entity): __tablename__="room_rate_rules"; rate_plan_id: Mapped[str]=mapped_column(ForeignKey("room_rate_plans.id")); start_date: Mapped[datetime]=mapped_column(Date); end_date: Mapped[datetime]=mapped_column(Date); rate: Mapped[Decimal]=mapped_column(Numeric(12,2))
class RoomBlock(Entity): __tablename__="room_blocks"; room_id: Mapped[str]=mapped_column(ForeignKey("rooms.id")); start_date: Mapped[datetime]=mapped_column(Date); end_date: Mapped[datetime]=mapped_column(Date); reason: Mapped[str]=mapped_column(String(200))
class Booking(Entity):
    __tablename__="bookings"; reference: Mapped[str]=mapped_column(String(30),unique=True,index=True); user_id: Mapped[str]=mapped_column(ForeignKey("users.id")); hotel_id: Mapped[str]=mapped_column(ForeignKey("hotels.id")); check_in: Mapped[datetime]=mapped_column(Date); check_out: Mapped[datetime]=mapped_column(Date); guests: Mapped[int]=mapped_column(Integer, default=1); status: Mapped[str]=mapped_column(String(30),default="pending_payment"); total: Mapped[Decimal]=mapped_column(Numeric(12,2)); hold_expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=True); idempotency_key: Mapped[str]=mapped_column(String(100),unique=True,nullable=True); user: Mapped[User]=relationship(); rooms: Mapped[list["BookingRoom"]]=relationship(cascade="all,delete-orphan")
class BookingRoom(Entity): __tablename__="booking_rooms"; booking_id: Mapped[str]=mapped_column(ForeignKey("bookings.id")); room_id: Mapped[str]=mapped_column(ForeignKey("rooms.id")); nightly_rate: Mapped[Decimal]=mapped_column(Numeric(12,2)); __table_args__=(Index("booking_room_dates_lookup","room_id","booking_id"),)
class BookingGuest(Entity): __tablename__="booking_guests"; booking_id: Mapped[str]=mapped_column(ForeignKey("bookings.id")); name: Mapped[str]=mapped_column(String(150)); email: Mapped[str]=mapped_column(String(320))
class BookingPriceItem(Entity): __tablename__="booking_price_items"; booking_id: Mapped[str]=mapped_column(ForeignKey("bookings.id")); label: Mapped[str]=mapped_column(String(100)); amount: Mapped[Decimal]=mapped_column(Numeric(12,2))
class BookingStatusHistory(Entity): __tablename__="booking_status_history"; booking_id: Mapped[str]=mapped_column(ForeignKey("bookings.id")); status: Mapped[str]=mapped_column(String(30)); actor_id: Mapped[str]=mapped_column(ForeignKey("users.id"),nullable=True)
class Payment(Entity): __tablename__="payments"; booking_id: Mapped[str]=mapped_column(ForeignKey("bookings.id")); provider: Mapped[str]=mapped_column(String(30)); provider_payment_id: Mapped[str]=mapped_column(String(100),unique=True); amount: Mapped[Decimal]=mapped_column(Numeric(12,2)); status: Mapped[str]=mapped_column(String(30),default="created"); idempotency_key: Mapped[str]=mapped_column(String(100),unique=True)
class Refund(Entity): __tablename__="refunds"; payment_id: Mapped[str]=mapped_column(ForeignKey("payments.id")); amount: Mapped[Decimal]=mapped_column(Numeric(12,2)); status: Mapped[str]=mapped_column(String(30),default="requested"); provider_refund_id: Mapped[str]=mapped_column(String(100))
class Invoice(Entity): __tablename__="invoices"; booking_id: Mapped[str]=mapped_column(ForeignKey("bookings.id")); number: Mapped[str]=mapped_column(String(50),unique=True); amount: Mapped[Decimal]=mapped_column(Numeric(12,2)); url: Mapped[str]=mapped_column(Text,default="")
class Stay(Entity): __tablename__="stays"; booking_id: Mapped[str]=mapped_column(ForeignKey("bookings.id"),unique=True); checked_in_at: Mapped[datetime]=mapped_column(DateTime(timezone=True)); checked_out_at: Mapped[datetime]=mapped_column(DateTime(timezone=True))
class ServiceRequest(Entity): __tablename__="service_requests"; hotel_id: Mapped[str]=mapped_column(ForeignKey("hotels.id")); booking_id: Mapped[str]=mapped_column(ForeignKey("bookings.id"),nullable=True); requested_by: Mapped[str]=mapped_column(ForeignKey("users.id")); type: Mapped[str]=mapped_column(String(30)); priority: Mapped[str]=mapped_column(String(20),default="normal"); status: Mapped[str]=mapped_column(String(30),default="open"); assigned_to: Mapped[str]=mapped_column(ForeignKey("users.id"),nullable=True); description: Mapped[str]=mapped_column(Text); room_number: Mapped[str]=mapped_column(String(30),default=""); preferred_time: Mapped[str]=mapped_column(String(80),default=""); category: Mapped[str]=mapped_column(String(100),default="")
class ServiceRequestHistory(Entity): __tablename__="service_request_history"; service_request_id: Mapped[str]=mapped_column(ForeignKey("service_requests.id")); status: Mapped[str]=mapped_column(String(30)); actor_id: Mapped[str]=mapped_column(ForeignKey("users.id"),nullable=True)
class FoodCategory(Entity): __tablename__="food_categories"; hotel_id: Mapped[str]=mapped_column(ForeignKey("hotels.id")); name: Mapped[str]=mapped_column(String(100))
class FoodItem(Entity): __tablename__="food_items"; category_id: Mapped[str]=mapped_column(ForeignKey("food_categories.id")); name: Mapped[str]=mapped_column(String(100)); description: Mapped[str]=mapped_column(Text, default=""); price: Mapped[Decimal]=mapped_column(Numeric(12,2)); vegetarian: Mapped[bool]=mapped_column(Boolean, default=True); image_url: Mapped[str]=mapped_column(Text, default=""); available: Mapped[bool]=mapped_column(Boolean,default=True)
class RestaurantOrder(Entity): __tablename__="restaurant_orders"; hotel_id: Mapped[str]=mapped_column(ForeignKey("hotels.id")); booking_id: Mapped[str]=mapped_column(ForeignKey("bookings.id"),nullable=True); status: Mapped[str]=mapped_column(String(30),default="new"); total: Mapped[Decimal]=mapped_column(Numeric(12,2),default=0)
class RestaurantOrderItem(Entity): __tablename__="restaurant_order_items"; order_id: Mapped[str]=mapped_column(ForeignKey("restaurant_orders.id")); item_name: Mapped[str]=mapped_column(String(100)); unit_price: Mapped[Decimal]=mapped_column(Numeric(12,2)); quantity: Mapped[int]=mapped_column(Integer)
class Notification(Entity): __tablename__="notifications"; user_id: Mapped[str]=mapped_column(ForeignKey("users.id")); type: Mapped[str]=mapped_column(String(40)); body: Mapped[str]=mapped_column(Text); read: Mapped[bool]=mapped_column(Boolean,default=False)
class Review(Entity): __tablename__="reviews"; booking_id: Mapped[str]=mapped_column(ForeignKey("bookings.id"),unique=True); user_id: Mapped[str]=mapped_column(ForeignKey("users.id")); rating: Mapped[int]=mapped_column(Integer); body: Mapped[str]=mapped_column(Text); cleanliness_rating: Mapped[int]=mapped_column(Integer,default=5); staff_rating: Mapped[int]=mapped_column(Integer,default=5); comfort_rating: Mapped[int]=mapped_column(Integer,default=5); dining_rating: Mapped[int]=mapped_column(Integer,nullable=True)
class GuestFeedback(Entity):
    __tablename__ = "guest_feedback"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(320))
    category: Mapped[str] = mapped_column(String(40))
    rating: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text)
    suggestions: Mapped[str] = mapped_column(Text, default="")
class Complaint(Entity): __tablename__="complaints"; user_id: Mapped[str]=mapped_column(ForeignKey("users.id")); hotel_id: Mapped[str]=mapped_column(ForeignKey("hotels.id")); body: Mapped[str]=mapped_column(Text); status: Mapped[str]=mapped_column(String(30),default="open")
class Coupon(Entity): __tablename__="coupons"; code: Mapped[str]=mapped_column(String(40),unique=True); percent: Mapped[int]=mapped_column(Integer); active: Mapped[bool]=mapped_column(Boolean,default=True)
class AuditLog(Entity): __tablename__="audit_logs"; actor_id: Mapped[str]=mapped_column(ForeignKey("users.id"),nullable=True); action: Mapped[str]=mapped_column(String(100)); resource: Mapped[str]=mapped_column(String(100)); details: Mapped[dict]=mapped_column(JSON,default=dict)
class RefreshToken(Entity): __tablename__="refresh_tokens"; user_id: Mapped[str]=mapped_column(ForeignKey("users.id")); token_hash: Mapped[str]=mapped_column(String(255)); expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True)); revoked: Mapped[bool]=mapped_column(Boolean,default=False)
class PasswordResetToken(Entity): __tablename__="password_reset_tokens"; user_id: Mapped[str]=mapped_column(ForeignKey("users.id")); token_hash: Mapped[str]=mapped_column(String(255)); expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True)); used: Mapped[bool]=mapped_column(Boolean,default=False)
