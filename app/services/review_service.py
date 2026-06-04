from fastapi import HTTPException, status
from app.models.review import Review
from app.models.consultation import Consultation
from app.schemas.review import ReviewCreate
from app.core.security import db_dependency, user_dependency


async def create_review(db: db_dependency, user: user_dependency, review_data: ReviewCreate):
    """Create a review for a completed consultation."""
    consultation = db.query(Consultation).filter(Consultation.id == review_data.consultation_id).first()

    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Consultation not found.')

    if user.get('id') != consultation.client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only the consultation client may submit a review.')

    if consultation.status != 'completed':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Reviews can only be submitted for completed consultations.')

    existing_review = db.query(Review).filter(Review.consultation_id == review_data.consultation_id).first()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='A review for this consultation already exists.')

    review = Review(
        consultation_id=review_data.consultation_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )

    db.add(review)
    db.commit()
    db.refresh(review)
    return review


async def get_reviews_for_consultant(db: db_dependency, consultant_id):
    """Return all reviews for the given consultant."""
    return db.query(Review).join(Consultation).filter(Consultation.consultant_id == consultant_id).all()
