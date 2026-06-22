from uuid import UUID

from fastapi import HTTPException, status

from app.models.consultant import Consultant
from app.models.user import User
from app.schemas.consultant import ConsultantUpdate
from app.core.security import db_dependency, user_dependency


async def get_all_consultants(db: db_dependency):
    """Get all online consultants (public)."""

    consultants = (
        db.query(Consultant)
        .filter(Consultant.status == "online")
        .all()
    )

    return consultants


async def get_top_rated_consultants(db: db_dependency):
    """Get top-rated online consultants (public)."""

    consultants = (
        db.query(Consultant)
        .filter(
            Consultant.status == "online",
            Consultant.rating >= 4.0
        )
        .all()
    )

    return consultants


async def get_consultant_profile_by_id(
    db: db_dependency,
    consultant_id: UUID  # FIX: was int — model uses UUID primary key
):
    """Get consultant profile by id."""

    consultant = (
        db.query(Consultant)
        .filter(Consultant.id == consultant_id)
        .first()
    )

    if not consultant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant profile not found."
        )

    return consultant


async def get_consultant_profile(
    db: db_dependency,
    user: user_dependency
):
    """Get authenticated consultant's own profile."""

    user_id = user.get("id")

    db_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if db_user.role != "consultant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a consultant."
        )

    consultant = (
        db.query(Consultant)
        .filter(Consultant.user_id == user_id)
        .first()
    )

    if not consultant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant profile not found."
        )

    return consultant


async def update_consultant_profile(
    db: db_dependency,
    user: user_dependency,
    consultant_data: ConsultantUpdate
):
    """Update consultant profile."""

    user_id = user.get("id")

    db_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if db_user.role != "consultant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a consultant."
        )

    consultant = (
        db.query(Consultant)
        .filter(Consultant.user_id == user_id)
        .first()
    )

    if not consultant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant profile not found."
        )

    update_data = consultant_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(consultant, key, value)

    db.add(consultant)
    db.commit()
    db.refresh(consultant)

    return consultant


async def update_consultant_status(
    db: db_dependency,
    user: user_dependency,
    consultant_status: str
):
    """Toggle consultant online/offline status."""

    # FIX: role check was missing — any authenticated user could call this
    if user.get("user_role") != "consultant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can update their status."
        )

    if consultant_status not in ["online", "offline"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid consultant status."
        )

    consultant = (
        db.query(Consultant)
        .filter(Consultant.user_id == user.get("id"))
        .first()
    )

    if not consultant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant profile not found."
        )

    consultant.status = consultant_status

    db.commit()
    db.refresh(consultant)

    return consultant