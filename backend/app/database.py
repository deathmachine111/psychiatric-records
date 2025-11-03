"""
Database configuration and connection
SQLite database for local storage
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL (relative path from backend directory)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./psychiatric_records.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency for FastAPI routes to get database session
    
    Usage in routes:
        @app.get("/api/patients")
        def get_patients(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(db_engine=None):
    """
    Initialize database by creating all tables
    Called during application startup

    Args:
        db_engine: Optional database engine to use (for testing)
    """
    from app import models  # Import here to avoid circular dependency
    target_engine = db_engine or engine
    Base.metadata.create_all(bind=target_engine)
    print("Database initialized successfully")
