from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class HumanAssistRequest(SQLModel, table=True):
    """Stores concierge requests sent from the PillPal app."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    mode: str = Field(nullable=False, description="chat or live")
    service: str = Field(nullable=False, description="pharmacist or clinician")
    summary: str = Field(nullable=False)
    availability: Optional[str] = Field(default=None)
    status: str = Field(default="new", nullable=False)
    attachments: List[dict] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False, default=list),
    )
    contact_email: Optional[str] = Field(default=None)
    contact_whatsapp: Optional[str] = Field(default=None)
