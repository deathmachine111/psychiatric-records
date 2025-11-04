"""
Pydantic Schemas
Request and response schemas for API validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


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


# File Schemas

class FileBase(BaseModel):
    """Base file schema with common fields"""
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="Type of file: 'audio', 'image', 'text'")
    user_metadata: Optional[str] = Field(None, description="User-provided metadata about the file")


class FileUpload(BaseModel):
    """Schema for file upload request (multipart form-data handled by FastAPI)"""
    user_metadata: Optional[str] = Field(None, description="Optional metadata")


class FileResponse(FileBase):
    """Schema for file response data"""
    model_config = ConfigDict(from_attributes=True)  # Allow ORM model to be used as schema

    id: int = Field(..., description="File ID")
    patient_id: int = Field(..., description="Patient ID")
    upload_date: datetime = Field(..., description="When the file was uploaded")
    processing_status: str = Field(..., description="Status: pending, processing, completed, failed")
    local_path: Optional[str] = Field(None, description="Local path relative to backend/patients/")
    transcribed_filename: Optional[str] = Field(None, description="Name of transcribed output file")
    transcribed_content: Optional[str] = Field(None, description="Transcribed/extracted text content")
    date_processed: Optional[datetime] = Field(None, description="When the file was processed")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")


# Metadata Schemas

class MetadataFileEntry(BaseModel):
    """Schema for file entry in metadata"""
    file_id: int = Field(..., description="File ID")
    filename: str = Field(..., description="Original filename")
    type: str = Field(..., description="File type: audio, image, text")
    uploaded_date: datetime = Field(..., description="When uploaded")
    user_metadata: Optional[str] = Field(None, description="User-provided metadata")
    processing_status: str = Field(..., description="Processing status")


class MetadataCreate(BaseModel):
    """Schema for creating/updating patient metadata"""
    model_config = ConfigDict(from_attributes=True)

    notes: Optional[str] = Field(None, min_length=0, description="Patient-level notes")


class MetadataResponse(BaseModel):
    """Schema for metadata response"""
    model_config = ConfigDict(from_attributes=True)

    patient_id: int = Field(..., description="Patient ID")
    patient_name: str = Field(..., description="Patient name")
    created_date: datetime = Field(..., description="When metadata was created")
    updated_date: datetime = Field(..., description="When metadata was last updated")
    notes: Optional[str] = Field(None, description="Patient-level notes")
    files: list[MetadataFileEntry] = Field(default_factory=list, description="List of files")
