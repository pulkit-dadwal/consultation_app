import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Numeric,
    DateTime,
    ForeignKey,
    Enum,
    Text
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Nullable — not all wallet movements are tied to a consultation (e.g.
    # a top-up deposit has no consultation_id)
    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id"),
        nullable=True,
        index=True
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    transaction_type = Column(
        Enum(
            "deposit",   # Client adds funds to wallet
            "paid",      # Fee deducted from client wallet on session acceptance
            "refund",    # Funds returned to client (rejected / expired session)
            "received",  # Earnings credited to consultant wallet
            name="wallet_transaction_type"
        ),
        nullable=False
    )

    description = Column(Text)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # --- Relationships ---

    user = relationship(
        "User",
        back_populates="wallet_transactions"
    )

    consultation = relationship(
        "Consultation",
        back_populates="wallet_transactions"
    )