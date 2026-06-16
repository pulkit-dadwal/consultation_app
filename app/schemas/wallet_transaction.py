from enum import Enum
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field


class WalletTransactionType(str, Enum):
    deposit = "deposit"
    paid = "paid"
    refund = "refund"
    received = "received"


class WalletTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    consultation_id: UUID | None = None
    amount: Decimal
    transaction_type: WalletTransactionType
    description: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class AddFundsRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)