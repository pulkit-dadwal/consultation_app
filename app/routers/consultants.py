from uuid import UUID

from fastapi import APIRouter, Query

from app.core.security import (
    db_dependency,
    user_dependency
)

from app.services.consultant_service import (
    get_consultant_profile,
    get_consultant_profile_by_id,
    update_consultant_profile,
    get_all_consultants,
    get_top_rated_consultants,
    update_consultant_status
)

from app.services.review_service import (
    get_reviews_for_consultant
)

from app.schemas.consultant import (
    ConsultantUpdate,
    ConsultantResponse
)

from app.schemas.review import ReviewResponse

router = APIRouter(
    prefix="/consultants",
    tags=["consultants"]
)


@router.get(
    "/",
    response_model=list[ConsultantResponse]
)
async def get_all_consultants_endpoint(
    db: db_dependency,
    user: user_dependency
):
    """Get all online consultants."""
    return await get_all_consultants(db, user)


@router.get(
    "/top-rated",
    response_model=list[ConsultantResponse]
)
async def get_top_rated_consultants_endpoint(
    db: db_dependency,
    user: user_dependency
):
    """Get top-rated online consultants."""
    return await get_top_rated_consultants(db, user)


@router.get(
    "/profile",
    response_model=ConsultantResponse
)
async def get_my_consultant_profile(
    db: db_dependency,
    user: user_dependency
):
    """Get current consultant's own profile."""
    return await get_consultant_profile(db, user)


@router.put(
    "/profile",
    response_model=ConsultantResponse
)
async def update_my_consultant_profile(
    consultant_data: ConsultantUpdate,
    db: db_dependency,
    user: user_dependency
):
    """Update consultant profile."""
    return await update_consultant_profile(db, user, consultant_data)


@router.patch("/status")
async def update_consultant_status_endpoint(
    db: db_dependency,
    user: user_dependency,
    # FIX: status value was never passed — added as a required query parameter
    consultant_status: str = Query(..., pattern="^(online|offline)$")
):
    """Toggle consultant online/offline status."""
    return await update_consultant_status(db, user, consultant_status)


# Dynamic routes below static ones to prevent shadowing /profile, /top-rated
@router.get(
    "/{consultant_id}",
    response_model=ConsultantResponse
)
async def get_consultant_profile_by_id_endpoint(
    consultant_id: UUID,
    db: db_dependency,
    user: user_dependency
):
    """Get consultant profile by ID."""
    return await get_consultant_profile_by_id(db, user, consultant_id)


@router.get(
    "/{consultant_id}/reviews",
    response_model=list[ReviewResponse]
)
async def get_consultant_reviews(
    consultant_id: UUID,
    db: db_dependency
):
    """Get all reviews for a consultant."""
    return await get_reviews_for_consultant(db, consultant_id)