import uuid

from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    Enum,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # One transaction record per consultation
    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id"),
        nullable=False
    )

    amount = Column(Numeric(10, 2), nullable=False)

    currency = Column(String(3), default="INR")

    status = Column(
        Enum(
            "pending",   # Wallet balance checked but not yet deducted
            "paid",      # Fee deducted after consultant acceptance
            "refunded",  # Refunded if session expired or was rejected
            name="payment_status"
        ),
        default="pending",
        nullable=False
    )

    paid_at = Column(DateTime)

    # --- Relationships ---

    consultation = relationship(
        "Consultation",
        back_populates="transaction"
    )