"""SQLAlchemy Database configuration and session dependency."""
import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# Engine configuration with dialect-specific options
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Ensure directory exists for SQLite
if settings.DATABASE_URL.startswith("sqlite:////"):
    db_file_path = settings.DATABASE_URL.replace("sqlite:////", "/")
    os.makedirs(os.path.dirname(db_file_path), exist_ok=True)
elif settings.DATABASE_URL.startswith("sqlite:///"):
    db_file_path = settings.DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_file_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_db_initialized = False


def init_db() -> None:
    """Initialize all tables in database and seed if needed."""
    global _db_initialized
    try:
        from app.models import ticket, log, user  # noqa: F401
        Base.metadata.create_all(bind=engine)
        _db_initialized = True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database session with auto-init safety."""
    global _db_initialized
    if not _db_initialized:
        init_db()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
