# 🧠 Psychiatric Patient Record System

AI-powered patient record management with Gemini transcription and Notion export.

## 🚀 Quick Start

### 1. Setup Environment

```powershell
# Navigate to project
cd C:\Users\soumy\Documents\Claude_Dir\psychiatric-records

# Create virtual environment
python -m venv .venv

# Activate venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```powershell
# Copy example env file
copy .env.example .env

# Edit .env and add your API keys:
# - GEMINI_API_KEY
# - NOTION_API_TOKEN
# - NOTION_DATABASE_ID
```

### 3. Start Development with Claude Code

```powershell
# Make sure venv is activated
.\.venv\Scripts\activate

# Start Claude Code
claude code

# Follow the instructions in CLAUDE.md
```

## 📚 Documentation

- **CLAUDE.md** - Complete development guide for Claude Code
- **Project Constitution** - See documents folder for detailed architecture

## 🏗️ Architecture

- **Backend:** FastAPI + SQLite
- **Frontend:** Svelte + Vite
- **AI Processing:** Google Gemini API
- **Export:** Notion API
- **Testing:** pytest with TDD

## 📂 Project Structure

```
psychiatric-records/
├── backend/           # FastAPI application
│   ├── app/          # Application code (Claude Code will build this)
│   └── patients/     # Local file storage
├── tests/            # Test suite (Claude Code will build this)
├── .claude/          # Claude Code configuration
├── CLAUDE.md         # Development instructions
└── requirements.txt  # Python dependencies
```

## 🧪 Testing

```powershell
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=backend/app --cov-report=html

# Run specific test file
pytest tests/test_patients.py -v
```

## 🚀 Running the Application

```powershell
# Start backend (in one terminal)
cd backend
uvicorn app.main:app --reload --port 8000

# Start frontend (in another terminal)
cd frontend
npm run dev
```

## 📝 Development Workflow

1. **Read CLAUDE.md** - Complete development guide
2. **Follow TDD** - Write tests first, always
3. **One phase at a time** - Don't skip ahead
4. **Commit after each phase** - Document progress
5. **Manual testing required** - Test in browser/Postman

## 🔒 Security Notes

- **NO authentication yet** (future feature)
- Patient data stored locally only
- Never commit `.env` file
- Add auth comments for future implementation

## 📊 Development Progress

### ✅ Completed Phases

#### Phase 1: Patient CRUD ✅
- Patient creation, retrieval, update, delete (13/13 tests)
- SQLite database integration
- Pydantic validation schemas
- Complete API endpoints

#### Phase 2: Audio File Upload ✅
- Audio file validation and storage
- Local filesystem organization (`backend/patients/PT_{name}/`)
- File metadata tracking in database
- Edge case testing (large files, wrong formats)
- 13/15 tests passing + resolved session isolation issues

#### Phase 3: Metadata Input ✅
- Metadata schema and validation
- File metadata API endpoints
- Metadata service layer with I/O operations
- 20/20 tests passing (100% coverage)
- Comprehensive testing documentation created

### 📋 Next Phase

**Phase 4: Image + Text Upload** (Starting Soon)
- Extend file upload for `.jpg`, `.png`, `.txt`, `.pdf`
- Validate file types and sizes
- Integrate with existing metadata system
- Edge case testing

### 🗺️ Full Roadmap

```
Phase 1: Patient CRUD                    ✅
Phase 2: Audio File Upload               ✅
Phase 3: Metadata Input                  ✅
Phase 4: Image + Text Upload             🚧 (Ready to start)
Phase 5: Gemini AI Transcription          ⬜
Phase 5.5: Notion Export Integration    ⬜
Phase 6: Display Records UI             ⬜
Phase 7: Error Handling & Progress      ⬜
Phase 8: Deployment to Fly.io           ⬜
Phase 9: Polish & Documentation         ⬜
```

---

*Built with Claude Code + TDD*
