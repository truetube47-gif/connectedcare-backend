from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class VerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ProfileVerification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    profile_id: int = Field(foreign_key="userprofile.id")
    document_type: str  # "professional_id", "medical_license", etc.
    document_url: str  # URL to uploaded document
    document_number: Optional[str] = None  # ID number from the document
    issuing_authority: Optional[str] = None  # Who issued the ID
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    status: VerificationStatus = Field(default=VerificationStatus.PENDING)
    rejection_reason: Optional[str] = None
    reviewed_by: Optional[int] = Field(foreign_key="user.id", default=None)
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    profile: Optional["UserProfile"] = Relationship(back_populates="verifications")

class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    
    # Basic profile info
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    # Professional info (for physicians/pharmacists)
    license_number: Optional[str] = None
    license_expiry: Optional[datetime] = None
    specialization: Optional[str] = None
    years_of_experience: Optional[int] = None
    workplace: Optional[str] = None
    workplace_address: Optional[str] = None
    
    # Contact info
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    
    # Medical info (for patients)
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    blood_type: Optional[str] = None
    
    # Profile completion
    is_complete: bool = Field(default=False)
    verification_status: VerificationStatus = Field(default=VerificationStatus.PENDING)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="profile")
    verifications: List[ProfileVerification] = Relationship(back_populates="profile")
