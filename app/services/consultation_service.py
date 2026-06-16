from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status

from app.core.security import db_dependency, user_dependency

from app.models.consultation import Consultation
from app.models.consultant import Consultant
from app.models.user import User

from app.schemas.consultation import ConsultationCreate

from app.services.wallet_transaction_service import (
    create_wallet_transaction
)


def expire_consultation_if_needed(consultation):
    """
    Automatically expire pending consultations
    after 2 minutes.
    """

    if consultation.status != "pending":
        return False

    expiry_time = consultation.scheduled_at + timedelta(minutes=2)

    if datetime.now(timezone.utc) > expiry_time:
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
    No money is deducted here.
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

    if consultant.consultation_fee_per_minute is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultant fee not configured."
        )

    total_amount = (
        consultant.consultation_fee_per_minute
        * consultation_data.duration_minutes
    )

    consultation = Consultation(
        client_id=user.get("id"),
        consultant_id=consultant.id,
        scheduled_at=datetime.now(timezone.utc),
        duration_minutes=consultation_data.duration_minutes,
        total_amount=total_amount,
        status="pending",
        notes=consultation_data.notes
    )

    db.add(consultation)

    db.commit()

    db.refresh(consultation)

    return consultation


async def accept_consultation(
    db: db_dependency,
    user: user_dependency,
    consultation_id
):
    """
    Consultant accepts consultation.
    Payment happens here.
    """

    if user.get("user_role") != "consultant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can accept consultations."
        )

    consultation = (
        db.query(Consultation)
        .filter(
            Consultation.id == consultation_id
        )
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
        .filter(
            Consultant.user_id == user.get("id")
        )
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

    if consultation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending consultations can be accepted."
        )

    client = (
        db.query(User)
        .filter(
            User.id == consultation.client_id
        )
        .first()
    )

    if client.wallet_balance < consultation.total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client has insufficient wallet balance."
        )

    client.wallet_balance -= consultation.total_amount

    consultation.status = "accepted"

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

    db.commit()

    db.refresh(consultation)

    return consultation


async def reject_consultation(
    db: db_dependency,
    user: user_dependency,
    consultation_id
):
    """
    Consultant rejects consultation.
    """

    if user.get("user_role") != "consultant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can reject consultations."
        )

    consultation = (
        db.query(Consultation)
        .filter(
            Consultation.id == consultation_id
        )
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
        .filter(
            Consultant.user_id == user.get("id")
        )
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

    return consultation


async def get_consultations(
    db: db_dependency,
    user: user_dependency
):
    """
    Get consultations for current user.
    """

    if user.get("user_role") == "client":

        consultations = (
            db.query(Consultation)
            .filter(
                Consultation.client_id == user.get("id")
            )
            .all()
        )

    elif user.get("user_role") == "consultant":

        consultant = (
            db.query(Consultant)
            .filter(
                Consultant.user_id == user.get("id")
            )
            .first()
        )

        if not consultant:
            return []

        consultations = (
            db.query(Consultation)
            .filter(
                Consultation.consultant_id == consultant.id
            )
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
        .filter(
            Consultation.id == consultation_id
        )
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
            .filter(
                Consultant.user_id == user.get("id")
            )
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