from typing import Annotated

from fastapi import APIRouter, Depends, status
from app.core.security import db_dependency, user_dependency
from app.services.consultant_service import get_consultant_profile, update_consultant_profile, get_all_consultants, get_top_rated_consultants
from app.schemas.consultant import ConsultantUpdate, ConsultantResponse

router = APIRouter(
    prefix='/consultants',
    tags=['consultants']
)


@router.get('/')
async def get_all_consultants_profile(db: db_dependency, user: user_dependency):
    """Get all consultants"""
    return await get_all_consultants(db, user)


@router.get('/top-rated')
async def get_top_rated_consultants_profile(db: db_dependency, user: user_dependency):
    """Get top-rated consultants"""
    return await get_top_rated_consultants(db, user)


@router.get('/{consultant_id}', response_model=ConsultantResponse)
async def get_consultant_profile_by_id(consultant_id: str, db: db_dependency, user: user_dependency):
    """Get a consultant profile by ID"""
    return await get_consultant_profile(db, user, consultant_id)



@router.get('/profile', response_model=ConsultantResponse)
async def get_my_consultant_profile(db: db_dependency, user: user_dependency):
    """Get current consultant's own profile"""
    return await get_consultant_profile(db, user)



@router.put('/profile', response_model=ConsultantResponse)
async def update_my_consultant_profile(db: db_dependency, consultant_data: ConsultantUpdate, user: user_dependency):
    """Update current consultant's own profile"""
    return await update_consultant_profile(db, user, consultant_data)
