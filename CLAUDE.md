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

## 📁 Project Structure

```
psychiatric-records/
├── .claude/
│   ├── CLAUDE.md              ← YOU ARE HERE
│   └── settings.json          ← Auto-test hooks
├── backend/
│   ├── app/
│   │   ├── main.py            ← FastAPI entry point
│   │   ├── database.py        ← SQLite connection
│   │   ├── models.py          ← SQLAlchemy models
│   │   ├── schemas.py         ← Pydantic schemas
│   │   └── routes/
│   │       ├── patients.py    ← Patient CRUD
│   │       ├── files.py       ← File upload
│   │       ├── processing.py  ← Gemini processing
│   │       └── notion.py      ← Notion export
│   ├── patients/              ← Local file storage
│   └── psychiatric_records.db ← SQLite database
├── frontend/
│   ├── src/
│   │   ├── App.svelte
│   │   ├── main.js
│   │   └── components/
│   │       ├── PatientList.svelte
│   │       ├── PatientForm.svelte
│   │       ├── FileUpload.svelte
│   │       └── RecordView.svelte
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── tests/
│   ├── conftest.py            ← Test fixtures
│   ├── test_patients.py
│   ├── test_files.py
│   ├── test_gemini.py
│   └── test_notion.py
├── .env                       ← API keys (gitignored)
├── .env.example               ← Template
├── .gitignore
├── requirements.txt
├── pytest.ini
└── README.md
```

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

## 🎯 Phase-by-Phase Checklist

### Phase 1: Patient CRUD ✅
- [ ] Create database models (`models.py`)
- [ ] Create Pydantic schemas (`schemas.py`)
- [ ] Implement database connection (`database.py`)
- [ ] Write tests first (`test_patients.py`)
- [ ] Implement patient routes (`routes/patients.py`)
- [ ] Run tests: `pytest tests/test_patients.py -v`
- [ ] Manual test with Postman/curl
- [ ] Commit: `git commit -m "Phase 1: Patient CRUD complete"`

### Phase 2: Audio Upload
- [ ] Write test for audio validation
- [ ] Build file upload endpoint
- [ ] Save to `patients/PT_{name}/raw_files/`
- [ ] Update files table in DB
- [ ] Test edge cases (large files, wrong formats)
- [ ] Run tests: `pytest tests/test_files.py -v`
- [ ] Manual test with real audio file
- [ ] Commit: `git commit -m "Phase 2: Audio upload complete"`

### Phase 3: Metadata Input
- [ ] Write test for metadata storage
- [ ] Add metadata field to schemas
- [ ] Update file upload to accept metadata
- [ ] Store in `metadata.json`
- [ ] Run tests
- [ ] Commit

### Phase 4: Image + Text Upload
- [ ] Write tests for image/text validation
- [ ] Extend upload endpoint for multiple types
- [ ] Validate file types (.jpg, .png, .txt, .pdf)
- [ ] Save to raw_files/
- [ ] Run tests
- [ ] Commit

### Phase 5: Gemini Integration
- [ ] Write tests with mocked Gemini API
- [ ] Implement Gemini client wrapper
- [ ] Build prompts for audio/image/text
- [ ] Create processing endpoint
- [ ] Save output to `processed_outputs/`
- [ ] Update DB with transcribed_content
- [ ] Test with REAL Gemini API (manual, limited calls)
- [ ] Run tests: `pytest tests/test_gemini.py -v`
- [ ] Commit

### Phase 5.5: Notion Export
- [ ] Write tests with mocked Notion API
- [ ] Implement Notion client wrapper
- [ ] Create export endpoint
- [ ] Test with REAL Notion API (manual)
- [ ] Run tests: `pytest tests/test_notion.py -v`
- [ ] Commit

### Phase 6: Display UI
- [ ] Build Svelte PatientList component
- [ ] Build RecordView component (shows files + transcriptions)
- [ ] Connect to FastAPI backend
- [ ] Test in browser
- [ ] Commit

