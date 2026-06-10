import uuid

from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base


class Consultant(Base):
	__tablename__ = "consultants"

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

	user_id = Column(
		UUID(as_uuid=True),
		ForeignKey("users.id"),
		nullable=False,
		unique=True
	)

	specialization = Column(String(255), nullable=True)

	consultation_fee = Column(Float, nullable=True)

	status = Column(
		Enum("online", "offline", name="consultant_status"),
		nullable=False,
		default="online"
	)

	rating = Column(Float, default=4.0)

	created_at = Column(DateTime, default=datetime.now(timezone.utc))

	updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

	user = relationship(
		"User",
		back_populates="consultant_profile"
	)
