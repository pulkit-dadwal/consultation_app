import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
    Enum
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    client_id = Column(
    UUID(as_uuid=True),
    ForeignKey("users.id"),
    nullable=False,
    index=True
    )

    consultant_id = Column(
    UUID(as_uuid=True),
    ForeignKey("consultants.id"),
    nullable=False,
    index=True
    )

    scheduled_at = Column(
        DateTime,
        nullable=False
    )

    duration_minutes = Column(
        Integer,
        nullable=False
    )

    total_amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    status = Column(
        Enum(
            "pending",
            "accepted",
            "ongoing",
            "completed",
            "rejected",
            "expired",
            name="consultation_status"
        ),
        nullable=False,
        default="pending"
    )

    notes = Column(Text)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    client = relationship(
        "User",
        back_populates="consultations"
    )

    consultant = relationship(
        "Consultant",
        back_populates="consultations"
    )

    messages = relationship(
        "ConsultationMessage",
        back_populates="consultation",
        cascade="all, delete-orphan"
    )

    wallet_transactions = relationship(
        "WalletTransaction",
        back_populates="consultation"
    )

    review = relationship(
    "Review",
    back_populates="consultation",
    uselist=False,
    cascade="all, delete-orphan"
    )

    transaction = relationship(
    "Transaction",
    back_populates="consultation",
    uselist=False,
    cascade="all, delete-orphan"
)