### Phase 7: Error Handling
- [ ] Add progress indicators
- [ ] Implement retry logic
- [ ] Add user-friendly error messages
- [ ] Test failure scenarios
- [ ] Commit

### Phase 8: Deployment
- [ ] Create Fly.io configuration
- [ ] Setup environment variables
- [ ] Deploy backend
- [ ] Test in production
- [ ] Commit

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

## 🧠 Advanced Development: Tools & Strategic Research

### Available Tools (Installed)

**Installed MCP Servers:**

1. **Sequential Thinking MCP** ⭐⭐⭐⭐ (Installed - Phase 4+)
   ```
   Purpose: Deep reasoning for complex debugging and analysis
   Use: When stuck on tricky bugs or need architectural decisions
   ⚠️ WARNING: Token-intensive! Use sparingly
   Cost: ~3-5x more tokens than regular requests
   Strategy: Reserve for Phase 5+ (Gemini integration, complex logic)
   ```

2. **GitHub MCP** ⭐⭐⭐⭐ (Installed - Always available)
   ```
   Purpose: Direct access to FastAPI/SQLAlchemy source code and issues
   Use: Search for framework patterns, read source, find solutions in issues
   Cost: Minimal token overhead
   Strategy: Use freely when investigating framework behavior
   Example: "Query GitHub issues about SQLAlchemy session isolation"
   ```

3. **WebSearch** ⭐⭐⭐⭐ (Built-in)
   ```
   Purpose: Current documentation, best practices, recent solutions
   Use: Planning phase, hypothesis formation, validating approaches
   Cost: Moderate (1-2x regular request)
   Strategy: Use BEFORE starting code, not after failing
   Example: "FastAPI file upload testing best practices"
   ```

**Usage Strategy:**

| Tool | When to Use | Frequency | Token Cost |
|------|------------|-----------|-----------|
| WebSearch | Before implementing features | ~1x per phase | Moderate |
| GitHub MCP | When debugging framework issues | Ad-hoc | Minimal |
| Sequential Thinking | Stuck >15 min on complex problem | Rare | High ⚠️ |

**Token Budget Guidelines:**
- WebSearch: ~1-2 searches per phase (planning + hypothesis)
- GitHub MCP: Use as needed (low cost)
- Sequential Thinking: Max 2-3 uses before reaching limits

### Strategic Web Search Methodology

**When to Search (Critical Timing):**

Research conducted at SPECIFIC points prevents most debugging:

1. **Planning Phase (Before Implementation)**
   ```
   Timing: Before writing ANY code for a new feature
   Search: "[Framework] [feature] best practices"
           "[Language] [pattern] common pitfalls"
   Example: Before file upload: "FastAPI file upload SQLAlchemy testing best practices"
   Result: Would find the :memory: SQLite issue immediately
   Impact: Prevents 1-2 hours of debugging
   ```

2. **Hypothesis Formation (Before Testing)**
   ```
   Timing: When you suspect something is wrong
   Search: "[Observed behavior] [framework] transaction lifecycle"
   Example: "SQLAlchemy session commit TestClient isolation"
   Result: Would find the autocommit=False behavior immediately
   Impact: Prevents 30-60 minutes of empirical testing
   ```

3. **Before Each "Leap of Faith"**
   ```
   Timing: Before trying a creative fix that seems risky
   Search: "[Fix idea] [framework] pattern"
   Example: Before adding db.begin(): "SQLAlchemy commit db.begin() transaction"
   Result: Validates approach before wasting time implementing it
   Impact: Prevents 15-30 minutes of dead-end coding
   ```

4. **During Debugging (When Stuck > 10 Minutes)**
   ```
   Timing: As soon as you have a concrete hypothesis
   Search: Keep hypothesis specific, not vague
   Example: "SQLite in-memory database connection pool isolation pytest"
   Not: "why is my test failing" (too vague)
   Result: Validates root cause, prevents further investigation of symptoms
   Impact: Prevents 30-60 minutes chasing wrong causes
   ```

