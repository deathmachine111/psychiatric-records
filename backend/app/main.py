"""
FastAPI Main Application
Entry point for the Psychiatric Patient Record System
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes
from app.routes import patients
from app.database import init_db

# Initialize FastAPI app
app = FastAPI(
    title="Psychiatric Patient Record System",
    description="AI-powered patient record management with Gemini transcription",
    version="0.1.0"
)

# Configure CORS for Svelte frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port + fallback
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database when app starts"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Psychiatric Patient Record System API",
        "version": "0.1.0"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",  # Will be updated after DB implementation
        "gemini_api": "configured" if os.getenv("GEMINI_API_KEY") else "not configured",
        "notion_api": "configured" if os.getenv("NOTION_API_TOKEN") else "not configured"
    }

# Mount routers (Phase 1: Patients, Phase 2+: Others)
app.include_router(patients.router, prefix="/api", tags=["patients"])
# app.include_router(files.router, prefix="/api", tags=["files"])  # Phase 2
# app.include_router(processing.router, prefix="/api", tags=["processing"])  # Phase 5
# app.include_router(notion.router, prefix="/api", tags=["notion"])  # Phase 5.5

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
