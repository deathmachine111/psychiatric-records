"""
File Management API Routes
Endpoints for uploading, listing, and managing patient files
"""
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patient, File as FileModel
from app.schemas import FileResponse
from app.services import MetadataManager

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/patients", tags=["files"])

# ===== Configuration =====
# Base path for patient files (can be patched in tests)
PATIENTS_BASE_PATH = Path(__file__).parent.parent.parent / "patients"

# Allowed audio MIME types (Phase 2)
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",      # .mp3
    "audio/mp3",       # .mp3 alternate
    "audio/wav",       # .wav
    "audio/x-wav",     # .wav alternate
    "audio/ogg",       # .ogg
    "audio/x-ogg",     # .ogg alternate
    "audio/webm",      # .webm
    "audio/aac",       # .aac
    "audio/x-m4a",     # .m4a
}

# Allowed image MIME types (Phase 4)
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",      # .jpg, .jpeg
    "image/jpg",       # .jpg alternate
    "image/png",       # .png
    "image/gif",       # .gif
    "image/webp",      # .webp
    "application/pdf", # .pdf (treated as image/document)
}

# Allowed text MIME types (Phase 4)
ALLOWED_TEXT_TYPES = {
    "text/plain",      # .txt
    "text/markdown",   # .md
    "text/x-markdown", # .md alternate
}

# All allowed file types
ALLOWED_FILE_TYPES = ALLOWED_AUDIO_TYPES | ALLOWED_IMAGE_TYPES | ALLOWED_TEXT_TYPES

# Maximum file size: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes


# ===== Helper Functions =====

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal

    Args:
        filename: Original filename from user

    Returns:
        Safe filename with path components stripped
    """
    if not filename:
        raise ValueError("Filename cannot be empty")

    # Get just the filename, strip any path components
    safe_name = Path(filename).name

    if not safe_name:
        raise ValueError("Filename cannot be empty or only path separators")

    return safe_name


def get_patient_directory(patient_id: int, patient_name: str) -> Path:
    """
    Get the directory path for a patient

    Args:
        patient_id: Patient ID (unused but included for consistency)
        patient_name: Patient's name

    Returns:
        Path object for patient directory
    """
    # Create sanitized directory name: PT_{patient_name}
    # Only replace path separators - spaces and other chars are allowed
    safe_patient_name = patient_name.replace("/", "_").replace("\\", "_")
    patient_dir = PATIENTS_BASE_PATH / f"PT_{safe_patient_name}"
    return patient_dir


# ===== API Endpoints =====

@router.post("/{patient_id}/files", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    patient_id: int,
    file: UploadFile = File(...),
    user_metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload a file for a patient

    - **patient_id**: The patient's ID
    - **file**: The file to upload (audio, image, or text)
    - **user_metadata**: Optional metadata about the file

    Returns: Created file record with ID and metadata
    """
    try:
        # 1. Validate patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            logger.warning(f"Patient not found for file upload: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )

        # Capture patient name early (before db operations that expire the object)
        patient_name = patient.name

        # 2. Validate file is provided
        if not file or not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )

        # 3. Sanitize filename
        try:
            safe_filename = sanitize_filename(file.filename)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # 4. Validate file type (MIME type)
        if not file.content_type or file.content_type not in ALLOWED_FILE_TYPES:
            logger.warning(
                f"Invalid file type: {file.content_type} for patient {patient_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file.content_type}' is not supported. Allowed: audio, image, or text files"
            )

        # 5. Validate file size
        if file.size and file.size > MAX_FILE_SIZE:
            logger.warning(
                f"File too large: {file.size} bytes for patient {patient_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of 50MB"
            )

        # 6. Create patient directory structure
        try:
            patient_dir = get_patient_directory(patient_id, patient.name)
            raw_files_dir = patient_dir / "raw_files"
            raw_files_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(
                f"Failed to create directory for patient {patient_id}: {str(e)}",
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create patient directory"
            )

        # 7. Save file to disk
        try:
            file_path = raw_files_dir / safe_filename

            # Read file content and write to disk
            content = await file.read()
            file_path.write_bytes(content)

            logger.info(f"File saved: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file"
            )

        # 8. Create database entry
        try:
            # Determine file type based on MIME type
            if file.content_type.startswith("audio/"):
                file_type = "audio"
            elif file.content_type.startswith("image/"):
                file_type = "image"
            elif file.content_type.startswith("text/"):
                file_type = "text"
            elif file.content_type == "application/pdf":  # PDF treated as image
                file_type = "image"
            else:
                file_type = "audio"  # Default fallback

            # Create relative path for database storage
            relative_path = f"PT_{patient.name}/raw_files/{safe_filename}"

            # Create database record
            db_file = FileModel(
                patient_id=patient_id,
                filename=safe_filename,
                file_type=file_type,
                local_path=relative_path,
                user_metadata=user_metadata,
                processing_status="pending"
            )
            db.add(db_file)
            db.flush()  # Flush to get the ID without committing

            # Store ID before commit
            file_id = db_file.id

            # Get all attributes BEFORE commit (before object is expired)
            response_data = {
                "id": db_file.id,
                "patient_id": db_file.patient_id,
                "filename": db_file.filename,
                "file_type": db_file.file_type,
                "upload_date": db_file.upload_date,
                "processing_status": db_file.processing_status,
                "user_metadata": db_file.user_metadata,
                "local_path": db_file.local_path,
                "transcribed_filename": db_file.transcribed_filename,
                "transcribed_content": db_file.transcribed_content,
                "date_processed": db_file.date_processed,
                "error_message": db_file.error_message,
            }
            logger.info(f"File record created: {file_id} for patient {patient_id}")

            # IMPORTANT: Commit the transaction to persist the file record
            # FastAPI + SQLAlchemy requires explicit db.commit() in endpoints for writes
            try:
                db.commit()
                logger.info(f"Database commit successful for file {file_id}")
            except Exception as commit_error:
                logger.error(f"Commit failed for file {file_id}: {commit_error}", exc_info=True)
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to persist file record: {str(commit_error)}"
                )

            # Sync metadata after successful file upload (Phase 3)
            try:
                metadata_manager = MetadataManager(PATIENTS_BASE_PATH)
                metadata_manager.sync_from_database(patient_id, patient_name, db)
                logger.info(f"Metadata synced after file upload for patient {patient_id}")
            except Exception as metadata_error:
                logger.error(
                    f"Failed to sync metadata after file upload for patient {patient_id}: {metadata_error}",
                    exc_info=True,
                )
                # Don't fail the upload if metadata sync fails, just log it
                # This prevents cascading failures

            # Return dict which Pydantic will validate
            return response_data

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create file record: {str(e)}", exc_info=True)
            # Try to clean up the saved file
            try:
                file_path.unlink()
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up file after DB error: {cleanup_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create file record"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during file upload"
        )


