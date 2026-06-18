from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status

from app.models.user import User
from app.models.wallet_transaction import WalletTransaction


async def add_funds_to_wallet(
    db,
    user: dict,
    amount: Decimal
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

    db_user.wallet_balance += amount

    transaction = create_wallet_transaction(
        db,
        user["id"],
        amount,
        "deposit",
        description="Wallet top-up"
    )

    db.commit()
    db.refresh(transaction)

    return transaction


def create_wallet_transaction(
    db,
    user_id: UUID,
    amount: Decimal,
    transaction_type: str,
    consultation_id: UUID = None,
    description: str = None
):
    transaction = WalletTransaction(
        user_id=user_id,
        consultation_id=consultation_id,
        amount=amount,
        transaction_type=transaction_type,
        description=description
    )

    db.add(transaction)

    return transaction