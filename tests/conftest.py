"""
Test Configuration and Fixtures
Sets up test database and FastAPI test client
"""
import sys
from pathlib import Path

# Add backend to path so we can import app
backend_path = str(Path(__file__).parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Create in-memory SQLite database for tests BEFORE importing app
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# NOW import app and database modules
from app.database import Base, get_db
from app.main import app as fastapi_app

# Import models to register them with Base
from app import models as _  # noqa: F401


@pytest.fixture(scope="function")
def db() -> Session:
    """
    Create a fresh test database for each test
    Tables are created before the test runs and destroyed after
    """
    # Create all tables in test database
    Base.metadata.create_all(bind=test_engine)

    # Create session
    session = TestingSessionLocal()

    yield session

    # Clean up
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db: Session, monkeypatch) -> TestClient:
    """
    Create FastAPI test client with overridden database dependency
    """
    # Import database module so we can patch it
    from app import database as db_module

    def override_get_db():
        """Override dependency to use test database session"""
        yield db

    # Patch the database.engine to use test_engine
    # This ensures the startup event creates tables in the test database
    monkeypatch.setattr(db_module, "engine", test_engine)

    # Register the override
    fastapi_app.dependency_overrides[get_db] = override_get_db

    # Create and return test client
    # The startup event will now use test_engine to create tables
    with TestClient(fastapi_app) as test_client:
        yield test_client

    # Clean up
    fastapi_app.dependency_overrides.clear()
