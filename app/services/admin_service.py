from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.core.security import db_dependency, user_dependency
from app.models.consultant import Consultant
from app.models.consultant_request import ConsultantRequest
from app.models.user import User
from app.schemas.admin import ConsultantRequestReview


async def get_all_consultant_requests(
    db: db_dependency,
    user: user_dependency
):
    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view consultant requests."
        )

    return (
        db.query(ConsultantRequest)
        .order_by(ConsultantRequest.applied_at.desc())
        .all()
    )


async def review_consultant_request(
    request_id,
    review_data: ConsultantRequestReview,
    db: db_dependency,
    user: user_dependency
):
    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can review consultant requests."
        )

    consultant_request = (
        db.query(ConsultantRequest)
        .filter(
            ConsultantRequest.id == request_id
        )
        .first()
    )

    if not consultant_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant request not found."
        )

    if consultant_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This request has already been reviewed."
        )

    applicant = (
        db.query(User)
        .filter(
            User.id == consultant_request.user_id
        )
        .first()
    )

    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    consultant_request.reviewed_at = datetime.now(
        timezone.utc
    )

    if review_data.status == "approved":

        consultant_request.status = "approved"

        applicant.role = "consultant"

        consultant_profile = Consultant(
            user_id=applicant.id,
            specialization=None,
            consultation_fee_per_minute=None,
            status="offline"
        )

        db.add(consultant_profile)

    else:

        consultant_request.status = "rejected"

        consultant_request.rejection_reason = (
            review_data.rejection_reason
        )

        consultant_request.cooldown_until = (
            datetime.now(timezone.utc)
            + timedelta(days=30)
        )

    db.commit()

    return {
        "message": (
            f"Consultant request "
            f"{consultant_request.status} successfully."
        )
    }