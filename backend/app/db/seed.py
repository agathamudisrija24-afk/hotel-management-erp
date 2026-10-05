"""Development data for the public hotel catalogue.

The functions are deliberately idempotent: names are used as stable natural keys
so application restarts do not duplicate hotels, rooms, services, or menu items.
"""
from hashlib import sha256

from app.core.security import hash_password
from app.models.models import FoodCategory, FoodItem, Hotel, HotelAmenity, HotelImage, Role, Room, RoomType, User, UserRole


HOTELS = [
    {
        "name": "Harbor Grand Resort", "city": "Candolim, Goa", "address": "Candolim Beach Road, North Goa, Goa",
        "description": "A polished beachfront retreat with sunset views, calm gardens and thoughtful Goan hospitality.", "rating": 4.8, "hotel_type": "Beach Resort",
        "images": ["https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1600&q=85", "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=85", "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1200&q=85"],
        "services": [("Free Wi-Fi", "Fast, complimentary internet throughout the resort."), ("Swimming pool", "An ocean-facing pool with lounge seating."), ("Spa and wellness", "Restorative treatments inspired by coastal traditions."), ("Beach access", "Direct access to Candolim's golden shoreline."), ("Fine dining", "Goan seafood and international favourites."), ("Airport transfers", "Pre-booked transfers from Goa International Airport.")],
        "rooms": [("Standard Garden", "A peaceful garden-facing room with queen bed.", 2, 6500, 5), ("Deluxe Ocean", "Private balcony and generous views of the Arabian Sea.", 2, 8200, 4), ("Seaside Suite", "Separate lounge, deep soaking tub and beach panorama.", 4, 12500, 3)],
        "menu": [("Breakfast", "Masala Dosa", "Crisp dosa with sambar and coconut chutney.", 180, True), ("Starters", "Paneer Tikka", "Char-grilled cottage cheese with mint chutney.", 320, True), ("Main course", "Chicken Biryani", "Fragrant basmati rice with tender chicken.", 450, False), ("Main course", "Fish Curry", "Local catch in a tangy Goan curry.", 420, False), ("Main course", "Veg Fried Rice", "Wok-tossed vegetables and jasmine rice.", 280, True), ("Main course", "Butter Naan", "Fresh tandoor-baked flatbread.", 70, True), ("Desserts", "Gulab Jamun", "Warm cardamom syrup dumplings.", 120, True), ("Beverages", "Fresh Lime Soda", "Sweet or salted, served chilled.", 100, True)],
    },
    {
        "name": "Royal Orchid Palace", "city": "Jaipur, Rajasthan", "address": "Amer Road, Jaipur, Rajasthan", "description": "A regal stay shaped by Jaipur's craft, cuisine and enduring palace architecture.", "rating": 4.7, "hotel_type": "Heritage Hotel",
        "images": ["https://images.unsplash.com/photo-1564501049412-61c2a3083791?auto=format&fit=crop&w=1600&q=85", "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&q=85", "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=85"],
        "services": [("Free Wi-Fi", "Complimentary connectivity across the palace."), ("Rooftop dining", "Evening dining with Aravalli skyline views."), ("Spa and wellness", "Ayurvedic rituals and relaxing therapies."), ("Banquet hall", "Elegant venues for celebrations and meetings."), ("24-hour front desk", "Round-the-clock guest assistance."), ("Free parking", "Secure on-site parking for guests.")],
        "rooms": [("Heritage Standard", "Handcrafted details with a courtyard view.", 2, 5500, 5), ("Orchid Deluxe", "A spacious room with traditional textiles.", 3, 7200, 4), ("Maharaja Suite", "Grand living area, carved furnishings and palace views.", 4, 11000, 2)],
        "menu": [("Breakfast", "Pyaz Kachori", "Flaky Jaipur pastry with spiced onion filling.", 160, True), ("Starters", "Rajasthani Paneer Tikka", "Smoky cottage cheese with desert spices.", 340, True), ("Main course", "Laal Maas", "Slow-cooked mutton in a rich chilli gravy.", 560, False), ("Main course", "Dal Baati Churma", "Traditional lentils, baked wheat dumplings and sweet crumble.", 380, True), ("Main course", "Gatte Ki Sabzi", "Gram flour dumplings in yoghurt gravy.", 300, True), ("Main course", "Missi Roti", "Spiced gram flour flatbread.", 80, True), ("Desserts", "Ghewar", "Honeycomb sweet with saffron rabri.", 180, True), ("Beverages", "Kesar Lassi", "Thick yoghurt drink with saffron.", 140, True)],
    },
    {
        "name": "Mountain View Retreat", "city": "Manali, Himachal Pradesh", "address": "Log Hut Area, Manali, Himachal Pradesh", "description": "A warm mountain base for crisp air, Himalayan views and unhurried alpine adventures.", "rating": 4.6, "hotel_type": "Mountain Resort",
        "images": ["https://images.unsplash.com/photo-1544986581-efac024faf62?auto=format&fit=crop&w=1600&q=85", "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1200&q=85", "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1200&q=85"],
        "services": [("Free Wi-Fi", "Reliable connection for planning mountain days."), ("Mountain-view rooms", "Wake up to views of pine-clad valleys."), ("Bonfire evenings", "Seasonal fires with hot beverages."), ("Trekking assistance", "Local route planning and guide arrangements."), ("Restaurant and dining", "Hearty Himalayan and North Indian cooking."), ("Housekeeping", "Daily room refresh and attentive service.")],
        "rooms": [("Pine Standard", "Cosy room with forest views and a reading nook.", 2, 4000, 6), ("Valley Deluxe", "Private balcony facing the valley.", 3, 5600, 4), ("Himalayan Suite", "Fireplace lounge and panoramic mountain views.", 4, 8600, 2)],
        "menu": [("Breakfast", "Aloo Paratha", "Stuffed flatbread with curd and pickle.", 190, True), ("Starters", "Trout Amritsari", "Crisp local trout with ajwain and lemon.", 480, False), ("Main course", "Himachali Dham", "A traditional regional thali of lentils and rice.", 360, True), ("Main course", "Chana Madra", "Chickpeas in a creamy yoghurt gravy.", 300, True), ("Main course", "Chicken Curry", "Home-style mountain chicken curry.", 440, False), ("Main course", "Tandoori Roti", "Whole-wheat bread from the tandoor.", 60, True), ("Desserts", "Mittha", "Sweet saffron rice with dry fruits.", 160, True), ("Beverages", "Ginger Honey Tea", "Warming tea with local honey.", 120, True)],
    },
    {
        "name": "Ocean Pearl Suites", "city": "Mumbai, Maharashtra", "address": "Marine Drive, Mumbai, Maharashtra", "description": "A refined city stay for business and leisure, moments from Mumbai's waterfront energy.", "rating": 4.8, "hotel_type": "City Hotel",
        "images": ["https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=1600&q=85", "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?auto=format&fit=crop&w=1200&q=85", "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1200&q=85"],
        "services": [("Business lounge", "Quiet workspaces, refreshments and meeting support."), ("Gym", "Modern cardio and strength equipment."), ("Swimming pool", "A relaxed rooftop pool for city escapes."), ("Multi-cuisine restaurant", "Indian, Asian and continental favourites."), ("Laundry service", "Same-day laundry and pressing."), ("24-hour front desk", "Always-available concierge and check-in support.")],
        "rooms": [("Urban Standard", "Comfortable city room with a work desk.", 2, 7000, 6), ("Pearl Deluxe", "Extra space, premium bedding and skyline views.", 3, 9000, 4), ("Executive Suite", "Lounge access and a separate living room.", 4, 14000, 3)],
        "menu": [("Breakfast", "Mumbai Masala Omelette", "Spiced eggs with pav and tomato relish.", 220, False), ("Starters", "Bombay Prawn Koliwada", "Crisp coastal prawns with chilli garlic dip.", 520, False), ("Main course", "Butter Chicken", "Tandoor chicken in a silky tomato gravy.", 500, False), ("Main course", "Veg Kolhapuri", "Seasonal vegetables in a bold coconut masala.", 360, True), ("Main course", "Schezwan Noodles", "Wok-tossed noodles with vegetables.", 320, True), ("Main course", "Garlic Naan", "Tandoor bread with roasted garlic.", 90, True), ("Desserts", "Chocolate Hazelnut Mousse", "Dark chocolate mousse with toasted hazelnuts.", 240, True), ("Beverages", "Cold Coffee", "Blended coffee with vanilla ice cream.", 180, True)],
    },
    {
        "name": "Green Valley Resort", "city": "Munnar, Kerala", "address": "Chithirapuram, Munnar, Kerala", "description": "A restorative tea-country hideaway surrounded by emerald slopes, fresh air and Kerala flavours.", "rating": 4.7, "hotel_type": "Nature Resort",
        "images": ["https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1600&q=85", "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=85", "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=85"],
        "services": [("Tea garden views", "Sweeping views from rooms and shared terraces."), ("Nature walks", "Guided walks through tea estates and forests."), ("Ayurvedic spa", "Traditional wellness therapies and massages."), ("Kerala restaurant", "Seasonal regional cooking with local ingredients."), ("Free parking", "Convenient private parking on the property."), ("Airport transfers", "Scheduled transport from Cochin International Airport.")],
        "rooms": [("Tea Garden Standard", "Bright room overlooking the estate.", 2, 4500, 6), ("Valley Deluxe", "A generous room with a private scenic balcony.", 3, 6200, 4), ("Plantation Suite", "Spacious suite with a lounge and tea garden panorama.", 4, 9800, 2)],
        "menu": [("Breakfast", "Puttu and Kadala Curry", "Steamed rice cakes with black chickpea curry.", 180, True), ("Starters", "Banana Leaf Fish Fry", "Spiced local fish wrapped and pan-fried.", 420, False), ("Main course", "Kerala Sadya", "Seasonal vegetarian feast served on banana leaf.", 390, True), ("Main course", "Appam and Stew", "Lacy rice pancakes with vegetable coconut stew.", 300, True), ("Main course", "Malabar Chicken Curry", "Coastal chicken curry with roasted coconut.", 460, False), ("Main course", "Kerala Parotta", "Layered flaky flatbread.", 70, True), ("Desserts", "Palada Payasam", "Creamy rice and milk pudding.", 150, True), ("Beverages", "Cardamom Tea", "Freshly brewed local tea with cardamom.", 110, True)],
    },
]

