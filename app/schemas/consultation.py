from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ConsultationCreate(BaseModel):
    consultant_id: UUID
    duration_minutes: int = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=1000)


class ConsultationExtend(BaseModel):
    additional_minutes: int = Field(..., gt=0)


class ConsultationResponse(BaseModel):
    id: UUID
    client_id: UUID
    consultant_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    total_amount: Decimal
    status: str
    notes: Optional[str]

    class Config:
        from_attributes = True