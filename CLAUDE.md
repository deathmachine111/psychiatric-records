# 🧠 Psychiatric Patient Record System - Claude Code Instructions

## 🎯 Project Mission
Build a psychiatric patient record management system that processes audio/image/text files through Gemini AI transcription and exports final outputs to Notion.

**User:** Solo psychiatrist with patient consent  
**Timeline:** MVP in 48-60 hours  
**Deployment:** Local first → Fly.io later  
**Architecture:** MODULAR. Test each brick before the next.

---

## ⚠️ CRITICAL DEVELOPMENT RULES

### 1. **TEST-DRIVEN DEVELOPMENT (TDD) - NON-NEGOTIABLE**
```
ALWAYS follow this sequence:
1. Write a FAILING test first
2. Run pytest to confirm it fails
3. Write minimal code to make it pass
4. Run pytest to confirm it passes
5. Refactor if needed
6. ONLY THEN move to next feature

NEVER write code without a test first.
```

### 2. **Defensive Coding Mindset**
- Assume the code WILL break
- Add try-catch blocks proactively
- Validate all inputs with Pydantic
- Log errors verbosely
- Test edge cases immediately
- If something can go wrong, it will - plan for it

### 3. **Modular Development - One Brick at a Time**
```
Phase 1: Patient CRUD (Database + API)
Phase 2: File Upload (Audio)
Phase 3: Metadata Input
Phase 4: Image + Text Upload
Phase 5: Gemini Transcription Processing
Phase 5.5: Notion Export Integration
Phase 6: Display Processed Records UI
Phase 7: Error Handling & Progress Indicators
Phase 8: Deployment to Fly.io
Phase 9: Polish & Documentation
```

**NEVER skip phases. NEVER work on Phase N+1 before Phase N is complete and tested.**

### 4. **Expert Debugging & Root Cause Analysis**
When a bug emerges, follow this discipline:

**Ask Deep Questions:**
- What is the actual value/state at point X in execution?
- When does this code run relative to other code?
- What module-level state exists? When is it initialized?
- What order does initialization happen in?
- Is there a state mismatch between test setup and runtime?

**Trace Execution Path:**
- Don't treat symptoms. Find root cause.
- Work backwards from error to origin.
- Follow the data/state through the call stack.
- Verify assumptions about when/where code runs.

**Build Smart Fixes:**
- Never skip/remove code to avoid problems.
- Patch state BEFORE it's used.
- Make problematic code work WITH your setup.
- Verify the fix makes logical sense, not just "works."

**Learn & Document:**
- Each bug reveals a planning gap.
- Document root cause and pattern for future reference.
- Update architecture if pattern appears again.
- Recognize missing "longsightedness" (state isolation issues, timing problems, etc.)

**Documented Patterns (Lessons from Phases 1-2):**

**Pattern 1: Module-Level Engine Patching (Phase 1)**
```
Problem: TestClient creates test session but init_db() uses wrong database engine
Root Cause: Module-level `engine` variable wasn't patched before startup event runs
Timeline: import app.database → creates engine → startup event uses engine
Fix: monkeypatch.setattr(db_module, "engine", test_engine) BEFORE TestClient creation
Prevention: Always identify when startup events run (before or after fixture setup)
```

**Pattern 2: ORM Session Lifecycle in Response Handlers (Phase 2)**
```
Problem: Returning ORM object after db.commit() fails with "object expired" error
Root Cause: SQLAlchemy expires object attributes after commit. Pydantic tries to access
           them, but can't reload from in-memory test database
Timeline: db.flush() → get ID → db.commit() → object expires → try to access attributes
Fix: Materialize all attributes into dict BEFORE commit:
     attrs = {attr: getattr(obj, attr) for attr in [...]}
     db.commit()
     return attrs
Prevention: For async endpoints returning ORM objects, always fetch dict representation
            before transaction close, or use fresh query after commit
```

**Pattern 3: Module-Level Filesystem Path Patching (Phase 2)**
```
Problem: Tests pollute real backend/patients/ directory with test files
Root Cause: PATIENTS_BASE_PATH defined at module level, not patched before routes imported
Timeline: import routes.files → PATIENTS_BASE_PATH set to real path → tests use real path
Fix: In fixture, import module THEN patch:
     from app.routes import files as files_module
     monkeypatch.setattr(files_module, "PATIENTS_BASE_PATH", tmp_path)
Prevention: Identify all module-level constants that affect I/O. Create fixtures to patch
            them. Document which modules need what patching in fixture dependencies.
```

