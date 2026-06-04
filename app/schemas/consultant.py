from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ConsultantCreate(BaseModel):
    specialization: Optional[str] = Field(None, max_length=255)
    consultation_fee: Optional[float] = Field(None, gt=0)


class ConsultantUpdate(BaseModel):
    specialization: Optional[str] = Field(None, max_length=255)
    consultation_fee: Optional[float] = Field(None, gt=0)


class ConsultantResponse(BaseModel):
    id: UUID
    user_id: UUID
    specialization: Optional[str]
    consultation_fee: Optional[float]
    rating: float = 0.0
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
