import uuid

from sqlalchemy import Column, Numeric, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base


class Consultant(Base):
    __tablename__ = "consultants"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    specialization = Column(
        String(255),
        nullable=True
    )

    consultation_fee_per_minute = Column(
        Numeric(10, 2),
        nullable=False
    )

    status = Column(
        Enum(
            "online",
            "offline",
            name="consultant_status"
        ),
        nullable=False,
        default="offline",
        index=True
    )

    rating = Column(
        Float,
        default=4.0
    )

    # FIX: was default=datetime.now(timezone.utc) — evaluated once at import
    # time, so all rows would share the same timestamp. lambda: ensures each
    # row gets the current time at INSERT.
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---

    user = relationship(
        "User",
        back_populates="consultant_profile"
    )

    consultations = relationship(
        "Consultation",
        back_populates="consultant"
    )

    @property
    def name(self):
        return self.user.name if self.user else None