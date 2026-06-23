# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Added pool settings to handle production connection limits cleanly
engine = create_engine(
    settings.database_url,
    pool_size=10,          # Keeps up to 10 persistent connections open
    max_overflow=20,       # Allows spikes up to 20 additional concurrent connections
    pool_pre_ping=True     # Automatic health-check reconnect wrapper if database drops idle sockets
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)