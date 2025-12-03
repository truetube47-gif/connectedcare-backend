from datetime import datetime, time
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

class AppointmentType(str, Enum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    ROUTINE_CHECKUP = "routine_checkup"
    URGENT_CARE = "urgent_care"
    VACCINATION = "vaccination"
    OTHER = "other"

class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    patient_id: int = Field(foreign_key="patient.id", index=True)
    physician_id: int = Field(foreign_key="physician.id", index=True)
    
    # Appointment Details
    title: str
    description: Optional[str] = None
    appointment_type: AppointmentType = Field(default=AppointmentType.CONSULTATION)
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED)
    
    # Timing
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    
    # Location
    is_virtual: bool = False
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    
    # Reminders
    reminder_sent: bool = False
    reminder_sent_at: Optional[datetime] = None
    
    # Cancellation
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_type="JSON",
        description="Additional metadata for the appointment"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    patient: Optional["Patient"] = Relationship(back_populates="appointments")
    physician: Optional["Physician"] = Relationship(back_populates="appointments")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "physician_id": 2,
                "title": "Annual Checkup",
                "description": "Routine annual health checkup",
                "appointment_type": "routine_checkup",
                "status": "scheduled",
                "start_time": "2023-12-15T10:00:00",
                "end_time": "2023-12-15T10:30:00",
                "timezone": "America/New_York",
                "is_virtual": False,
                "location": "123 Medical Center, Suite 100, New York, NY 10001"
            }
        }
