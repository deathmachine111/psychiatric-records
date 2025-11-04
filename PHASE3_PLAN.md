# Phase 3: Metadata Input - Fix Plan

## Current Status
- **Passing:** 16/20 tests (80%)
- **Failing:** 4 tests

## Root Cause Analysis

### Pattern 1: File Count Sync Issues (2 tests)
**Tests:**
- test_metadata_created_on_first_file_upload
- test_metadata_synced_after_file_upload

**Root Cause:**
When metadata sync happens in route handler:
1. Route handler creates File record and commits
2. Metadata sync queries database for files
3. Query sees 0 files (session hasn't seen the commit)
4. Metadata is written with empty file list

**Why it happens:**
- File upload endpoint commits file record
- Then immediately calls metadata_manager.sync_from_database()
- The sync uses the SAME session that route handler uses
- SQLAlchemy hasn't invalidated the query cache yet

**Solution:**
In `backend/app/services/metadata.py`, the `sync_from_database()` method needs to:
1. Refresh the session to see committed data
2. OR use a fresh database query with proper session handling

### Pattern 2: Special Characters Edge Case (1 test)
**Test:** test_metadata_with_special_characters_in_name

**Likely Causes:**
- Directory naming with special characters (parentheses, etc)
- Path sanitization not handling all cases
- File creation/metadata paths getting out of sync

**Solution:**
- Review the sanitization in both files.py and metadata.py
- Ensure consistent behavior for special character handling

### Pattern 3: Integration Test (1 test)
**Test:** test_metadata_reflects_all_file_operations

**Root Cause:**
Likely a cascade of the file count issues affecting complex multi-operation scenarios

**Solution:**
Will be fixed when Pattern 1 is resolved

## Fix Strategy

### Step 1: Fix Session Caching in MetadataManager
**File:** `backend/app/services/metadata.py`
**Method:** `sync_from_database()`

**Problem Code:**
```python
files = db.query(File).filter(File.patient_id == patient_id).all()
```

**Why it fails:**
The query happens in the same session that just committed the file. SQLAlchemy caches query results.

**Solution Options:**
A. Call `db.expire_all()` before querying (simplest)
B. Create a fresh connection for the query (safer)
C. Use `db.refresh()` on individual objects (overkill)

**Recommendation:** Option A - `db.expire_all()` before the query

### Step 2: Fix Special Characters Handling
**Files:**
- `backend/app/routes/files.py` - line 154 (get_patient_directory)
- `backend/app/services/metadata.py` - line 68 (get_patient_metadata_path)

**Current behavior:**
Replaces `/` and `\` with `_`
Example: "Test (Patient)" → "PT_Test (Patient)" (keeps parentheses)

**Issue:**
Parentheses might cause issues on some filesystems

**Solution:**
Decide on unified strategy - either:
1. Keep special chars (current approach) - just ensure consistent
2. Sanitize more characters - safer but changes directory structure

**Recommendation:** Keep current approach but ensure both files use identical sanitization

### Step 3: Systematic Testing
Apply fixes in this order:
1. Fix metadata.py session caching
2. Fix special characters if needed
3. Verify Phase 1 & 2 still pass (regression test)
4. Run Phase 3 full suite

## Implementation Plan

### Fix 1: MetadataManager Session Caching
Add `db.expire_all()` in `sync_from_database()` before querying files:

```python
def sync_from_database(self, patient_id: int, patient_name: str, db: Session) -> dict:
    # ... existing code ...
    
    # Ensure session sees all committed data
    db.expire_all()  # <-- ADD THIS LINE
    
    # Get all files for patient
    files = db.query(File).filter(File.patient_id == patient_id).all()
    
    # ... rest of method ...
```

### Fix 2: Verify Special Character Consistency
Check that both `files.py:80` and `metadata.py:68` use identical sanitization:
- Both files should use: `patient_name.replace("/", "_").replace("\\", "_")`

### Fix 3: Run Comprehensive Tests
```bash
# Test Phase 3 after fixes
pytest tests/test_metadata.py -v

# Regression test Phase 1 & 2
pytest tests/test_patients.py tests/test_files.py -v

# Full validation
pytest tests/ -v
```

## Expected Outcome
- Phase 3: 20/20 ✅
- Phase 1: 13/13 ✅
- Phase 2: 13/15 (session isolation issues remain but not related to Phase 3)
- **Total: 46/50 tests** (can investigate Phase 2 session issues separately)

## Time Estimate
- Fix metadata session caching: 5 minutes
- Verify special character consistency: 5 minutes
- Testing and validation: 10 minutes
- **Total: ~20 minutes**

---

## Root Cause Summary

All 4 Phase 3 failures trace back to ONE root cause:
**Session caching in MetadataManager.sync_from_database()**

When files are created and metadata sync is triggered:
1. File is inserted and committed (in route handler session)
2. Metadata sync queries same session
3. Session hasn't invalidated its File query cache
4. Query returns 0 files instead of 1
5. Metadata is synced with empty file list

**The Fix:**
Call `db.expire_all()` before querying in `sync_from_database()`

This single fix should resolve 3 of 4 failing tests. The special characters test likely fails independently.
