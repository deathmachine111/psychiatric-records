"""
Notion Export API Routes
Endpoints for exporting processed psychiatric records to Notion
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patient, File as FileModel
from app.services.notion import NotionExporter

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/patients", tags=["notion"])


@router.post("/{patient_id}/export/{file_id}")
async def export_file_to_notion(
    patient_id: int,
    file_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Export a single processed file to Notion database

    Args:
        patient_id: Patient ID
        file_id: File ID to export

    Returns:
        Dictionary with notion_page_id and export status
    """
    try:
        # 1. Validate patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            logger.warning(f"Patient not found for Notion export: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )

        # 2. Validate file exists and belongs to patient
        db_file = db.query(FileModel).filter(
            FileModel.id == file_id,
            FileModel.patient_id == patient_id
        ).first()

        if not db_file:
            logger.warning(f"File not found for export: {file_id} for patient {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with ID {file_id} not found for this patient"
            )

        # 3. Check if file has been processed
        if db_file.processing_status != "completed":
            logger.warning(
                f"Attempted to export unprocessed file: {file_id} "
                f"(status: {db_file.processing_status})"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File has not been processed yet (status: {db_file.processing_status})"
            )

        if not db_file.transcribed_content:
            logger.warning(f"File {file_id} has no transcribed content")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File has no transcribed content to export"
            )

        logger.info(f"Exporting file {file_id} to Notion for patient {patient_id}")

        # 4. Initialize Notion exporter
        try:
            exporter = NotionExporter()
        except (ValueError, ImportError) as e:
            logger.error(f"Failed to initialize Notion exporter: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Notion integration not properly configured: {str(e)}"
            )

        # 5. Export to Notion
        try:
            result = exporter.export_to_notion(
                patient_name=patient.name,
                file_id=file_id,
                filename=db_file.filename,
                file_type=db_file.file_type,
                transcribed_content=db_file.transcribed_content,
                upload_date=db_file.upload_date,
                processed_date=db_file.date_processed,
                user_metadata=db_file.user_metadata,
                patient_notes=patient.notes
            )

            logger.info(f"Successfully exported file {file_id} to Notion: {result['notion_page_id']}")
            return result

        except Exception as e:
            logger.error(f"Notion export failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Notion export failed: {str(e)}"
            )

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error during Notion export: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Notion export failed: internal server error"
        )


@router.post("/{patient_id}/export-all")
async def export_all_files_to_notion(
    patient_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Export all processed files for a patient to Notion

    Args:
        patient_id: Patient ID

    Returns:
        Dictionary with list of exported page IDs and status
    """
    try:
        # 1. Validate patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            logger.warning(f"Patient not found for batch Notion export: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )

        # 2. Get all processed files for patient
        processed_files = db.query(FileModel).filter(
            FileModel.patient_id == patient_id,
            FileModel.processing_status == "completed"
        ).all()

        if not processed_files:
            logger.warning(f"No processed files found for patient {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No processed files found for this patient"
            )

        logger.info(f"Exporting {len(processed_files)} files to Notion for patient {patient_id}")

        # 3. Prepare file data for batch export
        files_to_export = []
        for db_file in processed_files:
            if db_file.transcribed_content:  # Only export files with content
                files_to_export.append({
                    "file_id": db_file.id,
                    "filename": db_file.filename,
                    "file_type": db_file.file_type,
                    "transcribed_content": db_file.transcribed_content,
                    "upload_date": db_file.upload_date,
                    "processed_date": db_file.date_processed,
                    "user_metadata": db_file.user_metadata,
                    "patient_notes": patient.notes
                })

        if not files_to_export:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files with transcribed content found for export"
            )

        # 4. Initialize Notion exporter
        try:
            exporter = NotionExporter()
        except (ValueError, ImportError) as e:
            logger.error(f"Failed to initialize Notion exporter: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Notion integration not properly configured: {str(e)}"
            )

        # 5. Export batch to Notion
        try:
            result = exporter.export_batch(
                patient_name=patient.name,
                files=files_to_export
            )

            logger.info(
                f"Batch export complete for patient {patient_id}: "
                f"{result['exported_count']} successful, {result['failed_count']} failed"
            )
            return result

        except Exception as e:
            logger.error(f"Batch Notion export failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Notion export failed: {str(e)}"
            )

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error during batch Notion export: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Notion export failed: internal server error"
        )
