"""
Pydantic Schemas
Request and response schemas for API validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class PatientBase(BaseModel):
    """Base schema with common patient fields"""
    name: str = Field(..., min_length=1, description="Patient's full name")
    notes: Optional[str] = Field(None, description="Clinical notes about the patient")


class PatientCreate(PatientBase):
    """Schema for creating a new patient"""
    pass


class PatientUpdate(BaseModel):
    """Schema for updating a patient"""
    name: str = Field(..., min_length=1, description="Patient's full name")
    notes: Optional[str] = Field(None, description="Clinical notes about the patient")


class PatientResponse(PatientBase):
    """Schema for patient response data"""
    id: int = Field(..., description="Patient ID")
    date_created: datetime = Field(..., description="When the patient record was created")
    date_last_updated: datetime = Field(..., description="When the patient record was last updated")

    class Config:
        from_attributes = True  # Allow ORM model to be used as schema


class PatientDetailResponse(PatientResponse):
    """Detailed patient response (inherits from PatientResponse)"""
    pass
