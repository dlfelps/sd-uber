import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.models import RideStatus, User, UserRole, Ride, DriverProfile
from app.db.base import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest.fixture
def override_db(db_session):
    async def _override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_driver_accept_ride(db_session: AsyncSession, override_db):
    # Setup: Create rider, driver, and a requested ride
    rider = User(email="rider_accept@test.com", hashed_password="pw")
    driver_user = User(email="driver_accept@test.com", hashed_password="pw", role=UserRole.DRIVER)
    db_session.add_all([rider, driver_user])
    await db_session.commit()
    
    profile = DriverProfile(user_id=driver_user.id, license_plate="FLY-123", car_model="Tesla", is_available=True)
    ride = Ride(rider_id=rider.id, source_lat=37.7749, source_long=-122.4194, dest_lat=37.7849, dest_long=-122.4094, status=RideStatus.REQUESTED)
    db_session.add_all([profile, ride])
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "ride_id": ride.id,
            "driver_id": driver_user.id,
            "accept": True
        }
        response = await ac.patch("/ride/driver/accept", json=payload)
    
    assert response.status_code == 200
    
    # Verify DB state
    await db_session.refresh(ride)
    assert ride.status == RideStatus.MATCHED
    assert ride.driver_id == driver_user.id
    
    await db_session.refresh(profile)
    assert profile.is_available is False

@pytest.mark.asyncio
async def test_driver_deny_ride(db_session: AsyncSession, override_db):
    # Setup: Create rider, driver, and a requested ride
    rider = User(email="rider_deny@test.com", hashed_password="pw")
    driver_user = User(email="driver_deny@test.com", hashed_password="pw", role=UserRole.DRIVER)
    db_session.add_all([rider, driver_user])
    await db_session.commit()
    
    profile = DriverProfile(user_id=driver_user.id, license_plate="FLY-456", car_model="Toyota", is_available=True)
    ride = Ride(rider_id=rider.id, source_lat=37.7749, source_long=-122.4194, dest_lat=37.7849, dest_long=-122.4094, status=RideStatus.REQUESTED)
    db_session.add_all([profile, ride])
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "ride_id": ride.id,
            "driver_id": driver_user.id,
            "accept": False
        }
        response = await ac.patch("/ride/driver/accept", json=payload)
    
    assert response.status_code == 200
    
    # Verify DB state: nothing should change for ride status, driver remains available
    await db_session.refresh(ride)
    assert ride.status == RideStatus.REQUESTED
    
    await db_session.refresh(profile)
    assert profile.is_available is True

@pytest.mark.asyncio
async def test_driver_accept_already_matched(db_session: AsyncSession, override_db):
    # Setup
    rider = User(email="rider_already@test.com", hashed_password="pw")
    driver_user = User(email="driver_already@test.com", hashed_password="pw", role=UserRole.DRIVER)
    db_session.add_all([rider, driver_user])
    await db_session.commit()
    
    profile = DriverProfile(user_id=driver_user.id, license_plate="FLY-789", car_model="Tesla", is_available=True)
    ride = Ride(rider_id=rider.id, source_lat=37.7749, source_long=-122.4194, dest_lat=37.7849, dest_long=-122.4094, status=RideStatus.MATCHED)
    db_session.add_all([profile, ride])
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"ride_id": ride.id, "driver_id": driver_user.id, "accept": True}
        response = await ac.patch("/ride/driver/accept", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Ride is already matched or completed"

@pytest.mark.asyncio
async def test_driver_accept_driver_not_available(db_session: AsyncSession, override_db):
    # Setup
    rider = User(email="rider_notavail@test.com", hashed_password="pw")
    driver_user = User(email="driver_notavail@test.com", hashed_password="pw", role=UserRole.DRIVER)
    db_session.add_all([rider, driver_user])
    await db_session.commit()
    
    profile = DriverProfile(user_id=driver_user.id, license_plate="FLY-000", car_model="Tesla", is_available=False)
    ride = Ride(rider_id=rider.id, source_lat=37.7749, source_long=-122.4194, dest_lat=37.7849, dest_long=-122.4094, status=RideStatus.REQUESTED)
    db_session.add_all([profile, ride])
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"ride_id": ride.id, "driver_id": driver_user.id, "accept": True}
        response = await ac.patch("/ride/driver/accept", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Driver is not available"
