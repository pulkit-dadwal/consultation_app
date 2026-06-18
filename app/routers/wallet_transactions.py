from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.security import db_dependency, user_dependency
from app.models.wallet_transaction import WalletTransaction
from app.schemas.wallet_transaction import (
    AddFundsRequest,
    WalletTransactionResponse
)
from app.services.wallet_transaction_service import add_funds_to_wallet

router = APIRouter(
    prefix="/wallet-transactions",
    tags=["wallet-transactions"]
)


@router.post(
    "/deposit",
    response_model=WalletTransactionResponse,
    status_code=status.HTTP_201_CREATED
)
async def deposit_funds(
    funds_data: AddFundsRequest,
    db: db_dependency,
    user: user_dependency
):
    """Add funds to the current user's wallet."""
    return await add_funds_to_wallet(
        db,
        user,
        funds_data.amount
    )


@router.get(
    "/",
    response_model=list[WalletTransactionResponse]
)
async def get_my_wallet_transactions(
    db: db_dependency,
    user: user_dependency
):
    """Get all wallet transactions for the current user."""
    transactions = (
        db.query(WalletTransaction)
        .filter(WalletTransaction.user_id == user["id"])
        .order_by(WalletTransaction.created_at.desc())
        .all()
    )

    return transactions


@router.get(
    "/{transaction_id}",
    response_model=WalletTransactionResponse
)
async def get_wallet_transaction(
    transaction_id: UUID,  # FIX: was untyped
    db: db_dependency,
    user: user_dependency
):
    """Get a specific wallet transaction."""
    transaction = (
        db.query(WalletTransaction)
        .filter(
            WalletTransaction.id == transaction_id,
            WalletTransaction.user_id == user["id"]
        )
        .first()
    )

    # FIX: was returning None silently — now raises a proper 404
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found."
        )

    return transaction