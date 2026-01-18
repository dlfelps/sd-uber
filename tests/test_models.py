import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.models import User, DriverProfile, Ride, UserRole, RideStatus

@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(email="test@example.com", hashed_password="hashed_pw", full_name="Test User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.RIDER

@pytest.mark.asyncio
async def test_create_driver_profile(db_session):
    user = User(email="driver@example.com", hashed_password="pw", role=UserRole.DRIVER)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    profile = DriverProfile(user_id=user.id, license_plate="ABC-123", car_model="Toyota Prius")
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)
    
    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.is_available is False

@pytest.mark.asyncio
async def test_create_ride(db_session):
    rider = User(email="rider@example.com", hashed_password="pw")
    db_session.add(rider)
    await db_session.commit()
    
    ride = Ride(
        rider_id=rider.id,
        source_lat=37.7749,
        source_long=-122.4194,
        dest_lat=37.7849,
        dest_long=-122.4094,
        estimated_fare=15.50
    )
    db_session.add(ride)
    await db_session.commit()
    await db_session.refresh(ride)
    
    assert ride.id is not None
    assert ride.status == RideStatus.REQUESTED
    assert ride.rider_id == rider.id
