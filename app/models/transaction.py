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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id"),
        nullable=False
    )

    amount = Column(Numeric(10, 2), nullable=False)

    currency = Column(String(3), default="USD")

    status = Column(
        Enum(
            "pending",
            "paid",
            "refunded",
            name="payment_status"
        ),
        nullable=False
    )

    paid_at = Column(DateTime)

    consultation = relationship(
        "Consultation",
        back_populates="transaction"
    )