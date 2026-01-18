import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Ride, User, DriverProfile, RideStatus, UserRole
from app.services.location_service import LocationService
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class MatchingService:
    def __init__(self, db: AsyncSession, location_service: LocationService, redis_client: Redis):
        self.db = db
        self.location_service = location_service
        self.redis = redis_client
        self.lock_ttl = 10 # seconds

    async def match_ride(self, ride_id: int):
        """
        Main loop for matching a ride with a driver.
        """
        logger.info(f"Starting matching for ride {ride_id}")
        
        # 1. Fetch Ride
        result = await self.db.execute(select(Ride).where(Ride.id == ride_id))
        ride = result.scalars().first()
        if not ride or ride.status != RideStatus.REQUESTED:
            logger.error(f"Ride {ride_id} not found or not in REQUESTED status")
            return None

        # 2. Find nearby drivers
        # Using a fixed radius of 5km for MVP
        candidate_ids = await self.location_service.find_nearby_drivers(
            ride.source_lat, ride.source_long, radius_km=5.0
        )
        logger.info(f"Found {len(candidate_ids)} candidate drivers for ride {ride_id}")

        for driver_id in candidate_ids:
            # 3. Try to lock driver in Redis
            lock_key = f"lock:driver:{driver_id}"
            # NX=True means only set if not exists
            locked = await self.redis.set(lock_key, "locked", ex=self.lock_ttl, nx=True)
            
            if not locked:
                logger.info(f"Driver {driver_id} is currently being matched with another ride (locked)")
                continue

            try:
                # 4. Check if driver is available in DB
                result = await self.db.execute(
                    select(DriverProfile).where(
                        DriverProfile.user_id == driver_id,
                        DriverProfile.is_available == True
                    )
                )
                profile = result.scalars().first()
                
                if profile:
                    # 5. MATCH FOUND!
                    logger.info(f"Matching ride {ride_id} with driver {driver_id}")
                    
                    ride.status = RideStatus.MATCHED
                    ride.driver_id = driver_id
                    profile.is_available = False
                    
                    await self.db.commit()
                    return driver_id
                else:
                    logger.info(f"Driver {driver_id} is not available in database")
            finally:
                # Release lock if we didn't match (or even if we did, 
                # but in real system we might keep it until acceptance)
                # For this simple loop, we release it if not matched.
                # If matched, driver is now is_available=False anyway.
                await self.redis.delete(lock_key)

        logger.warning(f"No available drivers found for ride {ride_id}")
        return None
