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

    # The duration the client originally booked (never mutated after creation).
    # Use this as the audit baseline for refund or dispute calculations.
    original_duration_minutes = Column(
        Integer,
        nullable=False
    )

    # Current total duration in minutes. Increases when the client extends the
    # session. Starts equal to original_duration_minutes at booking time.
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
            "pending",      # Request sent, waiting for consultant to respond
            "accepted",     # Consultant accepted, fee deducted, chat not yet started
            "ongoing",      # Chat window is open
            "completed",    # Session ended normally
            "rejected",     # Consultant rejected the request
            "expired",      # Consultant did not respond within 2 minutes
            name="consultation_status"
        ),
        nullable=False,
        default="pending"
    )

    notes = Column(Text)

    # Deadline by which the consultant must accept or reject. Set to
    # created_at + 2 minutes at booking time. A background task checks this
    # and marks the consultation "expired" if the consultant does not respond.
    request_expires_at = Column(
        DateTime,
        nullable=False
    )

    # Set when the consultant accepts and the chat window opens (status →
    # "ongoing"). This is the reference point for the session countdown timer
    # and the 3-minute warning popup on the frontend.
    started_at = Column(
        DateTime,
        nullable=True
    )

    # Set when the session closes — either because the timer ran out or both
    # parties left. Useful for analytics and dispute resolution.
    ended_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # --- Relationships ---

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