@router.get("/{patient_id}/files", response_model=list[FileResponse])
async def list_patient_files(
    patient_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    List all files for a patient

    - **patient_id**: The patient's ID
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return

    Returns: List of file records
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )

        # Get files for patient
        files = (
            db.query(FileModel)
            .filter(FileModel.patient_id == patient_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        logger.info(f"Retrieved {len(files)} files for patient {patient_id}")
        return files

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing files for patient {patient_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files"
        )


@router.get("/{patient_id}/files/{file_id}", response_model=FileResponse)
async def get_file_details(
    patient_id: int,
    file_id: int,
    db: Session = Depends(get_db),
):
    """
    Get details of a specific file

    - **patient_id**: The patient's ID
    - **file_id**: The file's ID

    Returns: File record details
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )

        # Get file (verify it belongs to patient)
        file_record = (
            db.query(FileModel)
            .filter(FileModel.id == file_id, FileModel.patient_id == patient_id)
            .first()
        )

        if not file_record:
            logger.warning(f"File not found: {file_id} for patient {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with ID {file_id} not found"
            )

        return file_record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving file {file_id} for patient {patient_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve file"
        )


@router.delete("/{patient_id}/files/{file_id}", status_code=status.HTTP_200_OK)
async def delete_file(
    patient_id: int,
    file_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a file

    - **patient_id**: The patient's ID
    - **file_id**: The file's ID

    Returns: Success message
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )

        # Capture patient name early (before db operations that expire the object)
        patient_name = patient.name

        # Get file (verify it belongs to patient)
        file_record = (
            db.query(FileModel)
            .filter(FileModel.id == file_id, FileModel.patient_id == patient_id)
            .first()
        )

        if not file_record:
            logger.warning(f"File not found for deletion: {file_id} for patient {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with ID {file_id} not found"
            )

        # Delete file from filesystem
        try:
            if file_record.local_path:
                file_path = PATIENTS_BASE_PATH / file_record.local_path
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"File deleted from filesystem: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file from filesystem: {str(e)}", exc_info=True)
            # Continue with DB deletion even if filesystem delete fails

        # Delete file from database
        try:
            db.delete(file_record)
            db.commit()
            logger.info(f"File deleted from database: {file_id}")

            # Sync metadata after successful file deletion (Phase 3)
            try:
                metadata_manager = MetadataManager(PATIENTS_BASE_PATH)
                metadata_manager.sync_from_database(patient_id, patient_name, db)
                logger.info(f"Metadata synced after file deletion for patient {patient_id}")
            except Exception as metadata_error:
                logger.error(
                    f"Failed to sync metadata after file deletion for patient {patient_id}: {metadata_error}",
                    exc_info=True,
                )
                # Don't fail the deletion if metadata sync fails, just log it

            return {"message": f"File {file_id} deleted successfully"}
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete file from database: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during file deletion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during file deletion"
        )