**Pattern 4: Pydantic v2 Configuration (Phase 2)**
```
Problem: Deprecated Config class causes warnings and validation failures
Root Cause: Pydantic v2 requires ConfigDict instead of nested Config class
Fix: Replace:
     class Config:
         from_attributes = True
     With:
     model_config = ConfigDict(from_attributes=True)
Prevention: For all Pydantic models, use model_config = ConfigDict(...) pattern
```

**Critical Testing Principles (Learned Hard Way):**
1. **Capture state BEFORE operations change it** - Get values before commit, flush, or close
2. **Patch module-level state BEFORE importing code that uses it** - Order matters
3. **Test isolation = patch everything mutable** - DB engine, file paths, time, random
4. **Session lifecycle awareness** - Know when objects expire (after commit)
5. **Don't mock away the problem** - Make tests work WITH real behavior, not around it

### 5. **Checkpoint System**
After completing each phase:
- Run full test suite: `pytest tests/ -v`
- Manually test in browser if UI component
- **UPDATE PROJECT_STATUS.md** - CRITICAL: Update status, test counts, and completion percentage
- Commit changes: `git add . && git commit -m "Phase X complete"`
- Wait for user approval before next phase

**⚠️ CRITICAL RULE: PROJECT_STATUS.md MUST be updated after EVERY phase completion.** This is the single source of truth for project visibility. Never skip this step or project status becomes unreliable.

---

## 🏗️ Tech Stack

### Backend
- **Framework:** FastAPI (explicit errors, Pydantic validation)
- **Database:** SQLite (local file: `backend/psychiatric_records.db`)
- **File Storage:** Local filesystem (`backend/patients/PT_{name}/`)
- **AI Processing:** Gemini API (transcription/OCR)
- **Notion Export:** `notion-client` Python library

### Frontend
- **Framework:** Svelte (NOT React - cleaner errors)
- **Build Tool:** Vite
- **Testing:** Manual browser testing + Playwright (if time permits)

### Development
- **Language:** Python 3.11+
- **Testing:** pytest with coverage
- **Environment:** `.env` for secrets (NEVER commit)
- **Version Control:** Git (ALWAYS commit after each phase)

---

**→ See PROJECT_STATUS.md for project structure and current phase completion details**

---

## 🗄️ Database Schema

### Patients Table
```sql
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);
```

### Files Table
```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,  -- 'audio', 'image', 'text'
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_metadata TEXT,
    local_path TEXT NOT NULL,
    processing_status TEXT DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    transcribed_filename TEXT,
    transcribed_content TEXT,
    date_processed TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
);
```

### Processing Logs Table
```sql
CREATE TABLE processing_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    processed_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gemini_model TEXT,
    status TEXT NOT NULL,  -- 'success', 'error'
    error_message TEXT,
    tokens_used INTEGER,
    FOREIGN KEY (file_id) REFERENCES files (id)
);
```

---

## 📂 Local File Storage Structure

```
backend/patients/
  └── PT_{patient_name}/
      ├── raw_files/
      │   ├── session_1_audio.mp3
      │   ├── intake_form.jpg
      │   └── notes.txt
      ├── processed_outputs/
      │   ├── session_1_audio_transcribed.txt
      │   ├── intake_form_transcribed.txt
      │   └── notes_extracted.txt
      └── metadata.json
```

**metadata.json structure:**
```json
{
  "patient_name": "John Doe",
  "created_date": "2025-11-03",
  "files": [
    {
      "filename": "session_1_audio.mp3",
      "type": "audio",
      "uploaded_date": "2025-11-03",
      "user_metadata": "Second therapy session with both parents",
      "processing_status": "completed",
      "transcribed_file": "session_1_audio_transcribed.txt"
    }
  ]
}
```

---

## 🧪 Testing Standards

### Core Principle: RED → GREEN → REFACTOR

```python
# ALWAYS start with a failing test
def test_create_patient():
    # This test should FAIL initially
    response = client.post("/api/patients", json={"name": "Test Patient"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test Patient"

# Then write code to make it pass
# Then run: pytest tests/test_patients.py -v
```

### Test Coverage Requirements
- **Critical paths:** 90%+ coverage
- **API endpoints:** 100% coverage
- **Database operations:** 100% coverage
- **File operations:** 80%+ coverage (mocked)
- **Gemini integration:** 100% (mocked API calls)

