from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status
from app.schemas.user import CreateUserRequest
from app.services.auth_service import create_user, login_for_access_token
from app.core.security import db_dependency, Token

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(db: db_dependency, create_user_request: CreateUserRequest):
    return await create_user(db, create_user_request)

@router.post('/token', response_model=Token)
async def login_for_access_token_endpoint(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    return await login_for_access_token(form_data, db)
