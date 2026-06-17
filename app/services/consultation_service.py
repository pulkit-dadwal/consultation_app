from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status

from app.core.security import db_dependency, user_dependency
from app.core.websocket_manager import manager

from app.models.consultation import Consultation
from app.models.consultant import Consultant
from app.models.transaction import Transaction
from app.models.user import User

from app.schemas.consultation import ConsultationCreate, ConsultationExtend

from app.services.wallet_transaction_service import (
    create_wallet_transaction
)


def expire_consultation_if_needed(consultation):
    """
    Mark a pending consultation as expired if the consultant
    did not respond within the 2-minute window.
    Uses request_expires_at instead of recomputing from scheduled_at.
    """

    if consultation.status != "pending":
        return False

    if datetime.now(timezone.utc) > consultation.request_expires_at.replace(tzinfo=timezone.utc):
        consultation.status = "expired"
        return True

    return False


async def create_consultation(
    db: db_dependency,
    user: user_dependency,
    consultation_data: ConsultationCreate
):
    """
    Create consultation request.
    No money is deducted here — balance is checked upfront.
    The consultant is notified in real time via WebSocket.
    """

    if user.get("user_role") != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can create consultations."
        )

    consultant = (
        db.query(Consultant)
        .filter(
            Consultant.id == consultation_data.consultant_id
        )
        .first()
    )

    if not consultant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant not found."
        )

    if consultant.status != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultant is currently offline."
        )

    if not consultant.consultation_fee_per_minute or consultant.consultation_fee_per_minute == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultant fee not configured."
        )

    total_amount = (
        consultant.consultation_fee_per_minute
        * consultation_data.duration_minutes
    )

    client = (
        db.query(User)
        .filter(User.id == user.get("id"))
        .first()
    )

    if client.wallet_balance < total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient wallet balance."
        )

    now = datetime.now(timezone.utc)

    consultation = Consultation(
        client_id=user.get("id"),
        consultant_id=consultant.id,
        scheduled_at=now,
        duration_minutes=consultation_data.duration_minutes,
        original_duration_minutes=consultation_data.duration_minutes,
        total_amount=total_amount,
        status="pending",
        notes=consultation_data.notes,
        request_expires_at=now + timedelta(minutes=2),
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    await manager.send_to_user(
        str(consultant.user_id),
        {
            "type": "consultation_request",
            "consultation_id": str(consultation.id),
            "client_id": str(consultation.client_id),
            "client_name": client.name,
            "duration_minutes": consultation.duration_minutes,
            "total_amount": str(consultation.total_amount),
            "notes": consultation.notes,
            "request_expires_at": consultation.request_expires_at.isoformat(),
        }
    )

    return consultation


async def accept_consultation(
    db: db_dependency,
    user: user_dependency,
    consultation_id
):
    """
    Consultant accepts consultation.
    Fee is deducted here and chat window opens immediately.
    Client is notified in real time via WebSocket.
    """

    if user.get("user_role") != "consultant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can accept consultations."
        )

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

    if expire_consultation_if_needed(consultation):
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation request has expired."
        )

    if consultation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending consultations can be accepted."
        )

    consultant = (
        db.query(Consultant)
        .filter(Consultant.user_id == user.get("id"))
        .first()
    )

    if not consultant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant profile not found."
        )

    if consultation.consultant_id != consultant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot accept this consultation."
        )

    client = (
        db.query(User)
        .filter(User.id == consultation.client_id)
        .first()
    )

    if client.wallet_balance < consultation.total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client has insufficient wallet balance."
        )

    client.wallet_balance -= consultation.total_amount

    now = datetime.now(timezone.utc)

    consultation.status = "ongoing"
    consultation.started_at = now

    create_wallet_transaction(
        db=db,
        user_id=client.id,
        consultation_id=consultation.id,
        amount=consultation.total_amount,
        transaction_type="paid",
        description="Consultation payment"
    )

    create_wallet_transaction(
        db=db,
        user_id=consultant.user_id,
        consultation_id=consultation.id,
        amount=consultation.total_amount,
        transaction_type="received",
        description="Consultation payment received"
    )

    transaction = Transaction(
        consultation_id=consultation.id,
        amount=consultation.total_amount,
        status="paid",
        paid_at=now
    )
    db.add(transaction)

    db.commit()
    db.refresh(consultation)

    await manager.send_to_user(
        str(consultation.client_id),
        {
            "type": "consultation_accepted",
            "consultation_id": str(consultation.id),
            "started_at": consultation.started_at.isoformat(),
            "duration_minutes": consultation.duration_minutes,
            "total_amount": str(consultation.total_amount),
        }
    )

    return consultation


