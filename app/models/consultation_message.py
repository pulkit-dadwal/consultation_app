import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Enum,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ConsultationMessage(Base):
    __tablename__ = "consultation_messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id"),
        nullable=False,
        index=True
    )

    sender_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    message_type = Column(
        Enum(
            "chat",               # Regular chat message
            "extension_request",  # Client requesting to extend the session
            "system",             # System-generated (e.g. "Session ends in 3 minutes")
            name="consultation_message_type"
        ),
        nullable=False,
        default="chat"
    )

    sent_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # --- Relationships ---

    consultation = relationship(
        "Consultation",
        back_populates="messages"
    )

    # back_populates added to match User.consultation_messages
    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="consultation_messages"
    )