def food_image(name):
    """Return a stable, dish-specific photographic source.

    The previous code selected from one generic image list using a hash. That
    made a dish such as Gulab Jamun inherit an arbitrary photo. The dish terms
    are now part of the URL and its stable lock value, so every stored menu
    item has its own semantically targeted image reference on re-seeding.
    """
    keywords = name.lower().replace(" and ", ",").replace(" ", ",")
    lock = int(sha256(name.encode()).hexdigest(), 16) % 100_000
    return f"https://loremflickr.com/900/600/{keywords},indian,food?lock={lock}"


def seed_database(db):
    roles = {}
    for name in ["customer", "admin", "receptionist", "housekeeping", "restaurant"]:
        role = db.query(Role).filter_by(name=name).first()
        if not role:
            role = Role(name=name)
            db.add(role)
            db.flush()
        roles[name] = role

    hotel_by_name = {}
    for data in HOTELS:
        hotel = db.query(Hotel).filter_by(name=data["name"]).first()
        if not hotel:
            hotel = Hotel(name=data["name"], city=data["city"], address=data["address"], description=data["description"], rating=data["rating"], hotel_type=data["hotel_type"], published=True)
            db.add(hotel)
            db.flush()
        else:
            hotel.city, hotel.address, hotel.description = data["city"], data["address"], data["description"]
            hotel.rating, hotel.hotel_type, hotel.published = data["rating"], data["hotel_type"], True
        hotel_by_name[data["name"]] = hotel

        for url, label in zip(data["images"], ["exterior", "guest experience", "scenic view"]):
            if not db.query(HotelImage).filter_by(hotel_id=hotel.id, url=url).first():
                db.add(HotelImage(hotel_id=hotel.id, url=url, alt=f"{hotel.name} {label}"))
        for name, description in data["services"]:
            amenity = db.query(HotelAmenity).filter_by(hotel_id=hotel.id, name=name).first()
            if not amenity:
                db.add(HotelAmenity(hotel_id=hotel.id, name=name, description=description))
            else:
                amenity.description = description
        if not db.query(RoomType).filter_by(hotel_id=hotel.id).first():
            for room_name, description, capacity, rate, count in data["rooms"]:
                room_type = RoomType(hotel_id=hotel.id, name=room_name, description=description, capacity=capacity, base_rate=rate)
                db.add(room_type)
                db.flush()
                db.add_all([Room(room_type_id=room_type.id, number=f"{room_name[:2].upper()}-{number:02d}") for number in range(1, count + 1)])
        categories = {}
        for category_name, item_name, description, price, vegetarian in data["menu"]:
            category = categories.get(category_name)
            if not category:
                category = db.query(FoodCategory).filter_by(hotel_id=hotel.id, name=category_name).first()
                if not category:
                    category = FoodCategory(hotel_id=hotel.id, name=category_name)
                    db.add(category)
                    db.flush()
                categories[category_name] = category
            item = db.query(FoodItem).filter_by(category_id=category.id, name=item_name).first()
            if not item:
                item = FoodItem(category_id=category.id, name=item_name)
                db.add(item)
            item.description, item.price, item.vegetarian, item.image_url, item.available = description, price, vegetarian, food_image(item_name), True

    # Early development builds shipped a placeholder called "Harbor Grand".
    # Keep the row (and therefore any booking that references it) intact, but
    # do not expose it alongside the complete Harbor Grand Resort catalogue.
    # This is deliberately a narrow reconciliation instead of a delete: it is
    # safe to run against an existing production-like database and remains
    # idempotent on every application start.
    legacy_harbor = db.query(Hotel).filter_by(name="Harbor Grand").all()
    for hotel in legacy_harbor:
        hotel.published = False

    for email, name, role_name in [("admin@hotel.example", "Demo Admin", "admin"), ("customer@hotel.example", "Demo Customer", "customer"), ("reception@hotel.example", "Demo Reception", "receptionist"), ("housekeeping@hotel.example", "Demo Housekeeping", "housekeeping")]:
        user = db.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email, name=name, password_hash=hash_password("DemoPass123!"), verified=True)
            db.add(user)
            db.flush()
        if not db.query(UserRole).filter_by(user_id=user.id, role_id=roles[role_name].id).first():
            hotel_id = None if role_name == "customer" else hotel_by_name["Harbor Grand Resort"].id
            db.add(UserRole(user_id=user.id, role_id=roles[role_name].id, hotel_id=hotel_id))
