from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status
)

from fastapi.security import (
    OAuth2PasswordRequestForm
)

from app.schemas.user import (
    CreateUserRequest
)

from app.services.auth_service import (
    create_user,
    login_for_access_token,
    logout_user
)

from app.core.security import (
    db_dependency,
    user_dependency,
    Token
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register_endpoint(
    db: db_dependency,
    create_user_request: CreateUserRequest
):
    return await create_user(
        db,
        create_user_request
    )


@router.post(
    "/login",
    response_model=Token
)
async def login_endpoint(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ],
    db: db_dependency
):
    return await login_for_access_token(
        form_data,
        db
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
async def logout_endpoint(
    user: user_dependency
):
    return await logout_user(
        user
    )