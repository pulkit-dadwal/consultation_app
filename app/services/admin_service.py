from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload

from app.core.security import db_dependency, user_dependency
from app.models.consultant import Consultant
from app.models.consultant_request import ConsultantRequest
from app.models.user import User
from app.schemas.admin import ConsultantRequestReview


def serialize_admin_consultant_request(
    consultant_request: ConsultantRequest
) -> dict:
    return {
        "id": consultant_request.id,
        "user_id": consultant_request.user_id,
        "status": consultant_request.status,
        "linkedin_url": consultant_request.linkedin_url,
        "resume_url": consultant_request.resume_url,
        "portfolio_url": consultant_request.portfolio_url,
        "notes": consultant_request.notes,
        "rejection_reason": consultant_request.rejection_reason,
        "applied_at": consultant_request.applied_at,
        "reviewed_at": consultant_request.reviewed_at,
        "cooldown_until": consultant_request.cooldown_until,
        "applicant_name": consultant_request.user.name,
        "applicant_email": consultant_request.user.email,
    }


async def get_all_consultant_requests(
    db: db_dependency,
    user: user_dependency
):
    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view consultant requests."
        )

    requests = (
        db.query(ConsultantRequest)
        .options(joinedload(ConsultantRequest.user))
        .order_by(ConsultantRequest.applied_at.desc())
        .all()
    )

    return [
        serialize_admin_consultant_request(request)
        for request in requests
    ]


async def get_consultant_request_for_admin(
    db: db_dependency,
    user: user_dependency,
    request_id
):
    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view consultant requests."
        )

    consultant_request = (
        db.query(ConsultantRequest)
        .options(joinedload(ConsultantRequest.user))
        .filter(ConsultantRequest.id == request_id)
        .first()
    )

    if not consultant_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant request not found."
        )

    return serialize_admin_consultant_request(consultant_request)


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
        .filter(ConsultantRequest.id == request_id)
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
        .filter(User.id == consultant_request.user_id)
        .first()
    )

    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    consultant_request.reviewed_at = datetime.now(timezone.utc)

    if review_data.status == "approved":

        consultant_request.status = "approved"
        applicant.role = "consultant"

        # Guard against double-approval creating a duplicate profile.
        existing_profile = (
            db.query(Consultant)
            .filter(Consultant.user_id == applicant.id)
            .first()
        )

        if not existing_profile:
            # consultation_fee_per_minute starts at 0 — the consultant must
            # update their profile before going online. This avoids a NOT NULL
            # violation while still flagging unconfigured consultants via the
            # fee check in create_consultation.
            consultant_profile = Consultant(
                user_id=applicant.id,
                specialization=None,
                consultation_fee_per_minute=0,
                status="offline"
            )
            db.add(consultant_profile)

    else:

        consultant_request.status = "rejected"
        consultant_request.rejection_reason = review_data.rejection_reason
        consultant_request.cooldown_until = (
            datetime.now(timezone.utc) + timedelta(days=30)
        )

    db.commit()

    return {
        "message": (
            f"Consultant request "
            f"{consultant_request.status} successfully."
        )
    }