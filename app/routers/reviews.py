from uuid import UUID

from fastapi import APIRouter, status

from app.core.security import db_dependency, user_dependency
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review_service import create_review, get_reviews_for_consultant

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_review_endpoint(
    review_data: ReviewCreate,
    db: db_dependency,
    user: user_dependency
):
    """Submit a review after a completed consultation."""
    return await create_review(db, user, review_data)


@router.get(
    "/consultant/{consultant_id}",
    response_model=list[ReviewResponse]
)
async def get_consultant_reviews_endpoint(
    consultant_id: UUID,  # FIX: was str
    db: db_dependency
):
    """Get all reviews for a consultant."""
    return await get_reviews_for_consultant(db, consultant_id)