### Running Tests
```bash
# Full test suite
pytest tests/ -v --cov=backend/app --cov-report=html

# Single test file
pytest tests/test_patients.py -v

# Stop on first failure
pytest tests/ -v --maxfail=1

# With detailed output
pytest tests/ -vv --tb=short
```

### Test Isolation
- **Mock external APIs:** Gemini, Notion (use `pytest-mock`)
- **Separate test database:** Use `:memory:` SQLite
- **Clean state:** Reset database before each test
- **No real API calls in tests** (except manual Phase 5 verification)

---

## 🔌 API Endpoints to Build

### Phase 1: Patient Management
```
POST   /api/patients           - Create new patient
GET    /api/patients           - List all patients
GET    /api/patients/{id}      - Get patient details
PUT    /api/patients/{id}      - Update patient
DELETE /api/patients/{id}      - Delete patient
```

### Phase 2-4: File Management
```
POST   /api/patients/{id}/files              - Upload file (audio/image/text)
GET    /api/patients/{id}/files              - List patient files
GET    /api/patients/{id}/files/{file_id}    - Get file details
DELETE /api/patients/{id}/files/{file_id}    - Delete file
```

### Phase 5: Processing
```
POST   /api/patients/{id}/process/{file_id}  - Process file with Gemini
GET    /api/patients/{id}/processing-status  - Check processing status
```

### Phase 5.5: Notion Export
```
POST   /api/patients/{id}/export-to-notion   - Export processed data to Notion
```

---

## 🤖 Gemini API Integration

### Prompts to Use

**Audio Transcription (Hindi/Bengali/Assamese):**
```
You are a clinical transcriber for a psychiatrist's practice.
Transcribe this therapy session audio to clean, readable text.
The language may be Hindi, Bengali, or Assamese.
Preserve speaker turns and key clinical information.
Output: Plain text only, no markdown or formatting.
```

**Image/Document OCR:**
```
You are a psychiatric document analyzer.
Extract all text from this clinical document (form, assessment, notes).
Preserve structure, headings, and clinical relevance.
Output: Plain text only, clean and organized.
```

**Text File Cleaning:**
```
You are a clinical text processor.
Clean and organize this clinical note while preserving all clinical information.
Fix typos and formatting issues.
Output: Plain text only, preserve clinical accuracy.
```

### Error Handling Strategy
```python
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def process_with_gemini(file_path: str, prompt: str):
    try:
        # Upload file to Gemini
        file = genai.upload_file(file_path)
        
        # Generate content
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, file])
        
        return response.text
    except Exception as e:
        # Log error
        logger.error(f"Gemini processing failed: {e}")
        raise
```

---

## 📝 Notion Integration

### Setup
```python
from notion_client import Client

notion = Client(auth=os.getenv("NOTION_API_TOKEN"))

# Database ID for patient records (set in .env)
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
```

### Export Function
```python
async def export_to_notion(patient_id: int, file_id: int):
    """
    Export processed transcription to Notion database
    """
    # Get patient and file data from DB
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    file = db.query(File).filter(File.id == file_id).first()
    
    # Create Notion page
    notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Patient Name": {"title": [{"text": {"content": patient.name}}]},
            "File Type": {"select": {"name": file.file_type}},
            "Upload Date": {"date": {"start": file.upload_date.isoformat()}},
            "Processed Date": {"date": {"start": file.date_processed.isoformat()}},
        },
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": "Transcription"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": file.transcribed_content}}]}
            }
        ]
    )
```

---

## 🚨 Error Handling Patterns

### Always Use Try-Catch
```python
@router.post("/api/patients/{id}/files")
async def upload_file(id: int, file: UploadFile):
    try:
        # Validate file size
        if file.size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(400, "File too large (max 50MB)")
        
        # Validate file type
        allowed_types = ["audio/mpeg", "audio/wav", "image/jpeg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(400, f"Invalid file type: {file.content_type}")
        
        # Save file
        # ... implementation
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"File upload failed: {e}", exc_info=True)
        raise HTTPException(500, f"Upload failed: {str(e)}")
```

