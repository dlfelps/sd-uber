from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.models import Ride, RideStatus
from app.schemas.ride import RideRequestCreate, RideResponse

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
