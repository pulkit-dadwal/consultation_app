from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.models.consultation import Consultation
from app.models.consultation_message import ConsultationMessage

from app.schemas.consultation_message import (
    ConsultationMessageCreate
)

from app.core.security import (
    db_dependency,
    user_dependency
)

from app.core.websocket_manager import manager


async def send_message(
    db: db_dependency,
    user: user_dependency,
    message_data: ConsultationMessageCreate
):
    consultation = (
        db.query(Consultation)
        .filter(
            Consultation.id == message_data.consultation_id
        )
        .first()
    )

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found."
        )

    current_user_id = user.get("id")
    consultant_user_id = consultation.consultant.user_id

    allowed_users = [
        consultation.client_id,
        consultant_user_id
    ]

    if current_user_id not in allowed_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this consultation."
        )

    if consultation.status != "ongoing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat is only available for ongoing consultations."
        )

    if not consultation.started_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation has not started yet."
        )

    # End time is computed from started_at — not scheduled_at — so the client
    # gets the full paid duration regardless of when the consultant accepted.
    consultation_end_time = (
        consultation.started_at
        + timedelta(minutes=consultation.duration_minutes)
    )

    if datetime.now(timezone.utc) > consultation_end_time.replace(tzinfo=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation chat window has expired."
        )

    message = ConsultationMessage(
        consultation_id=message_data.consultation_id,
        sender_id=current_user_id,
        content=message_data.content,
        # Explicit so behaviour is not silently reliant on the DB default.
        message_type="chat"
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    if current_user_id == consultation.client_id:
        recipient_id = consultant_user_id
    else:
        recipient_id = consultation.client_id

    await manager.send_to_user(
        str(recipient_id),
        {
            "type": "chat_message",
            "consultation_id": str(consultation.id),
            "message_id": str(message.id),
            "sender_id": str(current_user_id),
            "content": message.content,
            "sent_at": message.sent_at.isoformat()
        }
    )

    return message


async def get_consultation_messages(
    db: db_dependency,
    user: user_dependency,
    consultation_id
):
    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == consultation_id)
        .first()
    )

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found."
        )

    consultant_user_id = consultation.consultant.user_id

    allowed_users = [
        consultation.client_id,
        consultant_user_id
    ]

    if user.get("id") not in allowed_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized."
        )

    messages = (
        db.query(ConsultationMessage)
        .filter(
            ConsultationMessage.consultation_id == consultation_id
        )
        .order_by(ConsultationMessage.sent_at.asc())
        .all()
    )

    return messages