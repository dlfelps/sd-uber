from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.models import Ride, RideStatus, DriverProfile
from app.schemas.ride import RideRequestCreate, RideResponse, DriverAcceptInput

router = APIRouter(prefix="/ride", tags=["rides"])

@router.post("/request", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def create_ride_request(ride_in: RideRequestCreate, db: AsyncSession = Depends(get_db)):
    ride = Ride(
        rider_id=ride_in.rider_id,
        source_lat=ride_in.source_lat,
        source_long=ride_in.source_long,
        dest_lat=ride_in.dest_lat,
        dest_long=ride_in.dest_long,
        status=RideStatus.REQUESTED
    )
    db.add(ride)
    await db.commit()
    await db.refresh(ride)
    
    # In a real system, this would trigger the Matching Service asynchronously.
    # For now, we just return the created ride.
    
    return ride

@router.get("/{ride_id}", response_model=RideResponse)
async def get_ride_status(ride_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ride).where(Ride.id == ride_id))
    ride = result.scalars().first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride

@router.patch("/driver/accept")
async def driver_accept_ride(input: DriverAcceptInput, db: AsyncSession = Depends(get_db)):
    # 1. Fetch Ride
    result = await db.execute(select(Ride).where(Ride.id == input.ride_id))
    ride = result.scalars().first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    if not input.accept:
        # In this MVP, denial just returns OK. 
        # In a real system, the matching loop would continue.
        return {"status": "denied"}

    # 2. Fetch Driver Profile
    result = await db.execute(select(DriverProfile).where(DriverProfile.user_id == input.driver_id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    if ride.status != RideStatus.REQUESTED:
        raise HTTPException(status_code=400, detail="Ride is already matched or completed")
    
    if not profile.is_available:
         raise HTTPException(status_code=400, detail="Driver is not available")

    # 3. Update Status
    ride.status = RideStatus.MATCHED
    ride.driver_id = input.driver_id
    profile.is_available = False
    
    await db.commit()
    return {"status": "accepted"}
