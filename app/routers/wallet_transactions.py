from fastapi import APIRouter

from app.core.security import db_dependency, user_dependency

from app.models.wallet_transaction import WalletTransaction

router = APIRouter(
    prefix="/wallet-transactions",
    tags=["wallet-transactions"]
)



@router.get("/")
async def get_my_wallet_transactions(
    db: db_dependency,
    user: user_dependency
):
    transactions = (
        db.query(WalletTransaction)
        .filter(
            WalletTransaction.user_id == user["id"]
        )
        .order_by(
            WalletTransaction.created_at.desc()
        )
        .all()
    )

    return transactions



@router.get("/{transaction_id}")
async def get_wallet_transaction(
    transaction_id,
    db: db_dependency,
    user: user_dependency
):
    transaction = (
        db.query(WalletTransaction)
        .filter(
            WalletTransaction.id == transaction_id,
            WalletTransaction.user_id == user["id"]
        )
        .first()
    )

    return transaction