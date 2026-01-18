import pytest
from unittest.mock import patch, MagicMock
from app.scripts.driver_simulator import simulate
from fakeredis import FakeAsyncRedis

@pytest.mark.asyncio
async def test_simulate_logic():
    # Mock Redis.from_url to return FakeAsyncRedis
    with patch("app.scripts.driver_simulator.Redis.from_url") as mock_from_url:
        fake_redis = FakeAsyncRedis()
        mock_from_url.return_value = fake_redis
        
        # Run for 1 iteration
        await simulate(driver_ids=[1], interval=0.1, redis_url="redis://dummy", iterations=1)
        
        # Verify location was updated in fake_redis
        pos = await fake_redis.geopos("driver_locations", "1")
        assert pos[0] is not None
        
        await fake_redis.close()
