from fastapi import APIRouter

from app.core.security import (
    db_dependency,
    user_dependency
)

from app.schemas.consultant_request import ConsultantRequestReview, ConsultantRequestResponse

from app.services.consultant_request_service import get_all_consultant_requests, get_consultant_request_by_id, review_consultant_request

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.get(
    "/consultant-requests",
    response_model=list[ConsultantRequestResponse]
)
async def get_all_consultant_requests_endpoint(
    db: db_dependency,
    user: user_dependency
):
    """
    Admin can view all consultant requests.
    """
    return await get_all_consultant_requests(
        db,
        user
    )


@router.get(
    "/consultant-requests/{request_id}",
    response_model=ConsultantRequestResponse
)
async def get_consultant_request_endpoint(
    request_id,
    db: db_dependency,
    user: user_dependency
):
    """
    Admin can view a specific consultant request.
    """
    return await get_consultant_request_by_id(
        db,
        user,
        request_id
    )


@router.patch(
    "/consultant-requests/{request_id}"
)
async def review_consultant_request_endpoint(
    request_id,
    review_data: ConsultantRequestReview,
    db: db_dependency,
    user: user_dependency
):
    """
    Approve or reject a consultant request.
    """
    return await review_consultant_request(
        db,
        user,
        request_id,
        review_data
    )