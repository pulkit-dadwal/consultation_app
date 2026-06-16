from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status

from app.models.user import User
from app.models.consultant import Consultant
from app.models.consultant_request import ConsultantRequest

from app.schemas.consultant_request import (
    ConsultantRequestCreate,
    ConsultantRequestReview
)

from app.core.security import (
    db_dependency,
    user_dependency
)


async def create_consultant_request(
    db: db_dependency,
    user: user_dependency,
    request_data: ConsultantRequestCreate
):
    """Client submits a consultant application."""

    if user.get("user_role") != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can apply to become consultants."
        )

    existing_pending_request = (
        db.query(ConsultantRequest)
        .filter(
            ConsultantRequest.user_id == user.get("id"),
            ConsultantRequest.status == "pending"
        )
        .first()
    )

    if existing_pending_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending consultant request."
        )

    latest_request = (
        db.query(ConsultantRequest)
        .filter(
            ConsultantRequest.user_id == user.get("id")
        )
        .order_by(
            ConsultantRequest.applied_at.desc()
        )
        .first()
    )

    if (
        latest_request
        and latest_request.status == "rejected"
        and latest_request.cooldown_until
        and latest_request.cooldown_until > datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot apply again until the cooldown period ends."
        )

    consultant_request = ConsultantRequest(
        user_id=user.get("id"),
        linkedin_url=request_data.linkedin_url,
        resume_url=request_data.resume_url,
        portfolio_url=request_data.portfolio_url,
        notes=request_data.notes,
        status="pending"
    )

    db.add(consultant_request)

    db.commit()

    db.refresh(consultant_request)

    return consultant_request


async def get_my_consultant_requests(
    db: db_dependency,
    user: user_dependency
):
    """Get all consultant requests submitted by the current user."""

    requests = (
        db.query(ConsultantRequest)
        .filter(
            ConsultantRequest.user_id == user.get("id")
        )
        .order_by(
            ConsultantRequest.applied_at.desc()
        )
        .all()
    )

    return requests


async def get_consultant_request_by_id(
    db: db_dependency,
    user: user_dependency,
    request_id
):
    """Get a specific consultant request."""

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

    if (
        user.get("user_role") != "admin"
        and consultant_request.user_id != user.get("id")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this request."
        )

    return consultant_request


async def get_all_consultant_requests(
    db: db_dependency,
    user: user_dependency
):
    """Admin can view all consultant requests."""

    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view consultant requests."
        )

    requests = (
        db.query(ConsultantRequest)
        .order_by(
            ConsultantRequest.applied_at.desc()
        )
        .all()
    )

    return requests


async def review_consultant_request(
    db: db_dependency,
    user: user_dependency,
    request_id,
    review_data: ConsultantRequestReview
):
    """Admin approves or rejects consultant request."""

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

    request_user = (
        db.query(User)
        .filter(
            User.id == consultant_request.user_id
        )
        .first()
    )

    if not request_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if review_data.status == "approved":
        request_user.role = "consultant"

        existing_profile = (db.query(Consultant).filter(Consultant.user_id == request_user.id).first())

        if not existing_profile:
            consultant_profile = Consultant(
                user_id=request_user.id,
                specialization=None,
                consultation_fee_per_minute=None,
                status="offline"
            )

            db.add(consultant_profile)

        consultant_request.status = "approved"

    elif review_data.status == "rejected":

        consultant_request.status = "rejected"

        consultant_request.rejection_reason = (
            review_data.rejection_reason
        )

        consultant_request.cooldown_until = (
            datetime.now(timezone.utc)
            + timedelta(days=30)
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either approved or rejected."
        )

    consultant_request.reviewed_at = (
        datetime.now(timezone.utc)
    )

    db.commit()

    db.refresh(consultant_request)

    return consultant_request