# Phase 2: Audio File Upload - Comprehensive Plan

## Executive Summary
Add file upload capability for audio files with full validation, filesystem storage, and database tracking.

---

## API Endpoints to Implement

```
POST   /api/patients/{id}/files              - Upload file (audio/image/text)
GET    /api/patients/{id}/files              - List patient files
GET    /api/patients/{id}/files/{file_id}    - Get file details
DELETE /api/patients/{id}/files/{file_id}    - Delete file
```

---

## Database Model

### File ORM Model (SQLAlchemy)
```python
Files table:
- id (Integer, PK)
- patient_id (Integer, FK → patients.id)
- filename (String) - original filename
- file_type (String) - 'audio', 'image', 'text'
- upload_date (DateTime) - auto timestamp
- user_metadata (Text) - optional user notes
- local_path (String) - relative path from backend/patients/
- processing_status (String) - 'pending', 'processing', 'completed', 'failed'
- transcribed_filename (String, nullable)
- transcribed_content (Text, nullable)
- date_processed (DateTime, nullable)
- error_message (Text, nullable)
```

---

## State Isolation Strategy

**Critical Issue #1: Filesystem Isolation**
- Problem: Tests must not pollute `backend/patients/` with real test files
- Solution: Monkeypatch the base patients directory to a temp location
- Implementation: Use `pytest.fixture` with `monkeypatch` to override `PATIENTS_BASE_PATH`
- When: Patch BEFORE any file operations run

**Critical Issue #2: Foreign Key Dependencies**
- Problem: Files table requires valid patient_id
- Solution: Test fixture creates patient first, then uploads files for that patient
- Implementation: `client` fixture depends on `db` which already has patient creation

**Critical Issue #3: Path Handling**
- Problem: Windows uses backslashes, tests might run on Unix
- Solution: Use `pathlib.Path` exclusively, never `os.path`
- Implementation: All path operations use `Path()` and `.as_posix()` for DB storage

**Critical Issue #4: File Cleanup**
- Problem: Test files might remain on disk after tests fail
- Solution: Use pytest's `tmp_path` fixture + manual cleanup in fixture
- Implementation: Fixture creates temp dir, tests use it, pytest auto-cleans

**Critical Issue #5: Concurrent File Operations**
- Problem: Multiple tests creating files in same directory
- Solution: Each test gets isolated temp directory via `tmp_path` fixture
- Implementation: Monkeypatch with unique temp path per test

---

## File Validation Rules

### Size Limits
- Maximum: 50MB
- Check: `UploadFile.size` before processing

### Supported Types (Phase 2: Audio only)
```
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",           # .mp3
    "audio/mp3",            # .mp3 (alternate MIME)
    "audio/wav",            # .wav
    "audio/x-wav",          # .wav (alternate)
    "audio/ogg",            # .ogg
    "audio/x-ogg",          # .ogg (alternate)
    "audio/webm",           # .webm
    "audio/aac",            # .aac
}
```

### Validation Order
1. File provided (not None)
2. Filename not empty
3. MIME type in allowed list
4. File size < 50MB
5. Patient exists
6. Patient directory can be created

---

## Tests to Write (TDD)

### Creation Tests
- [ ] test_upload_audio_valid_mp3 - Success path
- [ ] test_upload_audio_valid_wav - Different format
- [ ] test_upload_audio_with_metadata - Store user notes
- [ ] test_upload_audio_invalid_format - Reject .txt as audio
- [ ] test_upload_audio_too_large - Reject 51MB file
- [ ] test_upload_audio_no_file - Missing file body
- [ ] test_upload_audio_patient_not_found - 404 for invalid patient_id
- [ ] test_upload_audio_file_saved - Verify filesystem structure
- [ ] test_upload_audio_database_entry - Verify DB entry created

### List/Read Tests
- [ ] test_list_patient_files_empty - No files yet
- [ ] test_list_patient_files_multiple - Multiple files
- [ ] test_get_file_details_success - Retrieve file metadata
- [ ] test_get_file_details_not_found - 404 for invalid file_id

