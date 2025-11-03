"""
SQLAlchemy Database Models
Defines the database schema for the psychiatric records system
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Patient(Base):
    """
    Patient record model
    Represents a psychiatric patient with basic information
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationship to files
    files = relationship("File", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}')>"


class File(Base):
    """
    File record model
    Represents a file uploaded for a patient (audio, image, text)
    """
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # 'audio', 'image', 'text'
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_metadata = Column(Text, nullable=True)
    local_path = Column(String, nullable=False)  # Relative path from backend/patients/
    processing_status = Column(String, default="pending", nullable=False)  # pending, processing, completed, failed
    transcribed_filename = Column(String, nullable=True)
    transcribed_content = Column(Text, nullable=True)
    date_processed = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationship to patient
    patient = relationship("Patient", back_populates="files")

    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', patient_id={self.patient_id})>"
