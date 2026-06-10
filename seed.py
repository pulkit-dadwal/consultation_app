import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

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
from app.models.consultant import Consultant
from app.models.wallet import Wallet
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
    session.execute(delete(Wallet))
    session.execute(delete(Consultant))
    session.execute(delete(User))
    session.commit()


def seed_sample_data(session) -> None:
    """Insert sample users, wallets, consultant profiles, consultations, and reviews."""
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

    session.add_all([
        Wallet(user_id=alice.id, balance=Decimal("500.00")),
        Wallet(user_id=bob.id, balance=Decimal("0.00")),
        Wallet(user_id=admin.id, balance=Decimal("0.00")),
    ])

    bob_profile = Consultant(
        user_id=bob.id,
        specialization="Business Strategy",
        consultation_fee=150.0,
        status="online",
        rating=4.5
    )
    session.add(bob_profile)
    session.flush()

    consultation_confirmed = Consultation(
        client_id=alice.id,
        consultant_id=bob.id,
        scheduled_at=datetime.now(timezone.utc),
        status="confirmed",
        notes="Immediate strategy consultation booked via wallet payment."
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
        amount=Decimal("150.00"),
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
        content="Sure Alice, let's look at your goals and map a session agenda.",
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
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
