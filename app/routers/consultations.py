from typing import Annotated

from fastapi import APIRouter, Depends, status
from app.core.security import db_dependency, user_dependency
from app.schemas.consultation import ConsultationCreate, ConsultationResponse
from app.services.consultation_service import create_consultation, get_consultations, get_consultation_by_id

router = APIRouter(
    prefix='/consultations',
    tags=['consultations']
)


@router.post('/', response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
async def create_consultation_endpoint(consultation_data: ConsultationCreate, db: db_dependency, user: user_dependency):
    """Create a consultation request for the authenticated client."""
    return await create_consultation(db, user, consultation_data)


@router.get('/', response_model=list[ConsultationResponse])
async def list_consultations_endpoint(db: db_dependency, user: user_dependency):
    """List consultations for the authenticated user."""
    return await get_consultations(db, user)


@router.get('/{consultation_id}', response_model=ConsultationResponse)
async def get_consultation_endpoint(consultation_id: str, db: db_dependency, user: user_dependency):
    """Get a single consultation if the current user is a participant."""
    return await get_consultation_by_id(db, user, consultation_id)