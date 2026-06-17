from enum import Enum
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    chat = "chat"
    extension_request = "extension_request"
    system = "system"


class ConsultationMessageCreate(BaseModel):
    consultation_id: UUID
    content: str = Field(..., min_length=1, max_length=5000)


class ConsultationMessageResponse(BaseModel):
    id: UUID
    consultation_id: UUID
    sender_id: UUID
    content: str
    # message_type tells the frontend how to render each message:
    # "chat" = bubble, "extension_request" = action widget, "system" = notice bar
    message_type: MessageType
    sent_at: datetime

    class Config:
        from_attributes = True