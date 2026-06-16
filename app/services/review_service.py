from fastapi import HTTPException, status
from sqlalchemy import func

from app.models.review import Review
from app.models.consultation import Consultation
from app.models.consultant import Consultant

from app.schemas.review import ReviewCreate

from app.core.security import (
    db_dependency,
    user_dependency
)


async def create_review(
    db: db_dependency,
    user: user_dependency,
    review_data: ReviewCreate
):
    """Create a review for a completed consultation."""

    consultation = (
        db.query(Consultation)
        .filter(
            Consultation.id == review_data.consultation_id
        )
        .first()
    )

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found."
        )

    if consultation.client_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the client can submit a review."
        )

    if consultation.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation must be completed before reviewing."
        )

    existing_review = (
        db.query(Review)
        .filter(
            Review.consultation_id == review_data.consultation_id
        )
        .first()
    )

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Review already exists."
        )

    review = Review(
        consultation_id=review_data.consultation_id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(review)
    db.flush()

    average_rating = (
        db.query(
            func.avg(Review.rating)
        )
        .join(
            Consultation,
            Review.consultation_id == Consultation.id
        )
        .filter(
            Consultation.consultant_id == consultation.consultant_id
        )
        .scalar()
    )

    consultant = (
        db.query(Consultant)
        .filter(
            Consultant.id == consultation.consultant_id
        )
        .first()
    )

    consultant.rating = float(average_rating)

    db.commit()

    db.refresh(review)

    return review


async def get_reviews_for_consultant(
    db: db_dependency,
    consultant_id
):
    """Get all reviews for a consultant."""

    consultant = (
        db.query(Consultant)
        .filter(
            Consultant.id == consultant_id
        )
        .first()
    )

    if not consultant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant not found."
        )

    reviews = (
        db.query(Review)
        .join(
            Consultation,
            Review.consultation_id == Consultation.id
        )
        .filter(
            Consultation.consultant_id == consultant_id
        )
        .all()
    )

    return reviews