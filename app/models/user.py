import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Enum,
    String,
    DateTime,
    Numeric
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(120),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password = Column(
        String,
        nullable=False
    )

    role = Column(
        Enum(
            "client",
            "consultant",
            "admin",
            name="user_role"
        ),
        nullable=False,
        default="client"
    )

    wallet_balance = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---

    consultant_profile = relationship(
        "Consultant",
        back_populates="user",
        uselist=False
    )

    # Consultations where this user is the client
    consultations = relationship(
        "Consultation",
        back_populates="client"
    )

    wallet_transactions = relationship(
        "WalletTransaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Messages sent by this user inside consultation sessions
    consultation_messages = relationship(
        "ConsultationMessage",
        foreign_keys="ConsultationMessage.sender_id",
        back_populates="sender"
    )

    consultant_requests = relationship(
        "ConsultantRequest",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # AI chatbot conversation history for this user
    chat_messages = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan"
    )