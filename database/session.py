"""
Database session management for the application.

This module provides SQLAlchemy engine configuration, session factory,
and FastAPI dependency injection for database connections. Supports
both PostgreSQL (production) and SQLite (development) databases.
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base


# =============================================================================
# Database Configuration
# =============================================================================

# Database URL from environment variable
# Default: SQLite for development (file-based, no server required)
# Production: PostgreSQL with connection pooling
_DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./conversations.db"
)

# SQLite-specific configuration
# For SQLite, we need to check_same_thread=False for FastAPI compatibility
_CONNECT_ARGS = {"check_same_thread": False} if _DATABASE_URL.startswith("sqlite") else {}

# Engine configuration
# - echo=False: Disable SQL query logging (set to True for debugging)
# - pool_pre_ping=True: Verify connections before using them
# - pool_recycle: Recycle connections after 1 hour (PostgreSQL), -1 for SQLite (disabled)
_engine_kwargs = {
    "connect_args": _CONNECT_ARGS,
    "echo": False,
    "pool_pre_ping": True,
}

# Only set pool_recycle for PostgreSQL (SQLite doesn't support connection pooling)
if _DATABASE_URL.startswith("postgresql"):
    _engine_kwargs["pool_recycle"] = 3600

engine = create_engine(_DATABASE_URL, **_engine_kwargs)

# Session factory
# - autocommit=False: Transactions must be explicitly committed
# - autoflush=False: Don't flush before query (explicit control)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =============================================================================
# Public API
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session management.

    This function provides a database session to FastAPI endpoint functions.
    The session is automatically closed after the request is processed,
    ensuring proper connection cleanup.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/conversations")
        def get_conversations(db: Session = Depends(get_db)):
            return db.query(Conversation).all()

    Note:
        The session is yielded as part of a context manager pattern.
        FastAPI automatically handles the cleanup after the response is sent.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in the Base metadata.
    This is useful for development and testing.
    For production, use Alembic migrations instead.

    Example:
        from database.session import init_db
        init_db()
    """
    Base.metadata.create_all(bind=engine)


def get_database_url() -> str:
    """
    Get the current database URL (for debugging/monitoring).

    Returns:
        str: The database connection URL (with password masked for PostgreSQL)

    Example:
        from database.session import get_database_url
        print(f"Using database: {get_database_url()}")
    """
    if _DATABASE_URL.startswith("postgresql"):
        # Mask password in PostgreSQL URLs
        parts = _DATABASE_URL.split("@")
        if len(parts) == 2:
            user_part = parts[0].split("://")[1]
            host_part = parts[1]
            user = user_part.split(":")[0]
            return f"postgresql://{user}:***@{host_part}"
    return _DATABASE_URL
