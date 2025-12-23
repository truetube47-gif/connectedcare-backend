from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
import json


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
    __tablename__ = "notifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    message: str
    notification_type: NotificationType = Field(default=NotificationType.OTHER)
    status: NotificationStatus = Field(default=NotificationStatus.UNREAD)
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM)
    
    # Stored as JSON text safely
    channels_raw: str = Field(default="[]")
    metadata_raw: str = Field(default="{}")
    
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="notifications")

    # ---------- JSON Helpers ----------
    @property
    def channels(self) -> List[NotificationChannel]:
        return [NotificationChannel(c) for c in json.loads(self.channels_raw)]

    @channels.setter
    def channels(self, value: List[NotificationChannel]):
        self.channels_raw = json.dumps([v.value for v in value])

    @property
    def metadata(self) -> Dict[str, Any]:
        return json.loads(self.metadata_raw)

    @metadata.setter
    def metadata(self, value: Dict[str, Any]):
        self.metadata_raw = json.dumps(value)


class NotificationPreference(SQLModel, table=True):
    __tablename__ = "notification_preferences"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = True
    in_app_enabled: bool = True
    appointment_reminders: bool = True
    medication_reminders: bool = True
    prescription_updates: bool = True
    account_alerts: bool = True
    promotional: bool = False
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="notification_preferences")
