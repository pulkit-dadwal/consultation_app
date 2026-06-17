from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.security import db_dependency, user_dependency
from app.models.transaction import Transaction

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


@router.get("/")
async def get_all_transactions(
    db: db_dependency,
    user: user_dependency
):
    """Admin can view all payment transaction records."""

    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all transactions."
        )

    transactions = (
        db.query(Transaction)
        .order_by(Transaction.paid_at.desc())
        .all()
    )

    return transactions


@router.get("/{transaction_id}")
async def get_transaction_by_id(
    transaction_id: UUID,
    db: db_dependency,
    user: user_dependency
):
    """Admin can view a specific payment transaction record."""

    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view transactions."
        )

    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found."
        )

    return transaction