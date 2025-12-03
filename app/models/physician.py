from datetime import datetime, time
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from pydantic import validator
from enum import Enum

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class WeekDay(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class Availability(SQLModel):
    day: WeekDay
    start_time: str
    end_time: str
    is_available: bool = True

class Physician(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # Professional Information
    medical_license_number: str = Field(index=True)
    specialty: str
    sub_specialties: List[str] = Field(default_factory=list, sa_column=Column("sub_specialties_json", JSON))
    years_of_experience: Optional[int] = None
    
    # Practice Information
    clinic_name: str
    clinic_phone: str
    clinic_email: Optional[str] = None
    clinic_website: Optional[str] = None
    
    # Address
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "United States"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Availability
    availability: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column("availability_json", JSON),
        description="Weekly availability schedule"
    )
    
    # Verification and Status
    verification_status: VerificationStatus = Field(default=VerificationStatus.PENDING)
    verification_documents: List[Dict[str, str]] = Field(
        default_factory=list,
        sa_column=Column("verification_documents_json", JSON),
        description="List of document URLs for verification"
    )
    
    # Ratings and Reviews
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)
    review_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="physician")
    prescriptions: List["Prescription"] = Relationship(back_populates="physician")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 2,
                "medical_license_number": "MD12345678",
                "specialty": "Cardiology",
                "sub_specialties": ["Interventional Cardiology", "Heart Failure"],
                "years_of_experience": 10,
                "clinic_name": "Heart Care Specialists",
                "clinic_phone": "+12125551234",
                "clinic_email": "info@heartcare.example.com",
                "address_line1": "456 Health Ave",
                "city": "New York",
                "state": "NY",
                "postal_code": "10002",
                "availability": [
                    {"day": "monday", "start_time": "09:00", "end_time": "17:00", "is_available": True},
                    {"day": "tuesday", "start_time": "09:00", "end_time": "17:00", "is_available": True},
                    {"day": "wednesday", "start_time": "09:00", "end_time": "12:00", "is_available": True}
                ]
            }
        }