from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.consultant import Consultant
from app.models.user import User
from app.schemas.user import CreateUserRequest, UserRole
from app.core.security import authenticate_user, create_access_token, db_dependency, get_password_hash


async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    existing_user = db.query(User).filter(User.email == create_user_request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Email already registered.')

    # Prevent arbitrary users from registering as admins
    if create_user_request.role == UserRole.admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Cannot register with admin role.')

    create_user_model = User(
        name=create_user_request.name,
        email=create_user_request.email,
        hashed_password=get_password_hash(create_user_request.password),
        role=create_user_request.role
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    # If the user registered as a consultant, create an empty consultant profile
    if create_user_model.role == UserRole.consultant:
        create_consultant_model = Consultant(
            user_id=create_user_model.id,
            specialization=None,
            consultation_fee=None
        )
        db.add(create_consultant_model)
        db.commit()


async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.email, user.id, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}