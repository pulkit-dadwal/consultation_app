import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import delete

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import User
from app.models.consultant import Consultant
from app.models.consultant_request import ConsultantRequest
from app.models.consultation import Consultation
from app.models.consultation_message import ConsultationMessage
from app.models.transaction import Transaction
from app.models.wallet_transaction import WalletTransaction
from app.models.review import Review
from app.models.chat_message import ChatMessage


def create_schema() -> None:
    """Create all database tables for the current models."""
    Base.metadata.create_all(bind=engine)


def clear_seed_data(session) -> None:
    """Delete existing seed data in child-to-parent order to respect FK constraints."""
    session.execute(delete(ChatMessage))
    session.execute(delete(Review))
    session.execute(delete(WalletTransaction))
    session.execute(delete(Transaction))
    session.execute(delete(ConsultationMessage))
    session.execute(delete(Consultation))
    session.execute(delete(ConsultantRequest))
    session.execute(delete(Consultant))
    session.execute(delete(User))
    session.commit()


def seed_sample_data(session) -> None:
    """Insert sample users, consultants, consultations, messages, and reviews."""

    # --- Users ---
    alice = User(
        name="Alice Client",
        email="alice@example.com",
        hashed_password=get_password_hash("alicepassword"),
        role="client",
        wallet_balance=Decimal("500.00")
    )
    bob = User(
        name="Bob Consultant",
        email="bob@example.com",
        hashed_password=get_password_hash("bobpassword"),
        role="consultant",
        wallet_balance=Decimal("0.00")
    )
    admin = User(
        name="Admin User",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        role="admin",
        wallet_balance=Decimal("0.00")
    )

    session.add_all([alice, bob, admin])
    session.flush()

    # --- Consultant profile for Bob ---
    bob_profile = Consultant(
        user_id=bob.id,
        specialization="Business Strategy",
        consultation_fee_per_minute=Decimal("2.50"),
        status="online",
        rating=4.5
    )
    session.add(bob_profile)
    session.flush()

    # --- Consultant request (approved — the record that led to Bob's promotion) ---
    approved_request = ConsultantRequest(
        user_id=bob.id,
        status="approved",
        linkedin_url="https://linkedin.com/in/bobconsultant",
        resume_url="https://example.com/bob_resume.pdf",
        notes="5 years of business strategy consulting experience.",
        applied_at=datetime.now(timezone.utc) - timedelta(days=60),
        reviewed_at=datetime.now(timezone.utc) - timedelta(days=58),
    )
    session.add(approved_request)
    session.flush()

    # --- Completed consultation (10 days ago, 30 min session) ---
    started_at_completed = datetime.now(timezone.utc) - timedelta(days=10)
    duration_completed = 30
    amount_completed = bob_profile.consultation_fee_per_minute * duration_completed

    consultation_completed = Consultation(
        client_id=alice.id,
        consultant_id=bob_profile.id,
        scheduled_at=started_at_completed,
        original_duration_minutes=duration_completed,
        duration_minutes=duration_completed,
        total_amount=amount_completed,
        status="completed",
        notes="Completed strategy session covering pricing and roadmap.",
        request_expires_at=started_at_completed + timedelta(minutes=2),
        started_at=started_at_completed + timedelta(seconds=45),
        ended_at=started_at_completed + timedelta(minutes=duration_completed, seconds=45),
    )
    session.add(consultation_completed)
    session.flush()

    # Wallet transactions for the completed consultation
    session.add_all([
        WalletTransaction(
            user_id=alice.id,
            consultation_id=consultation_completed.id,
            amount=amount_completed,
            transaction_type="paid",
            description="Consultation payment"
        ),
        WalletTransaction(
            user_id=bob.id,
            consultation_id=consultation_completed.id,
            amount=amount_completed,
            transaction_type="received",
            description="Consultation payment received"
        ),
    ])

    # Transaction (payment audit record)
    session.add(
        Transaction(
            consultation_id=consultation_completed.id,
            amount=amount_completed,
            currency="INR",
            status="paid",
            paid_at=started_at_completed + timedelta(seconds=45)
        )
    )

    # Chat messages for the completed consultation
    session.add_all([
        ConsultationMessage(
            consultation_id=consultation_completed.id,
            sender_id=alice.id,
            content="Hi Bob, I need help preparing a strategy brief for my startup.",
            message_type="chat",
            sent_at=started_at_completed + timedelta(minutes=1)
        ),
        ConsultationMessage(
            consultation_id=consultation_completed.id,
            sender_id=bob.id,
            content="Sure Alice, let's map out your goals and build a session agenda.",
            message_type="chat",
            sent_at=started_at_completed + timedelta(minutes=2)
        ),
    ])

    # Review for the completed consultation
    session.add(
        Review(
            consultation_id=consultation_completed.id,
            rating=5,
            comment="Great session — clear recommendations and actionable next steps."
        )
    )

    # --- Ongoing consultation (started 5 minutes ago, 15 min session) ---
    started_at_ongoing = datetime.now(timezone.utc) - timedelta(minutes=5)
    duration_ongoing = 15
    amount_ongoing = bob_profile.consultation_fee_per_minute * duration_ongoing

    consultation_ongoing = Consultation(
        client_id=alice.id,
        consultant_id=bob_profile.id,
        scheduled_at=started_at_ongoing,
        original_duration_minutes=duration_ongoing,
        duration_minutes=duration_ongoing,
        total_amount=amount_ongoing,
        status="ongoing",
        notes="Quick follow-up on pricing strategy.",
        request_expires_at=started_at_ongoing + timedelta(minutes=2),
        started_at=started_at_ongoing + timedelta(seconds=30),
    )
    session.add(consultation_ongoing)
    session.flush()

    session.add_all([
        WalletTransaction(
            user_id=alice.id,
            consultation_id=consultation_ongoing.id,
            amount=amount_ongoing,
            transaction_type="paid",
            description="Consultation payment"
        ),
        WalletTransaction(
            user_id=bob.id,
            consultation_id=consultation_ongoing.id,
            amount=amount_ongoing,
            transaction_type="received",
            description="Consultation payment received"
        ),
        Transaction(
            consultation_id=consultation_ongoing.id,
            amount=amount_ongoing,
            currency="INR",
            status="paid",
            paid_at=started_at_ongoing + timedelta(seconds=30)
        ),
        ConsultationMessage(
            consultation_id=consultation_ongoing.id,
            sender_id=alice.id,
            content="Bob, should we revisit the pricing model we discussed last time?",
            message_type="chat",
            sent_at=started_at_ongoing + timedelta(minutes=1)
        ),
    ])

    # --- Pending consultation (just created, waiting for Bob to accept) ---
    now = datetime.now(timezone.utc)
    duration_pending = 10
    amount_pending = bob_profile.consultation_fee_per_minute * duration_pending

    consultation_pending = Consultation(
        client_id=alice.id,
        consultant_id=bob_profile.id,
        scheduled_at=now,
        original_duration_minutes=duration_pending,
        duration_minutes=duration_pending,
        total_amount=amount_pending,
        status="pending",
        notes="Need a quick 10 minute check-in.",
        request_expires_at=now + timedelta(minutes=2),
    )
    session.add(consultation_pending)
    session.flush()

    # --- AI chatbot history for Alice ---
    session.add_all([
        ChatMessage(
            user_id=alice.id,
            role="user",
            content="Hi, I need help finding a business strategy consultant.",
            intent="consultant_search"
        ),
        ChatMessage(
            user_id=alice.id,
            role="assistant",
            content="I can help with that! You can browse online consultants from the home page.",
            intent="consultant_search_response"
        ),
    ])

    # --- Wallet top-up record for Alice ---
    session.add(
        WalletTransaction(
            user_id=alice.id,
            consultation_id=None,
            amount=Decimal("500.00"),
            transaction_type="deposit",
            description="Initial wallet top-up"
        )
    )

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