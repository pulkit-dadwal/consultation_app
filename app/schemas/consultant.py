from decimal import Decimal
from enum import Enum
from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ConsultantStatus(str, Enum):
    online = "online"
    offline = "offline"


class ConsultantUpdate(BaseModel):
    specialization: Optional[str] = Field(None, max_length=255)
    # Decimal instead of float to avoid floating point precision errors on fees
    consultation_fee_per_minute: Optional[Decimal] = Field(None, gt=0)


class ConsultantResponse(BaseModel):
    id: UUID
    user_id: UUID
    specialization: Optional[str]
    # Decimal matches the Numeric(10, 2) column; proper enum for status
    consultation_fee_per_minute: Optional[Decimal]
    status: ConsultantStatus
    rating: float
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True