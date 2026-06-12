from decimal import Decimal

from app.models.wallet_transaction import WalletTransaction


def create_wallet_transaction(
    db,
    user_id,
    amount: Decimal,
    transaction_type: str,
    description: str = None
):
    transaction = WalletTransaction(
        user_id=user_id,
        amount=amount,
        transaction_type=transaction_type,
        description=description
    )

    db.add(transaction)

    return transaction