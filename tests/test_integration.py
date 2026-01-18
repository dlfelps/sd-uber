import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.models import RideStatus, User, UserRole, Ride, DriverProfile
from app.db.base import get_db
from app.services.location_service import LocationService
from app.services.matching_service import MatchingService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis
from fakeredis import FakeAsyncRedis

@pytest.fixture
async def redis_client():
    client = FakeAsyncRedis()
    yield client
    await client.aclose()

@pytest.fixture
def override_db(db_session):
    async def _override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_end_to_end_matching(db_session: AsyncSession, redis_client, override_db):
    transport = ASGITransport(app=app)
    
    # 1. Setup: Create Rider and Driver
    rider = User(email="rider_e2e@test.com", hashed_password="pw", role=UserRole.RIDER)
    driver_user = User(email="driver_e2e@test.com", hashed_password="pw", role=UserRole.DRIVER)
    db_session.add_all([rider, driver_user])
    await db_session.commit()
    
    profile = DriverProfile(user_id=driver_user.id, license_plate="E2E-123", car_model="Tesla", is_available=True)
    db_session.add(profile)
    await db_session.commit()
    
    # 2. Driver updates location
    loc_service = LocationService(redis_client)
    await loc_service.update_location(driver_user.id, 37.7749, -122.4194)
    
    # 3. Rider requests a ride via API
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "rider_id": rider.id,
            "source_lat": 37.7749,
            "source_long": -122.4194,
            "dest_lat": 37.7849,
            "dest_long": -122.4094
        }
        response = await ac.post("/ride/request", json=payload)
    
    assert response.status_code == 201
    ride_id = response.json()["id"]
    
    # 4. Matching Service runs (triggered manually for integration test)
    matching_service = MatchingService(db_session, loc_service, redis_client)
    matched_driver_id = await matching_service.match_ride(ride_id)
    
    assert matched_driver_id == driver_user.id
    
    # 5. Verify Ride Status is MATCHED
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/ride/{ride_id}")
    assert response.json()["status"] == "matched"
    assert response.json()["driver_id"] == driver_user.id
    
    # 6. Driver Accept via API (Confirming the match)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "ride_id": ride_id,
            "driver_id": driver_user.id,
            "accept": True
        }
        response = await ac.patch("/ride/driver/accept", json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    
    # Final check: Driver is no longer available
    await db_session.refresh(profile)
    assert profile.is_available is False
