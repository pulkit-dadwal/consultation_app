import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    # "user" = message from the client, "assistant" = response from the AI
    role = Column(
        Enum("user", "assistant", name="message_role"),
        nullable=False
    )

    content = Column(Text, nullable=False)

    # Optional classifier tag (e.g. "booking_query", "pricing", "support")
    # populated by the chatbot service to route or analyse conversations
    intent = Column(String(80))

    # FIX: was default=datetime.now(timezone.utc) — evaluated once at import
    # time, so all rows would share the same timestamp. lambda: ensures each
    # row gets the current time at INSERT.
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---

    user = relationship(
        "User",
        back_populates="chat_messages"
    )