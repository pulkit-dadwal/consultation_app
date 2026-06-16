import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Text,
    Enum
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ConsultantRequest(Base):
    __tablename__ = "consultant_requests"

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

    status = Column(
        Enum(
            "pending",
            "approved",
            "rejected",
            name="consultant_request_status"
        ),
        nullable=False,
        default="pending"
    )

    linkedin_url = Column(
        String(500)
    )

    resume_url = Column(
        String(500)
    )

    portfolio_url = Column(
        String(500)
    )

    notes = Column(
        Text
    )

    rejection_reason = Column(
        Text
    )

    applied_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    reviewed_at = Column(
        DateTime
    )

    cooldown_until = Column(
        DateTime
    )

    user = relationship(
        "User",
        back_populates="consultant_requests"
    )