from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConsultationCreate(BaseModel):
    consultant_id: UUID
    notes: Optional[str] = Field(None, max_length=1000)


class ConsultationResponse(BaseModel):
    id: UUID
    client_id: UUID
    consultant_id: UUID
    scheduled_at: datetime
    status: str
    notes: Optional[str]

    class Config:
        from_attributes = True
