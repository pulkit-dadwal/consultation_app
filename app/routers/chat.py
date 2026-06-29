from uuid import UUID

from fastapi import APIRouter, status

from app.core.security import db_dependency, user_dependency
from app.schemas.consultation_message import (
    ConsultationMessageCreate,
    ConsultationMessageResponse,
)
from app.services.consultation_message_service import (
    get_consultation_messages,
    send_message,
)

router = APIRouter(
    prefix='/chat',
    tags=['chat']
)

@router.get(
    "/{consultation_id}/messages",
    response_model=list[ConsultationMessageResponse],
)
async def list_messages(
    consultation_id: UUID,
    db: db_dependency,
    user: user_dependency,
):
    """Return the message history for an active consultation participant."""
    return await get_consultation_messages(db, user, consultation_id)


@router.post(
    "/messages",
    response_model=ConsultationMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    message_data: ConsultationMessageCreate,
    db: db_dependency,
    user: user_dependency,
):
    """Persist a chat message and notify the other participant in real time."""
    return await send_message(db, user, message_data)