### Progress Indicators
```python
from fastapi import BackgroundTasks

async def process_file_background(file_id: int):
    """Background task for long-running Gemini processing"""
    try:
        # Update status to 'processing'
        file = db.query(File).filter(File.id == file_id).first()
        file.processing_status = "processing"
        db.commit()
        
        # Process with Gemini
        result = await process_with_gemini(file.local_path, prompt)
        
        # Update status to 'completed'
        file.processing_status = "completed"
        file.transcribed_content = result
        file.date_processed = datetime.now()
        db.commit()
        
    except Exception as e:
        # Update status to 'failed'
        file.processing_status = "failed"
        file.error_message = str(e)
        db.commit()
```

---

## 🎯 REMAINING PHASES (Phases 1-6 Complete ✅)

### Phase 7: Error Handling & UI Polish 🔲 NEXT
- [ ] Add error display UI improvements
- [ ] Implement user-friendly error messages
- [ ] Add progress indicator for Gemini processing
- [ ] Improve validation feedback
- **Effort:** 4-8 hours | **Blocker:** None

### Phase 8: Deployment to Fly.io 🔲
- [ ] Create fly.toml configuration
- [ ] Setup environment variables
- [ ] Deploy backend + frontend
- [ ] Test in production
- **Effort:** 8-16 hours | **Blocker:** Fly.io account

### Phase 9: Polish & Documentation 🔲
- [ ] Final QA pass
- [ ] Performance optimization
- [ ] Authentication implementation (OAuth2/JWT)
- [ ] API versioning
- [ ] Rate limiting
- **Effort:** 16+ hours

**→ For completed phase details (1-6), see PROJECT_STATUS.md**

---

## 🔒 Security & Privacy Notes

### Data Protection
- **NO authentication yet** (Phase 9+ feature)
- Patient names stored directly (not de-identified, solo practice with consent)
- Local storage only (no cloud until Fly.io deployment)
- `.env` file NEVER committed (in `.gitignore`)

### Future Auth Placeholder
```python
# TODO: Add authentication in future version
# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/api/patients")
async def create_patient(patient: PatientCreate):  # , token: str = Depends(oauth2_scheme)
    """
    Create new patient
    
    TODO: Add authentication:
    - Verify token with oauth2_scheme
    - Check user permissions
    - Log access
    """
    pass
```

---

## 🛠️ Development Workflow

### Daily Workflow
```bash
# 1. Activate virtual environment
.\.venv\Scripts\activate  # Windows PowerShell

# 2. Run tests to ensure baseline
pytest tests/ -v

# 3. Work on current phase (TDD: test first, code second)

# 4. Run tests after each change
pytest tests/ -v --maxfail=1

# 5. Commit when phase complete
git add .
git commit -m "Phase X: Feature complete"

# 6. Document progress
```

### If Tests Fail
```bash
# 1. Read the error message carefully
pytest tests/test_patients.py -vv --tb=long

# 2. Check logs
tail -f backend/app.log

# 3. Debug with print statements or pdb
import pdb; pdb.set_trace()

# 4. Fix the issue

# 5. Re-run tests
pytest tests/ -v

# 6. NEVER proceed until tests pass
```

### Manual Testing
```bash
# 1. Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# 2. Start frontend (separate terminal)
cd frontend
npm run dev

# 3. Test in browser: http://localhost:5173

# 4. Use Postman/curl for API testing
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Patient"}'
```

---

## 📊 Progress Tracking

Keep a `PROGRESS.md` file to track completed phases:

```markdown
# Development Progress

## Phase 1: Patient CRUD ✅
- Completed: 2025-11-03
- Tests passing: 12/12
- Notes: Basic CRUD working, ready for file upload

## Phase 2: Audio Upload 🚧
- In Progress
- Tests passing: 3/5
- Blockers: File size validation edge case
```

---

## 🎓 Claude Code Tips

### How to Ask for Help
```
# Good prompts:
"Implement the patient CRUD tests in test_patients.py following TDD"
"Debug why the file upload is returning 500 error"
"Review the Gemini integration code for error handling issues"

# Bad prompts:
"Build everything" (too broad)
"Fix it" (no context)
"Make it work" (vague)
```

### Code Review Checklist
Before committing, ask yourself:
- [ ] Did I write tests FIRST?
- [ ] Do all tests pass?
- [ ] Is there error handling for edge cases?
- [ ] Are API responses validated with Pydantic?
- [ ] Is sensitive data in .env (not hardcoded)?
- [ ] Did I test manually in browser/Postman?
- [ ] Is the code readable (clear variable names)?
- [ ] Are there comments for complex logic?

---

## 🧠 Tools & Debugging Resources

