# Testing Patterns & Best Practices

## Critical Lessons from Phase 3 Testing

This document captures testing patterns discovered during Phase 3 implementation. These patterns prevent common pitfalls and accelerate test development.

---

## 1. Database Configuration for Testing

### ✅ **DO: Use File-Based SQLite for TestClient Tests**

```python
# conftest.py
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create temporary directory for test database
test_db_dir = tempfile.mkdtemp()
test_db_file = os.path.join(test_db_dir, "test.db")
TEST_DATABASE_URL = f"sqlite:///{test_db_file}"

# File-based SQLite maintains database state across connections
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
```

**Why:**
- `:memory:` SQLite databases are per-connection isolated
- TestClient creates separate connection contexts
- Data committed in one connection isn't visible to another
- File-based databases maintain state across commits

### ❌ **DON'T: Use :memory: SQLite with TestClient**

```python
# AVOID THIS
TEST_DATABASE_URL = "sqlite:///:memory:"
# Data will disappear after HTTP request completes
```

**Why it fails:**
- Each connection to `:memory:` gets its own isolated database
- TestClient's request handling creates connection scope issues
- Committed data isn't visible after request completes

---

## 2. Transaction Management in FastAPI Routes

### ✅ **DO: Let Dependency Override Manage Commits**

```python
# routes/files.py
async def upload_file(file: UploadFile, db: Session = Depends(get_db)):
    """
    Route handler should NOT call db.commit()
    Let the dependency override manage transaction completion
    """
    try:
        db_file = FileModel(...)
        db.add(db_file)
        db.flush()  # Get ID without committing

        # NOTE: No db.commit() here!
        # Dependency override will commit after route completes

        return {"id": db_file.id}
    except Exception as e:
        db.rollback()
        raise
```

```python
# conftest.py
def override_get_db():
    """
    Dependency override MUST manage transaction lifecycle
    """
    try:
        yield db
    finally:
        # CRITICAL: Commit after route handler finishes
        # This ensures TestClient sees committed data
        if db.in_transaction():
            db.commit()
```

**Why:**
- With `autocommit=False`, calling `db.commit()` in route handler starts a NEW transaction
- New transaction persists across the rest of the request
- Dependency override can't properly commit because session is in active transaction
- Correct pattern: Route prepares, Dependency commits

### ❌ **DON'T: Call db.commit() in Route Handlers (with TestClient)**

```python
# AVOID THIS
async def upload_file(db: Session = Depends(get_db)):
    db_file = FileModel(...)
    db.add(db_file)
    db.commit()  # DON'T DO THIS with TestClient!

    # After commit, a NEW transaction begins automatically
    # Dependency override's commit will fail or won't persist data
```

---

## 3. Session State Management

### ✅ **DO: Call db.expire_all() After Commits in Metadata Sync**

```python
# services/metadata.py
def sync_from_database(self, patient_id: int, patient_name: str, db: Session) -> dict:
    """
    After file upload route commits, metadata sync queries same session
    Must clear query cache to see newly committed data
    """
    # CRITICAL: Expire session cache to see committed data
    db.expire_all()

    # Now query sees the committed file
    files = db.query(File).filter(File.patient_id == patient_id).all()

    # ... rest of sync logic
```

**Why:**
- SQLAlchemy caches query results within a transaction
- Even after commit, if session is still active, it may use cached results
- `expire_all()` clears the cache and forces fresh queries from database

---

## 4. Path Sanitization Consistency

### ✅ **DO: Use Consistent Sanitization Across All Modules**

```python
# routes/files.py AND services/metadata.py should use IDENTICAL logic
def sanitize_patient_name(patient_name: str) -> str:
    """
    Sanitize directory name for filesystem safety
    Only replace path separators, preserve readability
    """
    return patient_name.replace("/", "_").replace("\\", "_")

# Usage in both files.py and metadata.py:
safe_name = sanitize_patient_name(patient.name)
patient_dir = PATIENTS_BASE_PATH / f"PT_{safe_name}"
```

**Why:**
- File upload creates directories in one place
- Metadata sync looks for them in another
- If sanitization differs, paths won't match
- Version control: extract to shared utility if used in 3+ places

### ❌ **DON'T: Different Sanitization in Different Modules**

```python
# files.py
safe_name = name.replace("/", "_")  # Only slashes

# metadata.py
safe_name = name.replace("/", "_").replace(" ", "_")  # Slashes AND spaces

# Result: Mismatched directory names!
```

---

## 5. Test Database Lifecycle

### ✅ **DO: Create Fresh DB Per Test, Clean Up After**

```python
@pytest.fixture(scope="function")
def db() -> Session:
    """
    Each test gets a fresh database
    """
    # Create fresh schema for this test
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()
    yield session

    # Clean up after test
    session.close()
    Base.metadata.drop_all(bind=test_engine)
```

**Why:**
- Test isolation prevents state leakage
- Fresh schema prevents schema conflicts
- Cleanup prevents test data accumulation

### ✅ **DO: Use Function Scope, Not Module Scope**

```python
# GOOD
@pytest.fixture(scope="function")  # Each test gets fresh DB
def db():
    ...

# AVOID
@pytest.fixture(scope="module")  # Tests share DB state
def db():
    ...
```

---

## 6. Dependency Override Pattern

### ✅ **DO: Override get_db with Session Management**

