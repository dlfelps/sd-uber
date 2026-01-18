from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.base import Base

class UserRole(enum.Enum):
    RIDER = "rider"
    DRIVER = "driver"
    ADMIN = "admin"

class RideStatus(enum.Enum):
    REQUESTED = "requested"
    MATCHED = "matched"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.RIDER)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    driver_profile = relationship("DriverProfile", back_populates="user", uselist=False)
    rides_as_rider = relationship("Ride", foreign_keys="[Ride.rider_id]", back_populates="rider")
    rides_as_driver = relationship("Ride", foreign_keys="[Ride.driver_id]", back_populates="driver")

class DriverProfile(Base):
    __tablename__ = "driver_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    license_plate = Column(String, nullable=False)
    car_model = Column(String, nullable=False)
    is_available = Column(Boolean, default=False)
    current_lat = Column(Float, nullable=True)
    current_long = Column(Float, nullable=True)
    
    user = relationship("User", back_populates="driver_profile")

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    source_lat = Column(Float, nullable=False)
    source_long = Column(Float, nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_long = Column(Float, nullable=False)
    
    status = Column(Enum(RideStatus), default=RideStatus.REQUESTED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    estimated_fare = Column(Float, nullable=True)
    estimated_time = Column(Integer, nullable=True) # in seconds
    
    rider = relationship("User", foreign_keys=[rider_id], back_populates="rides_as_rider")
    driver = relationship("User", foreign_keys=[driver_id], back_populates="rides_as_driver")
