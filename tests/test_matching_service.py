import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from app.services.matching_service import MatchingService
from app.models.models import Ride, User, DriverProfile, RideStatus, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest.fixture
def mock_location_service():
    service = MagicMock()
    service.find_nearby_drivers = AsyncMock(return_value=[10, 11, 12])
    return service

@pytest.fixture
def mock_redis():
    client = AsyncMock()
    # Mock lock acquisition
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_match_ride_success(db_session: AsyncSession, mock_location_service, mock_redis):
    # Setup: Create a rider, a ride, and an available driver
    rider = User(email="rider@matching.com", hashed_password="pw")
    db_session.add(rider)
    await db_session.commit()
    
    ride = Ride(rider_id=rider.id, source_lat=37.7749, source_long=-122.4194, dest_lat=37.7849, dest_long=-122.4094)
    db_session.add(ride)
    await db_session.commit()
    
    # Driver 10 is available
    driver = User(id=10, email="driver10@matching.com", hashed_password="pw", role=UserRole.DRIVER)
    db_session.add(driver)
    profile = DriverProfile(user_id=10, license_plate="FLY-101", car_model="Tesla", is_available=True)
    db_session.add(profile)
    await db_session.commit()
    
    matching_service = MatchingService(db_session, mock_location_service, mock_redis)
    
    # Run matching
    matched_driver_id = await matching_service.match_ride(ride.id)
    
    assert matched_driver_id == 10
    
    # Verify ride status in DB
    await db_session.refresh(ride)
    assert ride.status == RideStatus.MATCHED
    assert ride.driver_id == 10
    
    # Verify driver status
    await db_session.refresh(profile)
    assert profile.is_available is False

@pytest.mark.asyncio
async def test_match_ride_lock_contention(db_session: AsyncSession, mock_location_service, mock_redis):
    # Setup: Create a rider, a ride
    rider = User(email="rider_contention@matching.com", hashed_password="pw")
    db_session.add(rider)
    await db_session.commit()
    
    ride = Ride(rider_id=rider.id, source_lat=37.7749, source_long=-122.4194, dest_lat=37.7849, dest_long=-122.4094)
    db_session.add(ride)
    await db_session.commit()
    
    # Driver 10 is available in DB
    driver = User(id=10, email="driver10_contention@matching.com", hashed_password="pw", role=UserRole.DRIVER)
    db_session.add(driver)
    profile = DriverProfile(user_id=10, license_plate="FLY-101", car_model="Tesla", is_available=True)
    db_session.add(profile)
    await db_session.commit()
    
    # Mock redis to return False (locked) for driver 10
    mock_redis.set.return_value = False
    
    matching_service = MatchingService(db_session, mock_location_service, mock_redis)
    
    matched_driver_id = await matching_service.match_ride(ride.id)
    
    assert matched_driver_id is None
    
    # Verify ride is still REQUESTED
    await db_session.refresh(ride)
    assert ride.status == RideStatus.REQUESTED

@pytest.mark.asyncio
async def test_match_ride_no_drivers(db_session: AsyncSession, mock_location_service, mock_redis):
    # Setup: Create a rider, a ride
    rider = User(email="rider_nodrivers@matching.com", hashed_password="pw")
    db_session.add(rider)
    await db_session.commit()
    
    ride = Ride(rider_id=rider.id, source_lat=37.7749, source_long=-122.4194, dest_lat=37.7849, dest_long=-122.4094)
    db_session.add(ride)
    await db_session.commit()
    
    # Mock location service to return empty list
    mock_location_service.find_nearby_drivers.return_value = []
    
    matching_service = MatchingService(db_session, mock_location_service, mock_redis)
    
    matched_driver_id = await matching_service.match_ride(ride.id)
    
    assert matched_driver_id is None
