from typing import Annotated

from fastapi import APIRouter, Depends, status
from app.core.security import db_dependency, user_dependency
from app.services.consultant_service import get_consultant_profile, update_consultant_profile
from app.schemas.consultant import ConsultantUpdate, ConsultantResponse

router = APIRouter(
    prefix='/consultants',
    tags=['consultants']
)


@router.get('/me', response_model=ConsultantResponse)
async def get_my_consultant_profile(db: db_dependency, user: user_dependency):
    """Get current consultant's own profile"""
    return await get_consultant_profile(db, user)



@router.put('/me', response_model=ConsultantResponse)
async def update_my_consultant_profile(db: db_dependency, consultant_data: ConsultantUpdate, user: user_dependency):
    """Update current consultant's own profile"""
    return await update_consultant_profile(db, user, consultant_data)
