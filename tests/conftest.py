"""
PyTest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database.connection import get_db_session as get_db
from database.connection import Base
# Import all models to ensure they are registered with SQLAlchemy
from database.models import User, FMTTemplate

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine for each test function"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    # Clean up after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a fresh database session for each test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database session"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(client):
    """Create a test user"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    return response.json()
