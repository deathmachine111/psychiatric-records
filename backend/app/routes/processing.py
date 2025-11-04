"""
File Processing API Routes
Endpoints for Gemini AI transcription, OCR, and text cleaning
"""
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patient, File as FileModel
from app.schemas import FileResponse
from app.services.processing import GeminiProcessor

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/patients", tags=["processing"])

# Initialize Gemini processor
processor = GeminiProcessor()

# Base path for patient files
PATIENTS_BASE_PATH = Path(__file__).parent.parent.parent / "patients"


@router.post("/{patient_id}/process/{file_id}", response_model=FileResponse)
async def process_file(
    patient_id: int,
    file_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Process a file with Gemini AI

    Supports:
    - Audio files → transcription
    - Images/PDFs → OCR text extraction
    - Text files → cleaning and standardization

    Args:
        patient_id: Patient ID
        file_id: File ID to process

    Returns:
        Updated file record with transcribed_content
    """
    try:
        # 1. Validate patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            logger.warning(f"Patient not found for processing: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )

        patient_name = patient.name

        # 2. Validate file exists and belongs to patient
        db_file = db.query(FileModel).filter(
            FileModel.id == file_id,
            FileModel.patient_id == patient_id
        ).first()

        if not db_file:
            logger.warning(f"File not found: {file_id} for patient {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with ID {file_id} not found for this patient"
            )

        logger.info(f"Processing file {file_id} ({db_file.file_type}) for patient {patient_id}")

        # 3. Update status to 'processing'
        db_file.processing_status = "processing"
        db.commit()

        # 4. Construct file path
        file_path = PATIENTS_BASE_PATH / db_file.local_path

        if not file_path.exists():
            db_file.processing_status = "failed"
            db_file.error_message = f"File not found on disk: {file_path}"
            db.commit()
            logger.error(f"File not found on disk: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File not found on disk"
            )

        # 5. Process based on file type
        try:
            if db_file.file_type == "audio":
                logger.info(f"Transcribing audio: {file_path}")
                transcribed_content = processor.transcribe_audio(str(file_path))

            elif db_file.file_type == "image":
                logger.info(f"Extracting text from image/PDF: {file_path}")
                transcribed_content = processor.ocr_image(str(file_path))

            elif db_file.file_type == "text":
                logger.info(f"Cleaning text: {file_path}")
                transcribed_content = processor.clean_text(str(file_path))

            else:
                raise ValueError(f"Unsupported file type: {db_file.file_type}")

            # 6. Update file record with results
            db_file.transcribed_content = transcribed_content
            db_file.processing_status = "completed"
            db_file.date_processed = datetime.utcnow()
            db.commit()
            db.refresh(db_file)

            logger.info(
                f"File {file_id} processing complete: {len(transcribed_content)} characters"
            )

            # Return response
            return {
                "id": db_file.id,
                "patient_id": db_file.patient_id,
                "filename": db_file.filename,
                "file_type": db_file.file_type,
                "local_path": db_file.local_path,
                "user_metadata": db_file.user_metadata,
                "upload_date": db_file.upload_date,
                "processing_status": db_file.processing_status,
                "transcribed_content": db_file.transcribed_content,
                "date_processed": db_file.date_processed,
                "error_message": db_file.error_message
            }

        except Exception as e:
            # Update status to 'failed' with error message
            db_file.processing_status = "failed"
            db_file.error_message = str(e)
            db.commit()

            logger.error(
                f"File {file_id} processing failed: {str(e)}",
                exc_info=True
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing failed: {str(e)}"
            )

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(
            f"Unexpected error processing file {file_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Processing failed: internal server error"
        )


@router.get("/{patient_id}/processing-status")
async def get_processing_status(
    patient_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get processing status for all files of a patient

    Args:
        patient_id: Patient ID

    Returns:
        Dictionary with file IDs as keys and processing status as values
    """
    try:
        # 1. Validate patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )

        # 2. Get all files for patient
        files = db.query(FileModel).filter(FileModel.patient_id == patient_id).all()

        # 3. Build status response
        status_dict = {}
        for file in files:
            status_dict[file.id] = {
                "filename": file.filename,
                "file_type": file.file_type,
                "status": file.processing_status,
                "uploaded_date": file.upload_date,
                "processed_date": file.date_processed,
                "error": file.error_message
            }

        return {
            "patient_id": patient_id,
            "files": status_dict
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get processing status"
        )
