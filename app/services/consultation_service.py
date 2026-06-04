from fastapi import HTTPException, status
from app.models.consultation import Consultation
from app.models.consultant import Consultant
from app.models.user import User
from app.schemas.consultation import ConsultationCreate
from app.core.security import db_dependency, user_dependency


async def create_consultation(db: db_dependency, user: user_dependency, consultation_data: ConsultationCreate):
    """Create a new consultation request from a client."""
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

    consultation = Consultation(
        client_id=user.get('id'),
        consultant_id=consultation_data.consultant_id,
        scheduled_at=consultation_data.scheduled_at,
        status='pending',
        notes=consultation_data.notes
    )

    db.add(consultation)
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
