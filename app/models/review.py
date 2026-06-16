import uuid

from sqlalchemy import (
    Column,
    SmallInteger,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id"),
        unique=True,
        nullable=False
    )

    rating = Column(SmallInteger, nullable=False)

    comment = Column(Text)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    consultation = relationship(
        "Consultation",
        back_populates="review"
    )