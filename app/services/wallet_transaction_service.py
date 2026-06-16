from decimal import Decimal
from uuid import UUID

from app.models.wallet_transaction import WalletTransaction


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