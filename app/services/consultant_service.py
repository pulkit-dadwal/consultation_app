from fastapi import HTTPException, status
from app.models.consultant import Consultant
from app.models.user import User
from app.schemas.consultant import ConsultantUpdate
from app.core.security import db_dependency, user_dependency


async def get_all_consultants(db: db_dependency, user: user_dependency):
    """Get all consultants"""
    if(user.get('user_role') == 'consultant'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only clients can view all consultants.")
    consultants = db.query(Consultant).all()
    return consultants


async def get_top_rated_consultants(db: db_dependency, user: user_dependency):
    """Get top-rated consultants"""
    if(user.get('user_role') == 'consultant'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only clients can view top-rated consultants.")
    consultants = db.query(Consultant).filter(Consultant.rating >= 4.0).all()
    return consultants


async def get_consultant_profile_by_id(db: db_dependency, user: user_dependency, consultant_id):
    """Get a consultant profile by ID"""
    if(user.get('user_role') == 'consultant'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only clients can view consultant profiles.")
    
    consultant = db.query(Consultant).filter(Consultant.id == consultant_id).first()
    if not consultant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultant profile not found.")
    return consultant


async def get_consultant_profile(db: db_dependency, user: user_dependency):
    """Get consultant profile for the authenticated user"""
    user_id = user.get('id')
    # Ensure user is a consultant
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user.role != "consultant":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a consultant.")

    consultant = db.query(Consultant).filter(Consultant.user_id == user_id).first()
    if not consultant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultant profile not found.")
    return consultant


async def update_consultant_profile(db: db_dependency, user: user_dependency, consultant_data: ConsultantUpdate):
    """Update consultant profile for the authenticated user"""
    user_id = user.get('id')
    # Ensure user is a consultant
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user.role != "consultant":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a consultant.")

    consultant = db.query(Consultant).filter(Consultant.user_id == user_id).first()
    if not consultant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultant profile not found.")

    update_data = consultant_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(consultant, key, value)

    db.add(consultant)
    db.commit()
    db.refresh(consultant)
    return consultant
