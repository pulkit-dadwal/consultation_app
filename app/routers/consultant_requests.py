from uuid import UUID

from fastapi import APIRouter, status

from app.core.security import db_dependency, user_dependency
from app.schemas.consultant_request import (
    ConsultantRequestCreate,
    ConsultantRequestResponse
)
from app.services.consultant_request_service import (
    create_consultant_request,
    get_consultant_request_by_id,
    get_my_consultant_requests
)

router = APIRouter(
    prefix="/consultant-requests",
    tags=["consultant-requests"]
)


@router.post(
    "/",
    response_model=ConsultantRequestResponse,
    status_code=status.HTTP_201_CREATED
)
async def submit_consultant_request(
    request_data: ConsultantRequestCreate,
    db: db_dependency,
    user: user_dependency
):
    """Client submits a request to become a consultant."""
    return await create_consultant_request(db, user, request_data)


@router.get(
    "/",
    response_model=list[ConsultantRequestResponse]
)
async def list_my_consultant_requests(
    db: db_dependency,
    user: user_dependency
):
    """Get all consultant requests submitted by the current user."""
    return await get_my_consultant_requests(db, user)


@router.get(
    "/{request_id}",
    response_model=ConsultantRequestResponse
)
async def get_my_consultant_request(
    request_id: UUID,
    db: db_dependency,
    user: user_dependency
):
    """Get a specific consultant request belonging to the current user."""
    return await get_consultant_request_by_id(db, user, request_id)
