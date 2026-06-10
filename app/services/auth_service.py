from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.user import CreateUserRequest
from app.core.security import authenticate_user, create_access_token, db_dependency, get_password_hash


async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    existing_user = db.query(User).filter(User.email == create_user_request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Email already registered.')

    create_user_model = User(
        name=create_user_request.name,
        email=create_user_request.email,
        hashed_password=get_password_hash(create_user_request.password),
        role='client'
    )

    db.add(create_user_model)
    db.flush()

    db.add(Wallet(user_id=create_user_model.id, balance=0))
    db.commit()
    db.refresh(create_user_model)


async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.email, user.id, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}