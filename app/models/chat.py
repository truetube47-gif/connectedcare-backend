from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = Field(default=None, index=True)
    last_message_preview: Optional[str] = Field(default=None)

    participants: List["ConversationParticipant"] = Relationship(back_populates="conversation")
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationParticipantRole(str, Enum):
    PATIENT = "patient"
    PHYSICIAN = "physician"
    PHARMACIST = "pharmacist"


class ConversationParticipant(SQLModel, table=True):
    conversation_id: int = Field(foreign_key="conversation.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role: ConversationParticipantRole = Field(default=ConversationParticipantRole.PATIENT)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: "Conversation" = Relationship(back_populates="participants")
    user: "User" = Relationship(back_populates="conversations")


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    sender_id: int = Field(foreign_key="user.id", index=True)

    content: Optional[str] = Field(default=None, description="Text content of the message")
    attachment_url: Optional[str] = Field(default=None, description="URL to uploaded image/file")
    type: MessageType = Field(default=MessageType.TEXT, index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    is_read: bool = Field(default=False, index=True)

    conversation: "Conversation" = Relationship(back_populates="messages")
    sender: "User" = Relationship(back_populates="sent_messages")