async def reject_consultation(
    db: db_dependency,
    user: user_dependency,
    consultation_id
):
    """
    Consultant rejects consultation.
    Client is notified in real time via WebSocket.
    """

    if user.get("user_role") != "consultant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can reject consultations."
        )

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

    if expire_consultation_if_needed(consultation):
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation request has expired."
        )

    consultant = (
        db.query(Consultant)
        .filter(Consultant.user_id == user.get("id"))
        .first()
    )

    if not consultant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant profile not found."
        )

    if consultation.consultant_id != consultant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot reject this consultation."
        )

    if consultation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending consultations can be rejected."
        )

    consultation.status = "rejected"

    db.commit()
    db.refresh(consultation)

    await manager.send_to_user(
        str(consultation.client_id),
        {
            "type": "consultation_rejected",
            "consultation_id": str(consultation.id),
        }
    )

    return consultation


async def request_consultation_extension(
    db: db_dependency,
    user: user_dependency,
    consultation_id,
    extension_data: ConsultationExtend
):
    """
    Client requests to extend an ongoing consultation.

    Checks:
    - Consultation is ongoing
    - Request comes from the client of this consultation
    - Client has enough balance for the additional time
    - No extension request is already pending (checked via a pending
      extension message in the consultation messages)

    No money is deducted yet — that happens when the consultant accepts.
    The consultant is notified via WebSocket with an extension_request event.
    """

    if user.get("user_role") != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can request extensions."
        )

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

    if consultation.client_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the client of this consultation."
        )

    if consultation.status != "ongoing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extensions can only be requested for ongoing consultations."
        )

    # Fetch the consultant to get the fee per minute
    consultant = (
        db.query(Consultant)
        .filter(Consultant.id == consultation.consultant_id)
        .first()
    )

    extension_amount = (
        consultant.consultation_fee_per_minute
        * extension_data.additional_minutes
    )

    client = (
        db.query(User)
        .filter(User.id == user.get("id"))
        .first()
    )

    if client.wallet_balance < extension_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient wallet balance for the extension."
        )

    # Store the extension request as a ConsultationMessage with
    # message_type="extension_request". The content carries the
    # requested minutes and computed amount so the consultant's UI
    # can render the accept/reject widget without a separate API call.
    from app.models.consultation_message import ConsultationMessage
    import json

    extension_payload = json.dumps({
        "additional_minutes": extension_data.additional_minutes,
        "extension_amount": str(extension_amount),
    })

    extension_message = ConsultationMessage(
        consultation_id=consultation.id,
        sender_id=user.get("id"),
        content=extension_payload,
        message_type="extension_request"
    )

    db.add(extension_message)
    db.commit()
    db.refresh(extension_message)

    # Notify the consultant in real time so the accept/reject widget
    # appears in their chat window without a page refresh.
    await manager.send_to_user(
        str(consultant.user_id),
        {
            "type": "extension_request",
            "consultation_id": str(consultation.id),
            "extension_message_id": str(extension_message.id),
            "additional_minutes": extension_data.additional_minutes,
            "extension_amount": str(extension_amount),
        }
    )

    return extension_message


