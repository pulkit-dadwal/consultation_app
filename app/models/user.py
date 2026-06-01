import uuid

from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(120), nullable=False)

    email = Column(String, unique=True, nullable=False)

    role = Column(
        Enum("client", "consultant", "admin", name="user_roles"),
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    client_consultations = relationship(
        "Consultation",
        foreign_keys="Consultation.client_id"
    )

    consultant_consultations = relationship(
        "Consultation",
        foreign_keys="Consultation.consultant_id"
    )

    chat_messages = relationship(
        "ChatMessage",
        back_populates="user"
    )