# Test Scaffold Template

## Quick Start: Creating New Tests for This Project

Copy and adapt this template when writing new tests for any feature.

---

## Template 1: Basic CRUD Endpoint Test

```python
# tests/test_<feature>.py
import pytest
from fastapi import status
from app.models import <Model>
from app.schemas import <Schema>


class Test<FeatureName>:
    """Test suite for <feature> endpoints"""

    @pytest.fixture
    def sample_<entity>(self, db):
        """Create a sample entity for testing"""
        entity = <Model>(
            name="Test <Entity>",
            # ... required fields
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def test_create_<entity>_success(self, client, db):
        """Test successful creation"""
        payload = {
            "name": "New <Entity>",
            # ... required fields
        }
        response = client.post("/api/<entities>", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New <Entity>"

        # Verify in database
        db_entity = db.query(<Model>).filter(
            <Model>.name == "New <Entity>"
        ).first()
        assert db_entity is not None

    def test_create_<entity>_missing_required_field(self, client):
        """Test validation of required fields"""
        payload = {
            # Missing "name"
        }
        response = client.post("/api/<entities>", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_<entity>_success(self, client, sample_<entity>):
        """Test retrieving entity by ID"""
        response = client.get(f"/api/<entities>/{sample_<entity>.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_<entity>.id

    def test_get_<entity>_not_found(self, client):
        """Test 404 when entity doesn't exist"""
        response = client.get("/api/<entities>/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_<entity>_success(self, client, sample_<entity>, db):
        """Test updating entity"""
        payload = {"name": "Updated <Entity>"}
        response = client.put(
            f"/api/<entities>/{sample_<entity>.id}",
            json=payload
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify in database
        db.refresh(sample_<entity>)
        assert sample_<entity>.name == "Updated <Entity>"

    def test_delete_<entity>_success(self, client, sample_<entity>, db):
        """Test deleting entity"""
        response = client.delete(f"/api/<entities>/{sample_<entity>.id}")

        assert response.status_code == status.HTTP_200_OK

        # Verify deleted
        assert db.query(<Model>).filter(
            <Model>.id == sample_<entity>.id
        ).first() is None
```

---

## Template 2: File Upload Test

```python
# tests/test_file_upload.py
import pytest
import io
from fastapi import status
from pathlib import Path


class TestFileUpload:
    """Test suite for file upload functionality"""

    @pytest.fixture
    def patient_with_name(self, db):
        """Create a patient for file uploads"""
        from app.models import Patient

        patient = Patient(name="Upload Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    def test_upload_file_success(self, client, db, mock_patients_path, patient_with_name):
        """Test successful file upload"""
        # Prepare fake file
        fake_file = io.BytesIO(b"fake audio content")
        files = {"file": ("audio.mp3", fake_file, "audio/mpeg")}

        # Upload
        response = client.post(
            f"/api/patients/{patient_with_name.id}/files",
            files=files,
            data={"user_metadata": "Test metadata"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["filename"] == "audio.mp3"
        assert data["user_metadata"] == "Test metadata"

        # Verify file exists on disk
        from app.models import File
        file_record = db.query(File).filter(File.id == data["id"]).first()
        assert file_record is not None

    def test_upload_invalid_file_type(self, client, patient_with_name):
        """Test rejection of invalid file types"""
        fake_file = io.BytesIO(b"fake content")
        files = {"file": ("document.pdf", fake_file, "application/pdf")}

        response = client.post(
            f"/api/patients/{patient_with_name.id}/files",
            files=files
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_file_too_large(self, client, patient_with_name):
        """Test rejection of oversized files"""
        # This requires mocking - see conftest.py for patterns
        pass
```

---

## Template 3: Database Integration Test

```python
# tests/test_database_integration.py
import pytest
from app.models import Patient, File


class TestDatabaseIntegration:
    """Test complex database operations"""

    def test_patient_file_relationship(self, db):
        """Test FK relationships work correctly"""
        # Create patient
        patient = Patient(name="Relationship Test")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create files for patient
        file1 = File(
            patient_id=patient.id,
            filename="file1.mp3",
            file_type="audio",
            local_path="path/to/file1.mp3"
        )
        file2 = File(
            patient_id=patient.id,
            filename="file2.mp3",
            file_type="audio",
            local_path="path/to/file2.mp3"
        )
        db.add_all([file1, file2])
        db.commit()

        # Query and verify
        files = db.query(File).filter(File.patient_id == patient.id).all()
        assert len(files) == 2

    def test_cascade_delete(self, db):
        """Test that deleting patient cascades to files"""
        # Setup
        patient = Patient(name="Cascade Test")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        file = File(
            patient_id=patient.id,
            filename="test.mp3",
            file_type="audio",
            local_path="path/to/test.mp3"
        )
        db.add(file)
        db.commit()

        # Delete patient
        db.delete(patient)
        db.commit()

        # Verify files are deleted
        files = db.query(File).filter(File.patient_id == patient.id).all()
        assert len(files) == 0
```

