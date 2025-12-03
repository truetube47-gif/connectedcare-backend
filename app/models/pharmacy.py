from datetime import datetime, time
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from pydantic import validator
from enum import Enum

class PharmacyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    VERIFICATION_PENDING = "verification_pending"

class WeekDay(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class OperatingHours(SQLModel):
    day: WeekDay
    open_time: str
    close_time: str
    is_open: bool = True

class Pharmacy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # Pharmacy Information
    name: str
    description: Optional[str] = None
    license_number: str = Field(index=True)
    status: PharmacyStatus = Field(default=PharmacyStatus.VERIFICATION_PENDING)
    
    # Contact Information
    phone: str
    email: Optional[str] = None
    website: Optional[str] = None
    
    # Address
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "United States"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Operating Hours
    operating_hours: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Weekly operating hours"
    )
    
    # Services
    services: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of services offered (e.g., 'delivery', 'in_store_pickup', 'compounding')"
    )
    
    # Verification
    verification_documents: List[Dict[str, str]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of document URLs for verification"
    )
    verified_at: Optional[datetime] = None
    
    # Ratings and Reviews
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)
    review_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="pharmacy")
    prescriptions: List["Prescription"] = Relationship(back_populates="pharmacy")
    inventory: List["InventoryItem"] = Relationship(back_populates="pharmacy")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 3,
                "name": "24/7 Wellness Pharmacy",
                "license_number": "PH12345678",
                "phone": "+12125556789",
                "email": "contact@wellnesspharmacy.example.com",
                "address_line1": "789 Health St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10003",
                "services": ["delivery", "in_store_pickup", "compounding"],
                "operating_hours": [
                    {"day": "monday", "open_time": "08:00", "close_time": "22:00", "is_open": True},
                    {"day": "tuesday", "open_time": "08:00", "close_time": "22:00", "is_open": True},
                    {"day": "sunday", "open_time": "09:00", "close_time": "18:00", "is_open": True}
                ]
            }
        }