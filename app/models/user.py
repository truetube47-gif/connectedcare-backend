from datetime import datetime
from enum import Enum
from typing import Optional, List, ForwardRef
from sqlmodel import SQLModel, Field, Relationship

class UserRole(str, Enum):
    PATIENT = "patient"
    PHYSICIAN = "physician"
    PHARMACY = "pharmacy"
    ADMIN = "admin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending_verification"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"

# Forward references for circular imports
Patient = ForwardRef('Patient')
Physician = ForwardRef('Physician')
Pharmacy = ForwardRef('Pharmacy')
# Notification = ForwardRef('Notification')  # Temporarily commented out
# NotificationPreference = ForwardRef('NotificationPreference')  # Temporarily commented out
ConversationParticipant = ForwardRef('ConversationParticipant')
Message = ForwardRef('Message')

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    hashed_password: str
    full_name: str
    phone_number: Optional[str] = Field(default=None, index=True)
    profile_picture_url: Optional[str] = None
    role: UserRole
    status: UserStatus = Field(default=UserStatus.PENDING)
    is_active: bool = Field(default=True)
    is_email_verified: bool = Field(default=False)
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships based on role
    patient: Optional[Patient] = Relationship(back_populates="user")
    physician: Optional[Physician] = Relationship(back_populates="user")
    pharmacy: Optional[Pharmacy] = Relationship(back_populates="user")
    
    # Notifications - Temporarily commented out
    # notifications: List[Notification] = Relationship(back_populates="user")
    # notification_preferences: Optional[NotificationPreference] = Relationship(
    #     back_populates="user",
    #     sa_relationship_kwargs={"uselist": False}
    # )
    
    # Messaging
    conversations: List[ConversationParticipant] = Relationship(back_populates="user")
    sent_messages: List[Message] = Relationship(back_populates="sender")
    
    # Documents (if user uploads documents)
    uploaded_documents: List["Document"] = Relationship(back_populates="uploaded_by_user")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "phone_number": "+1234567890",
                "role": "patient",
                "status": "pending_verification"
            }
        }