async def accept_extension_request(
    db: db_dependency,
    user: user_dependency,
    consultation_id
):
    """
    Consultant accepts a pending extension request.

    - Finds the latest extension_request message for this consultation
    - Verifies client still has enough balance
    - Deducts the extension fee from the client wallet
    - Credits the consultant wallet
    - Updates duration_minutes and total_amount on the consultation
    - Notifies the client via WebSocket with the new end time
    """

    if user.get("user_role") != "consultant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can accept extension requests."
        )

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

    if consultation.status != "ongoing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation is not ongoing."
        )

    consultant = (
        db.query(Consultant)
        .filter(Consultant.user_id == user.get("id"))
        .first()
    )

    if not consultant or consultation.consultant_id != consultant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the consultant for this consultation."
        )

    # Find the most recent pending extension request message
    from app.models.consultation_message import ConsultationMessage
    import json

    extension_message = (
        db.query(ConsultationMessage)
        .filter(
            ConsultationMessage.consultation_id == consultation_id,
            ConsultationMessage.message_type == "extension_request"
        )
        .order_by(ConsultationMessage.sent_at.desc())
        .first()
    )

    if not extension_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending extension request found."
        )

    try:
        payload = json.loads(extension_message.content)
        additional_minutes = int(payload["additional_minutes"])
        extension_amount = consultant.consultation_fee_per_minute * additional_minutes
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid extension request data."
        )

    client = (
        db.query(User)
        .filter(User.id == consultation.client_id)
        .first()
    )

    if client.wallet_balance < extension_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client has insufficient wallet balance for the extension."
        )

    # Deduct fee and credit consultant
    client.wallet_balance -= extension_amount

    create_wallet_transaction(
        db=db,
        user_id=client.id,
        consultation_id=consultation.id,
        amount=extension_amount,
        transaction_type="paid",
        description=f"Extension payment ({additional_minutes} min)"
    )

    create_wallet_transaction(
        db=db,
        user_id=consultant.user_id,
        consultation_id=consultation.id,
        amount=extension_amount,
        transaction_type="received",
        description=f"Extension payment received ({additional_minutes} min)"
    )

    # Extend the consultation — duration_minutes grows, total_amount
    # reflects the full session cost. original_duration_minutes is untouched.
    consultation.duration_minutes += additional_minutes
    consultation.total_amount += extension_amount

    db.commit()
    db.refresh(consultation)

    # New end time based on updated duration so frontend can reset the timer
    new_end_time = (
        consultation.started_at
        + timedelta(minutes=consultation.duration_minutes)
    )

    await manager.send_to_user(
        str(consultation.client_id),
        {
            "type": "extension_accepted",
            "consultation_id": str(consultation.id),
            "additional_minutes": additional_minutes,
            "new_duration_minutes": consultation.duration_minutes,
            "new_end_time": new_end_time.isoformat(),
        }
    )

    return consultation


async def reject_extension_request(
    db: db_dependency,
    user: user_dependency,
    consultation_id
):
    """
    Consultant rejects a pending extension request.
    No money is touched. Client is notified via WebSocket.
    """

    if user.get("user_role") != "consultant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can reject extension requests."
        )

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

    if consultation.status != "ongoing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation is not ongoing."
        )

    consultant = (
        db.query(Consultant)
        .filter(Consultant.user_id == user.get("id"))
        .first()
    )

    if not consultant or consultation.consultant_id != consultant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the consultant for this consultation."
        )

    from app.models.consultation_message import ConsultationMessage

    extension_message = (
        db.query(ConsultationMessage)
        .filter(
            ConsultationMessage.consultation_id == consultation_id,
            ConsultationMessage.message_type == "extension_request"
        )
        .order_by(ConsultationMessage.sent_at.desc())
        .first()
    )

    if not extension_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending extension request found."
        )

    # Notify the client so they see the rejection immediately
    await manager.send_to_user(
        str(consultation.client_id),
        {
            "type": "extension_rejected",
            "consultation_id": str(consultation.id),
        }
    )

    return {"message": "Extension request rejected."}


async def get_consultations(
    db: db_dependency,
    user: user_dependency
):
    """Get consultations for the current user."""

    if user.get("user_role") == "client":
        consultations = (
            db.query(Consultation)
            .filter(Consultation.client_id == user.get("id"))
            .all()
        )

    elif user.get("user_role") == "consultant":
        consultant = (
            db.query(Consultant)
            .filter(Consultant.user_id == user.get("id"))
            .first()
        )

        if not consultant:
            return []

        consultations = (
            db.query(Consultation)
            .filter(Consultation.consultant_id == consultant.id)
            .all()
        )

    else:
        consultations = db.query(Consultation).all()

    changed = False

    for consultation in consultations:
        if expire_consultation_if_needed(consultation):
            changed = True

    if changed:
        db.commit()

    return consultations


async def get_consultation_by_id(
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

    if expire_consultation_if_needed(consultation):
        db.commit()

    if user.get("user_role") == "admin":
        return consultation

    if user.get("user_role") == "client":
        if consultation.client_id != user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized."
            )
        return consultation

    if user.get("user_role") == "consultant":
        consultant = (
            db.query(Consultant)
            .filter(Consultant.user_id == user.get("id"))
            .first()
        )

        if not consultant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultant profile not found."
            )

        if consultation.consultant_id != consultant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized."
            )

        return consultation

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized."
    )