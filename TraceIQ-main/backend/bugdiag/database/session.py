"""Database session and connection engine manager.
Supports PostgreSQL with pgvector, and automated fallback for local development.
"""

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from bugdiag.core.config import get_settings
from bugdiag.core.logging import get_logger

logger = get_logger("database")
settings = get_settings()

def create_configured_engine():
    db_url = settings.DATABASE_URL
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    
    try:
        engine = create_engine(
            db_url,
            connect_args=connect_args,
            pool_pre_ping=True
        )
        # Test connection
        with engine.connect() as conn:
            if db_url.startswith("postgresql"):
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    conn.commit()
                    logger.info("PostgreSQL pgvector extension verified.")
                except Exception as ext_err:
                    logger.warning(f"pgvector extension check notice: {ext_err}")
            conn.execute(text("SELECT 1"))
        logger.info(f"Database connection established successfully with {db_url.split('@')[-1] if '@' in db_url else db_url}")
        return engine
    except Exception as e:
        logger.warning(f"Could not connect to configured DATABASE_URL: {e}")
        # A silent production fallback can split writes between Postgres and a local
        # SQLite file. Keep the convenience fallback strictly in development.
        if not db_url.startswith("sqlite") and settings.APP_ENV.lower() in {"development", "dev", "local"}:
            fallback_url = "sqlite:///./bugdiag_local.db"
            logger.warning("Development database fallback enabled: using local SQLite.")
            fallback_engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False},
                pool_pre_ping=True
            )
            return fallback_engine
        raise RuntimeError(
            f"Could not connect to configured database for APP_ENV={settings.APP_ENV!r}; "
            "refusing to silently switch databases."
        ) from e

engine = create_configured_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all database tables based on declarative models."""
    from bugdiag.models import (  # noqa: F401
        submission,
        knowledge_base,
        diagnosis
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")