```python
@pytest.fixture
def client(db: Session, monkeypatch) -> TestClient:
    """
    Properly override database dependency
    """
    from app import database as db_module

    def override_get_db():
        """
        Route handler receives test session
        Override manages commit lifecycle
        """
        try:
            yield db
        finally:
            if db.in_transaction():
                db.commit()

    # Override the dependency
    from app.database import get_db
    fastapi_app.dependency_overrides[get_db] = override_get_db

    # Return test client
    with TestClient(fastapi_app) as test_client:
        yield test_client

    # Clean up overrides
    fastapi_app.dependency_overrides.clear()
```

---

## 7. Web Search & Hypothesis-Driven Testing

### ✅ **DO: Use Strategic Web Searches**

**Search BEFORE making assumptions:**
1. **Planning Phase** - Search for known patterns before designing
2. **Before Hypotheses** - Search for common pitfalls before testing theories
3. **When Suspicious** - Search if behavior seems wrong
4. **After Failures** - Search to understand root cause, not just workaround

**Search Strategy:**
```python
# Phase 1: Planning
# Search: "FastAPI SQLAlchemy session management TestClient best practices"
# Result: Discover dependency override pattern

# Phase 2: Before implementation
# Search: "SQLite :memory: TestClient isolation issues"
# Result: Discover file-based DB requirement

# Phase 3: During debugging
# Search: "SQLAlchemy autocommit=False transaction lifecycle"
# Result: Discover that commit() starts new transaction

# Phase 4: Validation
# Search: "FastAPI metadata sync patterns Flask patterns"
# Result: Validate our solution against known patterns
```

### Strategic Timing:

```
Investigation Path WITHOUT Web Search:
Hypothesis → Test → Fail → Hypothesis → Test → Fail → 2 hours of debugging

Investigation Path WITH Web Search:
Search → Hypothesis (informed) → Test → Success → 30 minutes total
```

---

## 8. File Upload with Metadata Integration

### ✅ **Complete Pattern for File Upload + Metadata Sync**

```python
# routes/files.py
@router.post("/{patient_id}/files")
async def upload_file(
    patient_id: int,
    file: UploadFile = File(...),
    user_metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Complete pattern for file upload with metadata sync
    """
    # 1. Validate
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404)

    # Capture name before DB operations expire object
    patient_name = patient.name

    # 2. Prepare
    safe_filename = sanitize_filename(file.filename)
    patient_dir = get_patient_directory(patient_id, patient_name)
    raw_files_dir = patient_dir / "raw_files"

    # 3. Create directories
    raw_files_dir.mkdir(parents=True, exist_ok=True)

    # 4. Save to disk
    file_path = raw_files_dir / safe_filename
    content = await file.read()
    file_path.write_bytes(content)

    # 5. Create DB entry
    db_file = FileModel(
        patient_id=patient_id,
        filename=safe_filename,
        file_type=infer_type(file.content_type),
        local_path=f"PT_{patient_name}/raw_files/{safe_filename}",
        user_metadata=user_metadata,
        processing_status="pending"
    )
    db.add(db_file)
    db.flush()  # Get ID without committing

    # Capture ID before object expires
    file_id = db_file.id

    # 6. Prepare response (BEFORE commit)
    response_data = {
        "id": db_file.id,
        "filename": db_file.filename,
        # ... all fields
    }

    # NOTE: DON'T commit here - let dependency override handle it

    # 7. Sync metadata (after flush, before commit)
    try:
        metadata_manager = MetadataManager(PATIENTS_BASE_PATH)
        # This will see the flushed but not-yet-committed file
        metadata_manager.sync_from_database(patient_id, patient_name, db)
    except Exception as e:
        logger.error(f"Metadata sync failed: {e}")
        # Don't fail upload if metadata sync fails

    return response_data
```

---

## 9. Testing Checklist

Before running tests:

- [ ] Test database is file-based, not `:memory:`
- [ ] Dependency override manages transaction (not route handler)
- [ ] Session lifecycle: fresh per test, cleaned up after
- [ ] Sanitization is consistent across all modules
- [ ] db.expire_all() used after commits in query-heavy code
- [ ] Patient/file names captured before object expiry
- [ ] Response data prepared from flushed objects, not after commit
- [ ] Error handling includes rollback
- [ ] Metadata operations don't fail main transaction

---

## 10. Common Pitfalls & Solutions

| Pitfall | Symptom | Solution |
|---------|---------|----------|
| `:memory:` SQLite | Data visible in route but not in tests | Use file-based SQLite |
| Route calls commit() | New transaction starts, dependency can't commit | Let dependency override manage commit |
| Forgot expire_all() | Metadata queries see 0 files after upload | Call `db.expire_all()` after flush/commit |
| Different sanitization | File path mismatch | Extract to shared utility |
| Query after expire | Session in new transaction | Call queries before commit |
| Object expires | AttributeError on access | Capture values before commit |

---

## 11. References & Further Reading

- **SQLAlchemy Session Management**: https://docs.sqlalchemy.org/en/20/orm/session_transaction.html
- **FastAPI Testing**: https://fastapi.tiangolo.com/advanced/testing-dependencies/
- **SQLModel Testing**: https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/
- **Pytest Fixtures**: https://docs.pytest.org/en/latest/how-to/fixtures.html
- **SQLite Limitations**: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#limitations

---

*Last Updated: 2025-11-03*
*Created after Phase 3 completion - captures 8 hours of debugging insights*
