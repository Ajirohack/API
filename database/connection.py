"""
Database connection management.

Provides optimized database connection pooling and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
from contextlib import contextmanager

import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=settings.ENVIRONMENT == "development"  # SQL logging in development
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()

def get_db_session() -> Generator[Session, None, None]:
    """
    Get a database session from the connection pool.
    
    Yields:
        Database session
        
    Note:
        This function is designed to be used as a FastAPI dependency.
        The session is automatically closed when the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def db_session():
    """
    Context manager for database sessions.
    For use in scripts and background tasks.
    
    Yields:
        Database session
        
    Example:
        with db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_engine():
    """
    Get the SQLAlchemy engine.
    
    Returns:
        SQLAlchemy engine
    """
    return engine

def init_db():
    """
    Initialize the database by creating all tables.
    
    Note:
        This should only be used for development and testing.
        Production should use proper migrations.
    """
    Base.metadata.create_all(bind=engine)
