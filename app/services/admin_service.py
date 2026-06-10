from fastapi import HTTPException, status
from app.models.consultant import Consultant
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.admin import PromoteUserRequest
from app.core.security import db_dependency, user_dependency
from datetime import datetime, timezone


async def promote_client_to_consultant(db: db_dependency, user: user_dependency, promote_request: PromoteUserRequest):
    """Promote an existing client to consultant using email."""
    if user.get('user_role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only admins can promote users to consultants.'
        )

    existing_user = db.query(User).filter(User.email == promote_request.email).first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found.'
        )

    if existing_user.role == 'consultant':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is already a consultant.'
        )

    if existing_user.role == 'admin':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Admin accounts cannot be promoted.'
        )

    existing_user.role = 'consultant'

    consultant_profile = db.query(Consultant).filter(Consultant.user_id == existing_user.id).first()
    if not consultant_profile:
        consultant_profile = Consultant(
            user_id=existing_user.id,
            specialization=None,
            consultation_fee=None,
            status='online'
        )
        db.add(consultant_profile)

    wallet = db.query(Wallet).filter(Wallet.user_id == existing_user.id).first()
    if not wallet:
        wallet = Wallet(user_id=existing_user.id, balance=0)
        db.add(wallet)

    db.add(existing_user)
    db.commit()
    db.refresh(existing_user)
    return {'message': 'User promoted to consultant successfully.'}
