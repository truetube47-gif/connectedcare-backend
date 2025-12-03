from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from enum import Enum

class PrescriptionStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FULFILLED = "fulfilled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class MedicationDosage(SQLModel):
    morning: bool = False
    afternoon: bool = False
    evening: bool = False
    night: bool = False
    as_needed: bool = False
    instructions: Optional[str] = None

class Medication(SQLModel):
    name: str
    dosage: str
    frequency: str
    quantity: int
    refills: int = 0
    dosage_instructions: MedicationDosage
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None

class Prescription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    patient_id: int = Field(foreign_key="patient.id", index=True)
    physician_id: int = Field(foreign_key="physician.id", index=True)
    pharmacy_id: Optional[int] = Field(foreign_key="pharmacy.id", index=True, nullable=True)
    
    # Prescription Details
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    medications: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of prescribed medications with details"
    )
    
    # Status and Dates
    status: PrescriptionStatus = Field(default=PrescriptionStatus.DRAFT)
    prescribed_date: date = Field(default_factory=date.today)
    expiry_date: Optional[date] = None
    filled_date: Optional[datetime] = None
    
    # Refill Information
    refills_remaining: int = 0
    refill_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="History of refills with dates and quantities"
    )
    
    # Digital Signature
    physician_signature: Optional[str] = None
    signed_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    patient: Optional["Patient"] = Relationship(back_populates="prescriptions")
    physician: Optional["Physician"] = Relationship(back_populates="prescriptions")
    pharmacy: Optional["Pharmacy"] = Relationship(back_populates="prescriptions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "physician_id": 2,
                "pharmacy_id": 3,
                "diagnosis": "Hypertension",
                "notes": "Take with food. Avoid alcohol.",
                "status": "pending",
                "prescribed_date": "2025-11-26",
                "expiry_date": "2026-05-26",
                "medications": [
                    {
                        "name": "Lisinopril",
                        "dosage": "10mg",
                        "frequency": "Once daily",
                        "quantity": 30,
                        "refills": 2,
                        "dosage_instructions": {
                            "morning": True,
                            "afternoon": False,
                            "evening": False,
                            "night": False,
                            "as_needed": False,
                            "instructions": "Take in the morning with food"
                        },
                        "start_date": "2025-11-26",
                        "end_date": "2026-02-26"
                    }
                ]
            }
        }