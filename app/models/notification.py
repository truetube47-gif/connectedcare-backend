from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class NotificationType(str, Enum):
    APPOINTMENT_REMINDER = "appointment_reminder"
    PRESCRIPTION_READY = "prescription_ready"
    MEDICATION_REMINDER = "medication_reminder"
    ACCOUNT_ALERT = "account_alert"
    SECURITY_ALERT = "security_alert"
    SYSTEM_UPDATE = "system_update"
    PROMOTIONAL = "promotional"
    OTHER = "other"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Recipient
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # Notification Content
    title: str
    message: str
    notification_type: NotificationType = Field(default=NotificationType.OTHER)
    
    # Status and Priority
    status: NotificationStatus = Field(default=NotificationStatus.UNREAD)
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM)
    
    # Delivery
    channels: List[NotificationChannel] = Field(
        default_factory=lambda: [NotificationChannel.IN_APP],
        sa_type="JSON"
    )
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # Action
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_type="JSON",
        description="Additional metadata for the notification"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="notifications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "title": "Appointment Reminder",
                "message": "You have an appointment with Dr. Smith tomorrow at 10:00 AM",
                "notification_type": "appointment_reminder",
                "status": "unread",
                "priority": "high",
                "channels": ["in_app", "email", "sms"],
                "action_url": "/appointments/123",
                "action_label": "View Appointment"
            }
        }

class NotificationPreference(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User reference
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    
    # Channel Preferences
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = True
    in_app_enabled: bool = True
    
    # Notification Type Preferences
    appointment_reminders: bool = True
    medication_reminders: bool = True
    prescription_updates: bool = True
    account_alerts: bool = True
    promotional: bool = False
    
    # Quiet Hours
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"  # 10 PM
    quiet_hours_end: str = "08:00"    # 8 AM
    
    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="notification_preferences")