**Search Query Formula:**

```
[Specific Observation] + [Framework/Language] + [Pattern Name]

Good: "SQLAlchemy session state after commit TestClient FastAPI"
Bad: "database issue"

Good: "pytest fixture scope isolation database test"
Bad: "tests not working"
```

**Web Search Results Assessment:**

When you get search results, prioritize:
1. Official documentation (10x value vs blog posts)
2. GitHub issues showing exact problem (validate you're not alone)
3. Stack Overflow answers with explanations (understand why)
4. Medium/blog posts with code examples (implementation patterns)

### Phase 3 Testing Lessons (Complete Analysis)

**Pattern 1: Transaction Isolation with TestClient**
```
Problem: Data persists in route handler but disappears from test
Root Cause: :memory: SQLite + TestClient connection isolation
Solution Details: Use file-based SQLite (see TESTING_PATTERNS.md)
Prevention: Search before choosing test database
```

**Pattern 2: Route Handler Commit Interference**
```
Problem: db.commit() in route, then dependency override can't see data
Root Cause: autocommit=False starts new transaction after commit
Solution Details: Don't commit in route, let dependency override handle it
Prevention: Research FastAPI session management patterns upfront
```

**Pattern 3: SQLAlchemy Query Cache**
```
Problem: After flush/commit, query returns 0 results
Root Cause: Session caches query results, doesn't refetch after external updates
Solution Details: Call db.expire_all() before querying after other operations
Prevention: Understanding session lifecycle prevents this
```

**See TESTING_PATTERNS.md for Complete Details** - Captured 8 hours of debugging insights

### Reference Documentation Created

**New Files to Review Before Phase 4+:**

1. **TESTING_PATTERNS.md** ⭐⭐⭐⭐⭐
   - Complete guide to testing FastAPI + SQLAlchemy + Pytest
   - 11 critical patterns with examples
   - Gotchas and common pitfalls
   - Before implementing Phase 4+ tests, review this
   - Saves 2-3 hours of debugging per new phase

2. **TEST_SCAFFOLD_TEMPLATE.md** ⭐⭐⭐⭐
   - Copy-paste templates for new test suites
   - Patterns for CRUD, file upload, integration, services
   - Complete conftest.py pattern
   - Use this as starting point for Phase 4+ tests

3. **CLAUDE.md (This File) - Updated Sections:**
   - "Advanced Development: Tools & Strategic Research"
   - Installed tools: Sequential Thinking MCP, GitHub MCP, WebSearch
   - Token budget guidelines (avoid hitting limits)
   - Strategic web search methodology
   - Phase 3 lessons learned

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

*Last Updated: 2025-11-03 (Post-Phase 3 Analysis)*
*Claude Code Version: Latest*
*Project Status: Phase 3 Complete (20/20 tests) ✅*

---

---

## 🔧 Available Tools: MCPs and Claude Skills

### Quick Reference Table

| Tool | Type | Installed | Status | Cost | Use Case |
|------|------|-----------|--------|------|----------|
| **WebSearch** | Built-in | ✅ | Always on | 1-2x | Planning, best practices, research |
| **Sequential Thinking** | MCP | ✅ | Manual invocation | 3-5x ⚠️ | Complex debugging, deep analysis |
| **GitHub MCP** | MCP | ✅ | Manual invocation | Minimal | Framework source, issue research |
| **systematic-debugging** | Skill | ✅ | Auto-activates | None | Root cause investigation framework |
| **root-cause-tracing** | Skill | ✅ | Auto-activates | None | Backward call stack tracing |
| **test-fixing** | Skill | ✅ | Auto-activates | None | Test failure resolution |

### What is a Skill vs an MCP?

**Claude Skills (.claude/skills/)**
- Pure **thinking methodologies** and frameworks
- Activate automatically in relevant contexts
- Zero system overhead (no hooks, no processes)
- Guide Claude's approach to problems
- Examples: systematic-debugging, root-cause-tracing

**MCPs (Model Context Protocol)**
- External **tool providers** via subprocesses
- Require explicit invocation via Task tool
- Provide specialized capabilities
- Token-intensive for complex tasks
- Examples: Sequential Thinking, GitHub integration

### Installed Skills (3 Total)

#### 1. **systematic-debugging** (SKILL.md - 113 lines)
```
Location: .claude/skills/systematic-debugging/SKILL.md
Source: obra/superpowers (skill only, NO HOOKS)
Activation: Auto-triggers on bugs, test failures, unexpected behavior
```

**When to Use:**
- Encountering any bug or test failure
- Before proposing ANY fix (investigate first!)
- Time pressure situations (when quick fixes tempt you)
- Complex multi-component issues

**The Four Phases:**
1. Root Cause Investigation: Trace data flow to source
2. Pattern Analysis: Compare working vs broken code
3. Hypothesis & Testing: Form specific, testable hypotheses
4. Implementation: Address root causes, not symptoms

**Key Principle:** "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"

**Red Flags (Stop & Discuss):**
- Proposing solutions before tracing data flow
- Attempting multiple fixes simultaneously
- Third+ fix attempt after two failures (architectural problem)
- Skipping test writing

#### 2. **root-cause-tracing** (SKILL.md - 145 lines)
```
Location: .claude/skills/root-cause-tracing/SKILL.md
Source: obra/superpowers (skill only, NO HOOKS)
Activation: Auto-triggers on deep execution stack bugs
```

**When to Use:**
- Errors occur deep in execution (not entry points)
- Long stack traces with unclear origins
- Invalid data with unknown source
- Need to identify which test/code path triggers problem

**The Five-Step Process:**
1. Observe symptom (where does error appear?)
2. Find immediate cause (what code directly fails?)
3. Ask "What called this?" (work backward)
4. Keep tracing upward (follow parameters backward)
5. Locate original trigger (true source of problem)

**Adding Instrumentation:**
```python
# When manual tracing insufficient, add logging
print(f"DEBUG: file_id = {file_id}, type = {type(file_id)}")
print(f"DEBUG: Stack: {inspect.stack()}")
```

**Defense-in-Depth:**
After fixing root cause, add validation at multiple layers to prevent recurrence.

#### 3. **test-fixing** (SKILL.md - 79 lines)
```
Location: .claude/skills/test-fixing/SKILL.md
Source: mhattingpete/claude-skills-marketplace
Activation: Auto-triggers on test failures
```

**When to Use:**
- Test suite failures
- Request: "fix these tests" or "make tests pass"
- After implementation, before commit

**Methodology:**
1. Execute test suite, catalog failures
2. Group by error type and module
3. Prioritize by impact and dependency order
4. Fix sequentially with validation
5. Run full suite to confirm no regressions

### Installed MCPs (2 Registered, Pending Verification)

#### 1. **Sequential Thinking MCP** ⭐⭐⭐⭐ (EXPENSIVE)
```
Connection: stdio transport (user scope)
Command: npx -y @modelcontextprotocol/inspector (test)
Status: Registered in settings.local.json
```

**When to Use:**
- Stuck on complex problem > 15 minutes
- Need deep systematic analysis
- Architecture decisions required
- Complex debugging requiring multiple hypothesis

**How to Use:**
```
Task tool with subagent_type="general-purpose"
Detailed prompt with full context
Expect 3-5x token consumption
Reserve for Phase 5+ or critical blockers
```

**Token Budget:** Max 2-3 uses before approaching limits
**Cost:** ~3-5x regular request tokens

#### 2. **GitHub MCP** ⭐⭐⭐⭐ (MINIMAL COST)
```
Connection: HTTP transport (pre-configured)
Status: Available for code search and issues
```

**When to Use:**
- Framework source code investigation
- Find GitHub issues matching your problem
- Research patterns in public repositories
- Validate approaches before implementation

**How to Use:**
```
Use directly in conversation:
- Search code: search_code("pattern language:python")
- View issues: issue_read(method="get", owner="...", repo="...", issue_number=...)
- Examine commits: get_commit(owner="...", repo="...", sha="...")
```

**Token Cost:** Minimal (1-2x overhead)
**Usage:** Ad-hoc, no daily limit

### Critical Discovery: obra/superpowers Hooks Issue

**Root Cause Analysis:**

The obra/superpowers library includes a **`hooks/session-start.sh`** script that auto-executes at terminal startup. This caused:
- session.ssh file creation
- Terminal becoming unresponsive
- Claude Code CLI breaking
- Complete inability to use terminal commands

**Why It Happens:**
```
obra/superpowers structure:
├── hooks/
│   ├── session-start.sh  ← Auto-executes at CLI startup
│   ├── hooks.json        ← Defines hook triggers
│   └── ...
└── skills/
    ├── systematic-debugging/
    ├── root-cause-tracing/
    └── test-fixing/
```

When installed via plugin system, the **entire library** (including hooks) gets loaded.

**Solution: Skill Definitions Only**

Extract ONLY the skill SKILL.md files and install project-scoped:
```
.claude/skills/
├── systematic-debugging/SKILL.md  (pure methodology)
├── root-cause-tracing/SKILL.md    (pure methodology)
└── test-fixing/SKILL.md           (pure methodology)
```

**Result:**
- ✅ Get proven debugging methodologies
- ✅ Zero hook infrastructure
- ✅ No CLI interference
- ✅ No terminal issues
- ✅ Project-scoped (safe to rollback)

**Key Principle:**
> "Extract skill definitions from problematic libraries. Install as project-scoped SKILL.md files only. Never use the full library installation if hooks are present."

---

## 📝 Evolution Log

### Session 1 (Phase 3 Completion + Analysis) - 2025-11-03

**Achievements:**
- ✅ Phase 3: 20/20 tests passing (100%)
- ✅ Identified root cause: Transaction isolation with TestClient + :memory: SQLite
- ✅ Fixed through strategic debugging and hypothesis-driven methodology
- ✅ Created comprehensive TESTING_PATTERNS.md
- ✅ Created TEST_SCAFFOLD_TEMPLATE.md
- ✅ Updated CLAUDE.md with MCP and web search strategy

**Key Insights Documented:**
- Transaction lifecycle with SQLAlchemy autocommit=False
- Session management patterns for FastAPI TestClient
- Strategic web search methodology (timing and query formulation)
- When to use MCP servers vs traditional documentation

**Improvements for Phase 4+:**
- Use file-based SQLite for tests (not :memory:)
- Let dependency override manage commits (not route handlers)
- Call db.expire_all() before querying after flush/commit
- Search proactively before implementing (prevent 1-2 hours of debugging)
- Use TEST_SCAFFOLD_TEMPLATE.md for new test suites

**Technical Debt Resolved:**
- Debug logging cleaned up
- Path sanitization made consistent
- Session lifecycle properly documented
- Metadata sync verified with file integration

---

### Session 2 (Phase 4 Initialization + Tool Setup) - 2025-11-04

**Achievements:**
- ✅ Evaluated ApiDog for TDD (conclusion: not helpful for this project)
- ✅ Installed Sequential Thinking MCP (stdio, user scope)
- ✅ Installed GitHub MCP (pre-existing, HTTP)
- ✅ Updated CLAUDE.md with actual tools + token budgets
- ✅ Documented tool usage strategy (prevent hitting limits)
- ✅ Ready to start Phase 4: Image + Text Upload

**Tools Now Available:**
- Sequential Thinking MCP: Deep debugging (use sparingly, ~3-5x token cost)
- GitHub MCP: Framework source + issues (use freely, minimal cost)
- WebSearch: Planning phase, best practices (1-2x token cost)

**Token Budget Strategy:**
- WebSearch: ~1-2 per phase (planning only)
- GitHub MCP: Ad-hoc, no limit
- Sequential Thinking: Max 2-3 before hitting limits (reserved for Phase 5+)

**Phase 4 Ready:**
- Review TESTING_PATTERNS.md before writing tests
- Use TEST_SCAFFOLD_TEMPLATE.md for test structure
- WebSearch once at phase start for "FastAPI image/text upload best practices"
- Apply file validation patterns from Phase 2

---

---

### Session 3 (Claude Skills Installation + obra/superpowers Discovery) - 2025-11-04

**Critical Discovery:**
- 🔍 **Root Cause Found:** obra/superpowers library includes `hooks/session-start.sh` that auto-executes at terminal startup
- ⚠️ This hook infrastructure is WHY previous installation broke your CLI (session.ssh issue, terminal unresponsiveness)
- ✅ **Solution Validated:** Extract ONLY skill definitions, install project-scoped without hooks

**Achievements:**
- ✅ Installed 3 Claude Skills (systematic-debugging, root-cause-tracing, test-fixing)
- ✅ All installed project-scoped in `.claude/skills/` directory
- ✅ ZERO hooks infrastructure (pure SKILL.md methodology files)
- ✅ All 71 tests passing - no project impact
- ✅ CLI remains safe and functional
- ✅ Created comprehensive "Available Tools" section in CLAUDE.md
- ✅ Documented obra/superpowers hook issue for future reference

**Technical Details:**

**What Was Installed:**
```
.claude/skills/
├── systematic-debugging/SKILL.md (113 lines)  - Four-phase debugging methodology
├── root-cause-tracing/SKILL.md   (145 lines)  - Backward call stack tracing
└── test-fixing/SKILL.md          (79 lines)   - Test failure resolution
```

**Why It's Safe:**
- Project-scoped (`.claude/skills/` not `~/.claude/skills/`)
- Pure methodology files (SKILL.md = thinking guides)
- NO hooks (obra's problematic `hooks/session-start.sh` excluded)
- NO subprocess management (no MCP overhead)
- NO configuration modification
- Zero system interference

**Skills Now Available:**

1. **systematic-debugging** - Auto-activates when bugs detected
   - Four-phase investigation framework
   - Prevents symptom-only fixes
   - Red flags for architectural problems

2. **root-cause-tracing** - Auto-activates for deep execution bugs
   - Five-step backward tracing methodology
   - Add instrumentation when needed
   - Defense-in-depth validation pattern

3. **test-fixing** - Auto-activates on test failures
   - Systematic test failure resolution
   - Group by error type and module
   - Sequential fix with regression testing

**Documentation Updates:**
- Added "🔧 Available Tools: MCPs and Claude Skills" section (200+ lines)
- Quick reference table (all tools, costs, use cases)
- Detailed explanation of each skill with when/how to use
- Critical discovery about obra/superpowers hook infrastructure
- Key principle: Extract skill definitions from problematic libraries

**What This Solves:**
- ✅ You wanted proven debugging methodologies
- ✅ You feared obra/superpowers breaking things again
- ✅ Root cause identified and documented
- ✅ Safe alternative solution deployed
- ✅ Future-proofing: Others know to extract skills from hooks

**Test Results:**
- ✅ 71/71 passing (100%)
- ✅ No regressions from skill installations
- ✅ All three skills available for auto-activation

**Key Insight for Future Sessions:**
> "When installing from problematic libraries: Extract ONLY the SKILL.md definition files. Project-scope them in `.claude/skills/`. Ignore all hook infrastructure. Result: Get the methodology without the breaking changes."

---

**Previous Sessions:**
- Phase 1: Patient CRUD (13/13 tests) ✅
- Phase 2: Audio Upload (13/15 tests) ✅ with known session isolation issues
- Phase 3: Metadata Input (20/20 tests) ✅
- Phase 5: Gemini AI Integration (71/71 tests) ✅ - Complete end-to-end processing
- Phase 5.5: Notion Export (71/71 tests) ✅ - Complete notion integration
- Phase 6: Frontend UI (104 tests) ✅ - Svelte components and routing
