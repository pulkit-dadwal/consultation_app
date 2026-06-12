from enum import Enum
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field



class WalletTransactionType(str, Enum):
    deposit = "deposit"
    consultation_charge = "consultation_charge"
    consultation_refund = "consultation_refund"
    consultant_payout = "consultant_payout"
    adjustment = "adjustment"




class WalletTransactionResponse(BaseModel):
    id: UUID
    amount: Decimal
    transaction_type: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True




class AddFundsRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)