"""
SQLAlchemy Database Models
Defines the database schema for the psychiatric records system
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
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

    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}')>"
