from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict
from sqlmodel import SQLModel


class ConversationCreate(SQLModel):
    """Incoming payload when starting a new conversation."""

    participant_ids: List[int]
    title: Optional[str] = None


class ConversationRead(SQLModel):
    """Response model for conversation payloads."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]
    last_message_preview: Optional[str]
    participant_ids: List[int]


class ConversationListItem(ConversationRead):
    """Conversation summary used in list views."""

    unread_count: int = 0


class MessageRead(SQLModel):
    """Response model for chat messages."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender_id: int
    content: Optional[str]
    attachment_url: Optional[str]
    type: str
    timestamp: datetime
    is_read: bool


class MessageHistoryResponse(SQLModel):
    """Paginated response for message history requests."""

    items: List[MessageRead]
    total: int
