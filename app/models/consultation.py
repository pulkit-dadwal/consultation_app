import uuid

from sqlalchemy import Column, DateTime, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    consultant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    scheduled_at = Column(DateTime, nullable=False)

    status = Column(
        Enum(
            "pending",
            "confirmed",
            "completed",
            "cancelled",
            name="consultation_status"
        ),
        nullable=False
    )

    notes = Column(Text)

    client = relationship(
        "User",
        foreign_keys=[client_id],
        back_populates="client_consultations"
    )

    consultant = relationship(
        "User",
        foreign_keys=[consultant_id],
        back_populates="consultant_consultations"
    )

    transaction = relationship(
        "Transaction",
        back_populates="consultation",
        uselist=False
    )

    review = relationship(
        "Review",
        back_populates="consultation",
        uselist=False
    )