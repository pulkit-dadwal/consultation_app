from fastapi import APIRouter, HTTPException, status

from app.core.security import db_dependency, user_dependency
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me")
async def get_current_user_profile(
    user: user_dependency,
    db: db_dependency
):
    db_user = (
        db.query(User)
        .filter(User.id == user["id"])
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return {
        "id": str(db_user.id),
        "name": db_user.name,
        "email": db_user.email,
        "role": db_user.role,
        "wallet_balance": db_user.wallet_balance,
    }