### Delete Tests
- [ ] test_delete_file_success - File removed from DB and disk
- [ ] test_delete_file_not_found - 404
- [ ] test_delete_file_filesystem_cleanup - File actually deleted

---

## Filesystem Structure

```
backend/
├── patients/
│   └── PT_John_Doe/
│       ├── raw_files/
│       │   ├── session_1_audio.mp3          (stored file)
│       │   └── intake_session.wav           (stored file)
│       ├── processed_outputs/               (Phase 5)
│       └── metadata.json                    (Phase 3)
└── ... (other directories)
```

**Path Format in DB:**
```
local_path = "PT_John_Doe/raw_files/session_1_audio.mp3"
(relative to backend/patients/)
```

---

## Error Responses

### 400 Bad Request
- File type not supported
- File size exceeds 50MB
- No filename provided

### 404 Not Found
- Patient doesn't exist
- File doesn't exist

### 500 Internal Server Error
- Directory creation fails
- File save fails
- Database entry creation fails

---

## Implementation Execution Order

1. **Write Tests First (TDD)** ✓
   - Create `tests/test_files.py`
   - All tests should FAIL initially

2. **Create Models** ✓
   - Add `File` ORM model to `backend/app/models.py`
   - Ensure migration/table creation

3. **Create Schemas** ✓
   - Add Pydantic schemas to `backend/app/schemas.py`
   - FileUpload, FileResponse

4. **Create Routes** ✓
   - Implement `backend/app/routes/files.py`
   - All 4 endpoints

5. **Update Main** ✓
   - Include router in `backend/app/main.py`

6. **Run Tests** ✓
   - Iterate until all pass
   - Track coverage

7. **Commit** ✓
   - `git commit -m "Phase 2: Audio Upload Complete"`

---

## Key Implementation Considerations

### Async File Operations
- Use `aiofiles` for non-blocking file I/O
- Don't use `open()` synchronously in async context

### Path Safety
- Never trust user-provided filename directly
- Use `Path(filename).name` to strip path components
- Validate against directory traversal: `../`

### Error Messages
- Log full errors server-side
- Return generic messages to client (no path leakage)

### Database Consistency
- Create file record AFTER successful filesystem write
- If DB write fails, clean up filesystem file
- Use try-except-finally pattern

---

## Testing Patterns

### Filesystem Mocking
```python
@pytest.fixture
def mock_patients_path(tmp_path, monkeypatch):
    """Redirect patients directory to temp location"""
    monkeypatch.setattr("app.routes.files.PATIENTS_BASE_PATH", tmp_path)
    return tmp_path
```

### Sample Test
```python
def test_upload_audio_valid_mp3(client, db, mock_patients_path):
    # 1. Create patient fixture
    patient = create_test_patient(db, "John Doe")

    # 2. Create fake audio file
    fake_audio = ("test.mp3", b"fake audio data", "audio/mpeg")

    # 3. Upload
    response = client.post(
        f"/api/patients/{patient.id}/files",
        files={"file": fake_audio}
    )

    # 4. Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.mp3"
    assert data["file_type"] == "audio"

    # 5. Verify file saved
    assert (mock_patients_path / f"PT_{patient.name}" / "raw_files" / "test.mp3").exists()

    # 6. Verify DB entry
    file_record = db.query(File).filter(File.id == data["id"]).first()
    assert file_record is not None
    assert file_record.patient_id == patient.id
```

---

## Success Criteria

- [ ] All 13 tests passing
- [ ] 80%+ code coverage
- [ ] File saved to correct path
- [ ] Database entry created with FK integrity
- [ ] Error handling for all edge cases
- [ ] Filesystem cleanup on test completion
- [ ] Windows and Unix path compatibility
- [ ] PHASE2_COMPLETE committed to git

---

*Plan Created: 2025-11-03*
*Ready for TDD: Writing failing tests first*
