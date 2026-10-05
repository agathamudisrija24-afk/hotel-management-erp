import os
import pytest
from uuid import uuid4
os.environ["DATABASE_URL"]="sqlite:///./test_hotel.db"
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import Base, engine
@pytest.fixture()
def client():
    # The SQLite test database is intentionally isolated from Compose/Postgres.
    # Reset it so a prior test run's bookings cannot exhaust seeded inventory.
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
def login(client,email="customer@hotel.example", password="DemoPass123!"):
    return client.post('/api/v1/auth/login',json={"email":email,"password":password}).json()['access_token']
def test_search_and_booking_flow(client):
    hotels=client.get('/api/v1/hotels').json()['items']; assert len(hotels)==5
    assert {hotel['name'] for hotel in hotels} == {"Harbor Grand Resort", "Royal Orchid Palace", "Mountain View Retreat", "Ocean Pearl Suites", "Green Valley Resort"}
    assert all(hotel['images'] and hotel['services'] for hotel in hotels)
    assert client.get('/api/v1/hotels?q=Goa').json()['total']==1
    assert client.get('/api/v1/hotels?service=Spa&sort=rating_desc').json()['total']>=2
    detail=client.get('/api/v1/hotels/'+hotels[0]['id']).json(); assert len(detail['images'])>=3 and detail['services']
    room=hotels[0]['room_types'][0]
    headers={'Authorization':'Bearer '+login(client),'Idempotency-Key':'test-flow-'+str(uuid4())}
    b=client.post('/api/v1/bookings',headers=headers,json={'hotel_id':hotels[0]['id'],'room_type_id':room['id'],'check_in':'2030-01-10','check_out':'2030-01-12','guests':1}); assert b.status_code==201
    booking=b.json(); assert booking['status']=='pending_payment'
    p=client.post('/api/v1/payments/initiate?booking_id='+booking['id'],headers={**headers,'Idempotency-Key':'payment-'+str(uuid4())}); assert p.status_code==200
    done=client.post('/api/v1/payments/'+p.json()['payment_id']+'/verify',headers=headers); assert done.json()['booking']['status']=='confirmed'
def test_permissions_require_authentication(client):
    assert client.get('/api/v1/bookings').status_code==401
    assert client.get('/api/v1/admin/reports/summary',headers={'Authorization':'Bearer '+login(client)}).status_code==403

def test_guest_feedback_is_validated_saved_and_admin_only(client):
    payload={"name":"  Guest Name ","email":"guest@example.com","category":"website_experience","rating":4,"message":"  The site was easy to use.  ","suggestions":"  Add more photos.  "}
    assert client.post('/api/v1/feedback',json={**payload,"message":" "}).status_code==422
    assert client.post('/api/v1/feedback',json={**payload,"email":"not-an-email"}).status_code==422
    assert client.post('/api/v1/feedback',json={**payload,"rating":6}).status_code==422
    assert client.post('/api/v1/feedback',json={**payload,"category":"made_up"}).status_code==422
    assert client.get('/api/v1/admin/feedback').status_code==401
    result=client.post('/api/v1/feedback',json=payload)
    assert result.status_code==201 and result.json()['status']=='received'
    customer_headers={'Authorization':'Bearer '+login(client)}
    assert client.get('/api/v1/admin/feedback',headers=customer_headers).status_code==403
    admin_headers={'Authorization':'Bearer '+login(client,'admin@hotel.example')}
    items=client.get('/api/v1/admin/feedback',headers=admin_headers)
    assert items.status_code==200
    saved=items.json()['items'][0]
    assert saved['email']=='guest@example.com' and saved['name']=='Guest Name'
    assert saved['message']=='The site was easy to use.' and saved['suggestions']=='Add more photos.'

def test_authenticated_feedback_is_associated_with_account(client):
    headers={'Authorization':'Bearer '+login(client)}
    response=client.post('/api/v1/feedback',headers=headers,json={"name":"Different Name","email":"other@example.com","category":"payment","rating":5,"message":"Payment was straightforward."})
    assert response.status_code==201
    admin_headers={'Authorization':'Bearer '+login(client,'admin@hotel.example')}
    saved=client.get('/api/v1/admin/feedback',headers=admin_headers).json()['items'][0]
    assert saved['name']=='Demo Customer'
    assert saved['email']=='customer@hotel.example'

def test_customer_can_view_and_update_own_profile(client):
    headers = {'Authorization': 'Bearer ' + login(client)}
    profile = client.get('/api/v1/auth/me', headers=headers)
    assert profile.status_code == 200
    assert profile.json()['email'] == 'customer@hotel.example'
    updated = client.patch('/api/v1/auth/me', headers=headers, json={'name': 'Updated Customer', 'phone': '+91 90000 00000'})
    assert updated.status_code == 200
    assert updated.json()['name'] == 'Updated Customer'
    assert updated.json()['phone'] == '+91 90000 00000'

def test_services_menu_and_notifications_are_persisted(client):
    headers={'Authorization':'Bearer '+login(client)}
    hotel=client.get('/api/v1/hotels').json()['items'][0]
    created=client.post('/api/v1/services',headers=headers,json={'hotel_id':hotel['id'],'type':'housekeeping','priority':'high','description':'Please replenish towels'})
    assert created.status_code==201
    assert client.get('/api/v1/services',headers=headers).json()['items'][0]['status']=='open'
    assert client.get('/api/v1/notifications',headers=headers).json()['items']
    menu=client.get('/api/v1/restaurant/menu?hotel_id='+hotel['id']).json()['items']
    assert menu and menu[0]['items'][0]['available'] is True
    assert all(item['image_url'] for category in menu for item in category['items'])
    vegetarian_menu=client.get('/api/v1/restaurant/menu?hotel_id='+hotel['id']+'&vegetarian=true').json()['items']
    assert all(item['vegetarian'] for category in vegetarian_menu for item in category['items'])

    # Every public hotel owns a populated, image-backed menu.
    for public_hotel in client.get('/api/v1/hotels').json()['items']:
        hotel_menu = client.get('/api/v1/restaurant/menu?hotel_id=' + public_hotel['id']).json()['items']
        assert hotel_menu
        assert all(item['image_url'] and item['available'] for group in hotel_menu for item in group['items'])
