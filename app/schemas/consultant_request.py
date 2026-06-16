from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConsultantRequestCreate(BaseModel):
    linkedin_url: Optional[str] = Field(None, max_length=500)
    resume_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class ConsultantRequestReview(BaseModel):
    status: str
    rejection_reason: Optional[str] = None


class ConsultantRequestResponse(BaseModel):
    id: UUID
    user_id: UUID

    status: str

    linkedin_url: Optional[str]
    resume_url: Optional[str]
    portfolio_url: Optional[str]

    notes: Optional[str]

    rejection_reason: Optional[str]

    applied_at: datetime

    reviewed_at: Optional[datetime]

    cooldown_until: Optional[datetime]

    class Config:
        from_attributes = True