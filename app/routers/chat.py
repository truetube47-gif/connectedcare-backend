from datetime import datetime
import json
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy import func
from sqlmodel import Session, select

from app.chat_manager import manager
from app.database import get_session
from app.models import (
    Conversation,
    ConversationParticipant,
    ConversationParticipantRole,
    Message,
    MessageType,
    User,
    UserRole,
)
from app.schemas.chat import (
    ConversationCreate,
    ConversationListItem,
    ConversationRead,
    MessageHistoryResponse,
    MessageRead,
)
from app.utils.security import (
    get_current_active_user,
    get_user_from_token,
)

router = APIRouter(tags=["Chat"])


def _map_role(user: User) -> ConversationParticipantRole:
    mapping = {
        UserRole.PATIENT: ConversationParticipantRole.PATIENT,
        UserRole.PHYSICIAN: ConversationParticipantRole.PHYSICIAN,
        UserRole.PHARMACY: ConversationParticipantRole.PHARMACIST,
    }
    return mapping.get(user.role, ConversationParticipantRole.PATIENT)


def _ensure_participant(session: Session, conversation_id: int, user_id: int) -> None:
    exists = session.exec(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id,
        )
    ).first()
    if not exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a conversation participant")


def _get_participant_ids(session: Session, conversation_id: int) -> List[int]:
    rows = session.exec(
        select(ConversationParticipant.user_id).where(
            ConversationParticipant.conversation_id == conversation_id
        )
    ).all()
    return [row[0] if isinstance(row, tuple) else row for row in rows]


def _serialize_conversation(session: Session, conversation: Conversation) -> ConversationRead:
    participant_ids = _get_participant_ids(session, conversation.id)
    return ConversationRead(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_message_at=conversation.last_message_at,
        last_message_preview=conversation.last_message_preview,
        participant_ids=participant_ids,
    )


def _serialize_message(message: Message) -> MessageRead:
    return MessageRead.model_validate(message)


def _get_unread_count(session: Session, conversation_id: int, user_id: int) -> int:
    result = session.exec(
        select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,
            Message.is_read.is_(False),
        )
    ).one()
    return int(result or 0)


def _create_conversation(
    session: Session, *, participant_ids: List[int], title: str | None = None
) -> Conversation:
    conversation = Conversation(title=title)
    session.add(conversation)
    session.flush()

    users = session.exec(select(User).where(User.id.in_(participant_ids))).all()
    user_ids = {user.id for user in users}
    if len(user_ids) != len(participant_ids):
        raise HTTPException(status_code=404, detail="One or more participants were not found")

    for user in users:
        session.add(
            ConversationParticipant(
                conversation_id=conversation.id,
                user_id=user.id,
                role=_map_role(user),
            )
        )

    session.commit()
    session.refresh(conversation)
    return conversation


@router.post(
    "/conversations/",
    response_model=ConversationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    payload: ConversationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    participant_ids = set(payload.participant_ids)
    participant_ids.add(current_user.id)
    if len(participant_ids) < 2:
        raise HTTPException(status_code=400, detail="A conversation requires at least two participants")

    conversation = _create_conversation(
        session,
        participant_ids=list(participant_ids),
        title=payload.title,
    )
    return _serialize_conversation(session, conversation)


@router.get("/conversations/{conversation_id}", response_model=ConversationRead)
def get_conversation(
    conversation_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    _ensure_participant(session, conversation_id, current_user.id)
    return _serialize_conversation(session, conversation)


@router.get("/conversations/by-users", response_model=ConversationRead)
def get_or_create_conversation(
    user_a: int,
    user_b: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.id not in {user_a, user_b}:
        raise HTTPException(status_code=403, detail="Access denied")
    if user_a == user_b:
        raise HTTPException(status_code=400, detail="user_a and user_b must be different")

    user_set = {user_a, user_b}
    subquery = (
        select(ConversationParticipant.conversation_id)
        .where(ConversationParticipant.user_id.in_(user_set))
        .group_by(ConversationParticipant.conversation_id)
        .having(func.count(ConversationParticipant.user_id) == len(user_set))
    )
    existing = session.exec(select(Conversation).where(Conversation.id.in_(subquery))).first()
    if existing:
        return _serialize_conversation(session, existing)

    conversation = _create_conversation(session, participant_ids=list(user_set))
    return _serialize_conversation(session, conversation)


@router.get(
    "/users/{user_id}/conversations",
    response_model=List[ConversationListItem],
)
def list_user_conversations(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot view another user's conversations")

    conversations = session.exec(
        select(Conversation)
        .join(ConversationParticipant)
        .where(ConversationParticipant.user_id == user_id)
        .order_by(Conversation.last_message_at.desc().nullslast())
    ).all()

    items: List[ConversationListItem] = []
    for conversation in conversations:
        serialized = _serialize_conversation(session, conversation)
        items.append(
            ConversationListItem(
                **serialized.model_dump(),
                unread_count=_get_unread_count(session, conversation.id, user_id),
            )
        )
    return items


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=MessageHistoryResponse,
)
def get_message_history(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    _ensure_participant(session, conversation_id, current_user.id)

    total = session.exec(
        select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    ).one()

    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    serialized = [_serialize_message(message) for message in reversed(messages)]
    return MessageHistoryResponse(items=serialized, total=int(total or 0))


@router.patch("/messages/{message_id}/read", response_model=MessageRead)
def mark_message_read(
    message_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    _ensure_participant(session, message.conversation_id, current_user.id)

    if message.sender_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot mark your own message as read")

    if not message.is_read:
        message.is_read = True
        session.add(message)
        session.commit()
        session.refresh(message)

    return _serialize_message(message)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_session),
):
    """Authenticate via token query param and relay chat messages."""

    user = get_user_from_token(token=token, db=db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = user.id
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            conversation_id = message_data.get("conversation_id")
            if conversation_id is None:
                await websocket.send_json({"error": "conversation_id is required"})
                continue

            _ensure_participant(db, int(conversation_id), user_id)

            message_type_value = message_data.get("type", MessageType.TEXT.value)
            try:
                message_type = MessageType(message_type_value)
            except ValueError:
                message_type = MessageType.TEXT

            content = message_data.get("content")
            attachment_url = message_data.get("attachment_url")

            db_message = Message(
                conversation_id=conversation_id,
                sender_id=user_id,
                content=content,
                attachment_url=attachment_url,
                type=message_type,
                is_read=True,
            )
            conversation = db.get(Conversation, conversation_id)
            if not conversation:
                await websocket.send_json({"error": "Conversation not found"})
                continue

            conversation.last_message_at = db_message.timestamp
            conversation.updated_at = datetime.utcnow()
            if content:
                conversation.last_message_preview = content[:140]
            elif attachment_url:
                conversation.last_message_preview = "Image attachment"

            db.add(db_message)
            db.add(conversation)
            db.commit()
            db.refresh(db_message)

            participants = _get_participant_ids(db, conversation_id)
            payload = _serialize_message(db_message).model_dump()
            await manager.broadcast(payload, participants)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception:
        manager.disconnect(user_id)