---

## Template 4: Service/Business Logic Test

```python
# tests/test_metadata_service.py
import pytest
from app.services import MetadataManager


class TestMetadataService:
    """Test metadata service logic"""

    @pytest.fixture
    def metadata_manager(self, mock_patients_path):
        """Initialize metadata manager with test path"""
        return MetadataManager(mock_patients_path)

    def test_sanitize_patient_name(self, metadata_manager):
        """Test patient name sanitization"""
        name = "Dr. John/Mary Doe-Smith (Pediatric)"
        safe_name = name.replace("/", "_").replace("\\", "_")

        # Verify no path separators remain
        assert "/" not in safe_name
        assert "\\" not in safe_name

    def test_metadata_sync_creates_file(self, db, mock_patients_path):
        """Test that metadata sync creates metadata.json"""
        from app.models import Patient

        # Setup
        patient = Patient(name="Metadata Test")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Sync metadata
        manager = MetadataManager(mock_patients_path)
        metadata = manager.sync_from_database(patient.id, patient.name, db)

        # Verify file exists
        metadata_path = (
            mock_patients_path / f"PT_{patient.name}" / "metadata.json"
        )
        assert metadata_path.exists()

        # Verify content
        assert metadata["patient_id"] == patient.id
        assert metadata["patient_name"] == patient.name
```

---

## Template 5: Error Handling Test

```python
# tests/test_error_handling.py
import pytest
from fastapi import status


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_endpoint_returns_proper_error_status(self, client):
        """Test HTTP status codes"""
        # 404 Not Found
        response = client.get("/api/patients/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # 400 Bad Request
        response = client.post("/api/patients", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_error_response_includes_message(self, client):
        """Test that error responses include helpful messages"""
        response = client.post("/api/patients", json={"name": ""})
        assert response.status_code >= 400
        data = response.json()
        assert "detail" in data or "message" in data
```

---

## conftest.py Pattern

```python
# tests/conftest.py
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Database setup
test_db_dir = tempfile.mkdtemp()
test_db_file = os.path.join(test_db_dir, "test.db")
TEST_SQLALCHEMY_DATABASE_URL = f"sqlite:///{test_db_file}"

test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="function")
def db() -> Session:
    """Fresh database for each test"""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db: Session, monkeypatch) -> TestClient:
    """TestClient with overridden database"""
    from app import database as db_module

    def override_get_db():
        try:
            yield db
        finally:
            if db.in_transaction():
                db.commit()

    monkeypatch.setattr(db_module, "engine", test_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_patients_path(tmp_path, monkeypatch):
    """Mock patients directory"""
    from app.routes import files as files_module

    monkeypatch.setattr(files_module, "PATIENTS_BASE_PATH", tmp_path)
    tmp_path.mkdir(exist_ok=True)
    return tmp_path
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_patients.py -v

# Run specific test class
pytest tests/test_patients.py::TestPatientCRUD -v

# Run specific test
pytest tests/test_patients.py::TestPatientCRUD::test_create_patient_success -v

# Run with coverage
pytest tests/ -v --cov=backend/app --cov-report=html

# Stop on first failure
pytest tests/ -v --maxfail=1

# Show print statements
pytest tests/ -v -s
```

---

## Key Principles

1. **One feature per test class** - Organize logically
2. **Descriptive names** - `test_create_patient_with_duplicate_name_fails` not `test_1`
3. **Arrange-Act-Assert** - Setup, execute, verify
4. **Use fixtures** - Don't repeat setup code
5. **Test edge cases** - Happy path + errors + boundaries
6. **Database isolation** - Each test gets fresh DB
7. **No external dependencies** - Mock or skip if needed
8. **Fast tests** - Use in-memory/file-based DB, not production DB

---

*Template Created: 2025-11-03*
*For use with FastAPI + SQLAlchemy + Pytest stack*
