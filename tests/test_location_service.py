import pytest
import asyncio
from fakeredis import FakeAsyncRedis
from app.services.location_service import LocationService

@pytest.fixture
async def redis_client():
    client = FakeAsyncRedis()
    yield client
    await client.flushall()
    await client.close()

@pytest.mark.asyncio
async def test_update_driver_location(redis_client):
    service = LocationService(redis_client=redis_client)
    
    driver_id = 1
    lat = 37.7749
    long = -122.4194
    
    await service.update_location(driver_id, lat, long)
    
    # Verify directly in redis
    pos = await redis_client.geopos("driver_locations", str(driver_id))
    assert pos[0] is not None
    # Redis stores with slight precision loss, so check close enough if needed
    # But for geopos it returns a tuple (long, lat)
    assert abs(pos[0][0] - long) < 0.0001
    assert abs(pos[0][1] - lat) < 0.0001

@pytest.mark.asyncio
async def test_find_nearby_drivers(redis_client):
    service = LocationService(redis_client=redis_client)
    
    # Driver 1: Center
    await service.update_location(1, 37.7749, -122.4194)
    # Driver 2: Nearby (~1km away)
    await service.update_location(2, 37.7849, -122.4094)
    # Driver 3: Far away
    await service.update_location(3, 34.0522, -118.2437) # Los Angeles
    
    # Search around Driver 1 within 5km
    drivers = await service.find_nearby_drivers(37.7749, -122.4194, 5.0)
    
    assert 1 in drivers
    assert 2 in drivers
    assert 3 not in drivers

@pytest.mark.asyncio
async def test_find_nearby_drivers_empty(redis_client):
    service = LocationService(redis_client=redis_client)
    drivers = await service.find_nearby_drivers(37.7749, -122.4194, 5.0)
    assert drivers == []