import asyncio
import os
from sqlalchemy import select, delete
from redis.asyncio import Redis

from app.db.base import AsyncSessionLocal, engine
from app.models.models import User, DriverProfile, Ride, UserRole, RideStatus
from app.services.location_service import LocationService
from app.services.matching_service import MatchingService

async def main():
    # Load environment
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    print("--- Phase 3 Verification: Matching Loop ---")
    
    async with AsyncSessionLocal() as db:
        # 1. Cleanup old test data
        await db.execute(delete(Ride))
        await db.execute(delete(DriverProfile))
        await db.execute(delete(User).where(User.email.like("test_%")))
        await db.commit()
        
        # 2. Setup Rider
        rider = User(
            email="test_rider@example.com", 
            hashed_password="pw", 
            full_name="Test Rider",
            role=UserRole.RIDER
        )
        db.add(rider)
        await db.commit()
        await db.refresh(rider)
        print(f"Created Rider: {rider.id}")
        
        # 3. Setup Driver
        driver = User(
            email="test_driver@example.com", 
            hashed_password="pw", 
            full_name="Test Driver",
            role=UserRole.DRIVER
        )
        db.add(driver)
        await db.commit()
        await db.refresh(driver)
        
        profile = DriverProfile(
            user_id=driver.id, 
            license_plate="VERIFY-1", 
            car_model="Test Car", 
            is_available=True
        )
        db.add(profile)
        await db.commit()
        print(f"Created Driver: {driver.id} (Available)")
        
        # 4. Update Driver Location in Redis
        redis_client = Redis.from_url(redis_url)
        location_service = LocationService(redis_client)
        
        # San Francisco location
        lat, lon = 37.7749, -122.4194
        await location_service.update_location(driver.id, lat, lon)
        print(f"Updated Driver {driver.id} location in Redis.")
        
        # 5. Create Ride Request
        ride = Ride(
            rider_id=rider.id,
            source_lat=lat,
            source_long=lon,
            dest_lat=37.7849,
            dest_long=-122.4094,
            status=RideStatus.REQUESTED
        )
        db.add(ride)
        await db.commit()
        await db.refresh(ride)
        print(f"Created Ride Request: {ride.id}")
        
        # 6. Run Matching Service
        matching_service = MatchingService(db, location_service, redis_client)
        print("Running Matching Service...")
        matched_driver_id = await matching_service.match_ride(ride.id)
        
        # 7. Verification
        if matched_driver_id == driver.id:
            print(f"SUCCESS: Ride {ride.id} matched with Driver {matched_driver_id}")
            
            await db.refresh(ride)
            await db.refresh(profile)
            
            print(f"Ride Status: {ride.status}")
            print(f"Driver Availability: {profile.is_available}")
        else:
            print(f"FAILURE: Expected match with {driver.id}, but got {matched_driver_id}")

        await redis_client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
