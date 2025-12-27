from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import HumanAssistRequest
from app.schemas.human_assist import (
    HumanAssistCreate,
    HumanAssistRead,
    HumanAssistStatusPatch,
    HumanAssistAttachment,
)

router = APIRouter(prefix="/human-assist", tags=["Human Assist"])


def _serialize(record: HumanAssistRequest) -> HumanAssistRead:
    attachments: List[HumanAssistAttachment] = []
    for raw in record.attachments or []:
        try:
            attachments.append(HumanAssistAttachment.model_validate(raw))
        except Exception:
            # In case of malformed JSON row, fall back to minimal structure
            attachments.append(
                HumanAssistAttachment(
                    name=str(raw.get("name", "attachment")),
                    kind=str(raw.get("kind", "document")),
                    mime_type=raw.get("mime_type"),
                )
            )
    return HumanAssistRead(
        id=record.id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        mode=record.mode,
        service=record.service,
        summary=record.summary,
        availability=record.availability,
        status=record.status,
        attachments=attachments,
        contact_email=record.contact_email,
        contact_whatsapp=record.contact_whatsapp,
    )


@router.post("/requests", response_model=HumanAssistRead, status_code=status.HTTP_201_CREATED)
def create_request(payload: HumanAssistCreate, session: Session = Depends(get_session)):
    record = HumanAssistRequest(
        mode=payload.mode,
        service=payload.service,
        summary=payload.summary,
        availability=payload.availability,
        attachments=[attachment.model_dump() for attachment in payload.attachments],
        contact_email=payload.contact_email,
        contact_whatsapp=payload.contact_whatsapp,
        status="new",
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return _serialize(record)


@router.get("/requests", response_model=List[HumanAssistRead])
def list_requests(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
):
    statement = select(HumanAssistRequest).order_by(HumanAssistRequest.created_at.desc())
    if status_filter:
        statement = statement.where(HumanAssistRequest.status == status_filter)
    results = session.exec(statement.offset(offset).limit(limit)).all()
    return [_serialize(row) for row in results]


@router.patch("/requests/{request_id}", response_model=HumanAssistRead)
def update_request_status(
    request_id: int,
    payload: HumanAssistStatusPatch,
    session: Session = Depends(get_session),
):
    record = session.get(HumanAssistRequest, request_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    record.status = payload.status
    record.updated_at = datetime.utcnow()
    session.add(record)
    session.commit()
    session.refresh(record)
    return _serialize(record)
