"""
Test Configuration and Fixtures
Sets up test database and FastAPI test client
"""
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Add backend to path so we can import app
backend_path = str(Path(__file__).parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Create SQLite database for tests BEFORE importing app
# Use file-based database instead of :memory: to avoid connection pool issues
# with TestClient and transaction commits
import tempfile
import os
test_db_dir = tempfile.mkdtemp()
test_db_file = os.path.join(test_db_dir, "test.db")
TEST_SQLALCHEMY_DATABASE_URL = f"sqlite:///{test_db_file}"
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
    from app.models import File

    def override_get_db():
        """Override dependency to use test database session"""
        try:
            yield db
        finally:
            # CRITICAL: Commit any pending changes after route handler finishes
            # The route handler doesn't call commit(), so we must commit here
            # This is necessary for transaction management in TestClient
            if db.in_transaction():
                db.commit()

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


@pytest.fixture(scope="function")
def mock_patients_path(tmp_path, monkeypatch):
    """
    Mock the patients directory to use temporary location
    Prevents test files from polluting the real backend/patients/ directory

    This fixture patches PATIENTS_BASE_PATH in routes/files.py and routes/processing.py to use temp directory.
    Tests using this fixture can verify files were saved correctly.

    STATE ISOLATION: This is critical for preventing test files from polluting
    the real filesystem. We patch BEFORE any routes code runs.
    """
    # Import the files and processing modules so we can patch their PATIENTS_BASE_PATH
    from app.routes import files as files_module
    from app.routes import processing as processing_module

    # Patch PATIENTS_BASE_PATH to use the temp directory in both modules
    monkeypatch.setattr(files_module, "PATIENTS_BASE_PATH", tmp_path)
    monkeypatch.setattr(processing_module, "PATIENTS_BASE_PATH", tmp_path)

    # Create the patients base directory
    tmp_path.mkdir(exist_ok=True)

    yield tmp_path
