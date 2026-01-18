from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class RideRequestCreate(BaseModel):
    rider_id: int
    source_lat: float
    source_long: float
    dest_lat: float
    dest_long: float

class RideResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rider_id: int
    driver_id: Optional[int] = None
    source_lat: float
    source_long: float
    dest_lat: float
    dest_long: float
    status: str
    created_at: datetime
    estimated_fare: Optional[float] = None

class DriverAcceptInput(BaseModel):
    ride_id: int
    driver_id: int
    accept: bool
