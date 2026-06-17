from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConsultationStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    ongoing = "ongoing"
    completed = "completed"
    rejected = "rejected"
    expired = "expired"


class ConsultationCreate(BaseModel):
    consultant_id: UUID
    # ge=3 enforces the minimum 3-minute booking rule from the workflow
    duration_minutes: int = Field(..., ge=3)
    notes: Optional[str] = Field(None, max_length=1000)


class ConsultationExtend(BaseModel):
    # ge=3 enforces the minimum 3-minute extension rule from the workflow
    additional_minutes: int = Field(..., ge=3)


class ConsultationResponse(BaseModel):
    id: UUID
    client_id: UUID
    consultant_id: UUID
    scheduled_at: datetime
    # original_duration_minutes — the baseline set at booking, never mutated
    original_duration_minutes: int
    # duration_minutes — grows on each extension
    duration_minutes: int
    total_amount: Decimal
    status: ConsultationStatus
    notes: Optional[str]
    # request_expires_at — deadline for consultant to accept (created_at + 2 min)
    request_expires_at: datetime
    # started_at / ended_at — drive the frontend chat window timer
    started_at: Optional[datetime]
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True