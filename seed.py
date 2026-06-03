import os
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

# Ensure app package imports work when running seed.py from the repository root.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT_DIR, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import User
from app.models.consultation import Consultation
from app.models.transaction import Transaction
from app.models.review import Review
from app.models.chat_message import ChatMessage


def create_schema() -> None:
    """Create all database tables for the current models."""
    Base.metadata.create_all(bind=engine)


def clear_seed_data(session) -> None:
    """Delete any existing seed data in a safe child-to-parent order."""
    session.execute(delete(ChatMessage))
    session.execute(delete(Review))
    session.execute(delete(Transaction))
    session.execute(delete(Consultation))
    session.execute(delete(User))
    session.commit()


def seed_sample_data(session) -> None:
    """Insert sample users, consultations, transactions, reviews, and chat messages."""
    alice = User(
        name="Alice Client",
        email="alice@example.com",
        hashed_password=get_password_hash("alicepassword"),
        role="client"
    )
    bob = User(
        name="Bob Consultant",
        email="bob@example.com",
        hashed_password=get_password_hash("bobpassword"),
        role="consultant"
    )
    admin = User(
        name="Admin User",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        role="admin"
    )

    session.add_all([alice, bob, admin])
    session.flush()

    consultation_confirmed = Consultation(
        client_id=alice.id,
        consultant_id=bob.id,
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
        status="confirmed",
        notes="Initial strategy consultation for a new product launch."
    )

    consultation_completed = Consultation(
        client_id=alice.id,
        consultant_id=bob.id,
        scheduled_at=datetime.now(timezone.utc) - timedelta(days=10),
        status="completed",
        notes="Completed follow-up consultation covering pricing and roadmap."
    )

    session.add_all([consultation_confirmed, consultation_completed])
    session.flush()

    transaction_paid = Transaction(
        consultation_id=consultation_completed.id,
        amount=299.99,
        currency="USD",
        status="paid",
        paid_at=datetime.now(timezone.utc) - timedelta(days=9)
    )

    review = Review(
        consultation_id=consultation_completed.id,
        rating=5,
        comment="Great session: clear recommendations and next steps."
    )

    chat_user = ChatMessage(
        user_id=alice.id,
        role="user",
        content="Hi Bob, I need help preparing a consultant brief for my startup.",
        intent="consultation_request"
    )

    chat_assistant = ChatMessage(
        user_id=bob.id,
        role="assistant",
        content="Sure Alice, let’s look at your goals and map a session agenda.",
        intent="consultation_response"
    )

    session.add_all([transaction_paid, review, chat_user, chat_assistant])
    session.commit()


def main() -> None:
    create_schema()

    session = SessionLocal()
    try:
        clear_seed_data(session)
        seed_sample_data(session)
        print("Seed data inserted successfully.")
    except Exception as exc:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()