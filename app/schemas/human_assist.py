from datetime import datetime
from typing import List, Optional

from pydantic import Field, validator
from sqlmodel import SQLModel


class HumanAssistAttachment(SQLModel):
    name: str
    kind: str
    mime_type: Optional[str] = None
    base64: Optional[str] = None


class HumanAssistCreate(SQLModel):
    mode: str = Field(..., description="chat or live")
    service: str = Field(..., description="pharmacist or clinician")
    summary: str
    availability: Optional[str] = None
    attachments: List[HumanAssistAttachment] = Field(default_factory=list)
    contact_email: Optional[str] = None
    contact_whatsapp: Optional[str] = None

    @validator("attachments", each_item=True)
    def validate_attachment(cls, value: HumanAssistAttachment):  # type: ignore[override]
        if value.kind not in {"image", "document"}:
            raise ValueError("Attachment kind must be image or document")
        return value


class HumanAssistRead(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime
    mode: str
    service: str
    summary: str
    availability: Optional[str]
    status: str
    attachments: List[HumanAssistAttachment]
    contact_email: Optional[str]
    contact_whatsapp: Optional[str]


class HumanAssistStatusPatch(SQLModel):
    status: str = Field(..., description="new, in_progress, resolved")
