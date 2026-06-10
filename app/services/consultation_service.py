from fastapi import HTTPException, status
from app.models.consultation import Consultation
from app.models.consultant import Consultant
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.schemas.consultation import ConsultationCreate
from app.core.security import db_dependency, user_dependency
from datetime import datetime, timezone
from decimal import Decimal


async def create_consultation(db: db_dependency, user: user_dependency, consultation_data: ConsultationCreate):
    """Create a new consultation and transfer payment immediately if the client has enough wallet balance."""
    if user.get('user_role') != 'client':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only clients can request consultations.'
        )

    consultant_profile = db.query(Consultant).filter(Consultant.user_id == consultation_data.consultant_id).first()
    if not consultant_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Consultant profile not found.'
        )

    if consultant_profile.consultation_fee is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Consultant fee is not configured.'
        )

    if consultant_profile.status != 'online':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Consultant is currently offline and cannot accept consultations.'
        )

    client_wallet = db.query(Wallet).filter(Wallet.user_id == user.get('id')).first()
    if not client_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Client wallet not found.'
        )

    consultant_wallet = db.query(Wallet).filter(Wallet.user_id == consultation_data.consultant_id).first()
    if not consultant_wallet:
        consultant_wallet = Wallet(user_id=consultation_data.consultant_id, balance=0)
        db.add(consultant_wallet)
        db.flush()

    fee_amount = Decimal(str(consultant_profile.consultation_fee))
    if client_wallet.balance < fee_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Insufficient wallet balance to book this consultation.'
        )

    utc_now = datetime.now(timezone.utc)

    consultation = Consultation(
        client_id=user.get('id'),
        consultant_id=consultation_data.consultant_id,
        scheduled_at=utc_now,
        status='confirmed',
        notes=consultation_data.notes
    )

    client_wallet.balance -= fee_amount
    consultant_wallet.balance += fee_amount

    transaction = Transaction(
        consultation=consultation,
        amount=fee_amount,
        currency='USD',
        status='paid',
        paid_at=utc_now
    )

    db.add(consultation)
    db.add(transaction)
    db.add(client_wallet)
    db.add(consultant_wallet)
    db.commit()
    db.refresh(consultation)
    return consultation


async def get_consultations(db: db_dependency, user: user_dependency):
    """Return consultations visible to the authenticated user."""
    if user.get('user_role') == 'client':
        return db.query(Consultation).filter(Consultation.client_id == user.get('id')).all()

    if user.get('user_role') == 'consultant':
        return db.query(Consultation).filter(Consultation.consultant_id == user.get('id')).all()

    return db.query(Consultation).all()


async def get_consultation_by_id(db: db_dependency, user: user_dependency, consultation_id):
    """Return a specific consultation if the user is a participant."""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Consultation not found.'
        )

    if user.get('user_role') != 'admin' and user.get('id') not in [consultation.client_id, consultation.consultant_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to view this consultation.'
        )

    return consultation