### Quick Reference: Available Tools

| Tool | Type | Status | Token Cost | Use Case |
|------|------|--------|-----------|----------|
| **WebSearch** | Built-in | Always on | 1-2x | Planning, best practices, research |
| **Sequential Thinking** | MCP | Manual | 3-5x ⚠️ | Complex debugging (reserve for Phase 7+) |
| **GitHub MCP** | MCP | Manual | Minimal | Framework source, issue research |
| **systematic-debugging** | Skill | Auto | None | Root cause investigation framework |
| **root-cause-tracing** | Skill | Auto | None | Backward call stack tracing |
| **test-fixing** | Skill | Auto | None | Test failure resolution |

**Strategy:** WebSearch at phase start for best practices (1-2x per phase). GitHub MCP as needed. Sequential Thinking only for critical blockers. Claude Skills auto-activate on issues.

### Critical Testing Patterns (From Phase 1-6)

**Pattern: Transaction Isolation with TestClient**
- **Problem:** Data persists in route handler but disappears from test
- **Root Cause:** :memory: SQLite + TestClient connection isolation
- **Fix:** Use file-based SQLite (not in-memory)
- **Prevention:** Read TESTING_PATTERNS.md before writing tests

**Pattern: SQLAlchemy Session Lifecycle**
- **Problem:** "Object expired" after db.commit()
- **Root Cause:** SQLAlchemy expires object attributes after commit
- **Fix:** Materialize attributes to dict BEFORE commit, or fresh query after
- **Prevention:** Understand session lifecycle before writing ORM code

**Reference Documentation:**
- **TESTING_PATTERNS.md** - Complete testing guide (11 critical patterns)
- **TEST_SCAFFOLD_TEMPLATE.md** - Copy-paste test templates
- **PROJECT_STATUS.md** - Current phase completion and test metrics

---

## 🚀 Getting Started

### First-Time Setup (Already Done)
```powershell
# 1. Navigate to project
cd C:\Users\soumy\Documents\Claude_Dir\psychiatric-records

# 2. Run setup script
.\setup.ps1

# 3. Start coding!
claude code
```

### Start Development
```powershell
# Activate venv
.\.venv\Scripts\activate

# Start backend
cd backend
uvicorn app.main:app --reload

# Start frontend (new terminal)
cd frontend
npm run dev

# Run tests (new terminal)
pytest tests/ -v --cov
```

---

## 📚 Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Svelte Tutorial:** https://svelte.dev/tutorial
- **Pytest Guide:** https://docs.pytest.org/
- **Gemini API:** https://ai.google.dev/docs
- **Notion API:** https://developers.notion.com/
- **Fly.io Docs:** https://fly.io/docs/

---

## ⚡ Remember

1. **Tests first, code second** - ALWAYS
2. **One phase at a time** - NO skipping
3. **Commit after each phase** - Document progress
4. **Error handling is NOT optional** - Plan for failure
5. **Manual testing required** - Automated tests aren't enough
6. **Read error messages carefully** - They tell you what's wrong
7. **Ask for help when stuck** - Don't waste time debugging alone
8. **Search strategically** - Use WebSearch BEFORE implementing (1-2x per phase)
9. **Review TESTING_PATTERNS.md** - Before writing tests for any new phase
10. **Use tools wisely** - GitHub MCP (free), Sequential Thinking (rare, expensive)

---

## 🎯 Success Criteria for MVP

- [ ] All 8 phases complete and tested
- [ ] Patient CRUD working
- [ ] File upload (audio/image/text) working
- [ ] Gemini transcription working
- [ ] Notion export working
- [ ] Basic UI functional
- [ ] 80%+ test coverage
- [ ] Deployed to Fly.io
- [ ] Error handling robust

**When all checked: MVP COMPLETE! 🎉**

---

*Last Updated: 2025-11-05 (Phase 6 Complete - File Compression)*
*Claude Code Version: Latest*
*Project Status: Phase 6 Complete - 175/175 tests passing (100%) - 78% Done ✅*

---

## 📝 Session Log

**Current Status (2025-11-05):**
- Phases 1-6 Complete: 175 tests passing (100%)
- 78% of project complete
- Claude Skills (3): systematic-debugging, root-cause-tracing, test-fixing - Auto-activated
- Next: Phase 7 (Error Handling & UI Polish)

**For detailed evolution and tool setup, see ARCHIVE.md**
