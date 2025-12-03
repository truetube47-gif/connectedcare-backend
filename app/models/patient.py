from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from pydantic import EmailStr, HttpUrl

class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class Patient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # Personal Information
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_type: Optional[BloodType] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    
    # Contact Information
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    
    # Medical Information
    allergies: List[str] = Field(default_factory=list, sa_column=Column("allergies_json", JSON))
    current_medications: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column("current_medications_json", JSON))
    medical_history: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column("medical_history_json", JSON))
    
    # Insurance Information
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry_date: Optional[date] = None
    
    # Address
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "United States"
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_medical_checkup: Optional[datetime] = None
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="patient")
    prescriptions: List["Prescription"] = Relationship(back_populates="patient")
    documents: List["Document"] = Relationship(back_populates="patient")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "date_of_birth": "1990-01-01",
                "gender": "Male",
                "blood_type": "A+",
                "emergency_contact_name": "Jane Smith",
                "emergency_contact_phone": "+1234567890",
                "emergency_contact_relation": "Spouse",
                "allergies": ["Penicillin", "Peanuts"],
                "insurance_provider": "Blue Cross",
                "address_line1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "United States"
            }
        }