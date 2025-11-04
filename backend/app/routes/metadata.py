"""
Metadata Management API Routes

Endpoints for managing patient metadata (metadata.json files).
Provides full CRUD operations for patient-level metadata.
"""
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patient
from app.schemas import MetadataResponse, MetadataCreate
from app.services import MetadataManager

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/patients", tags=["metadata"])

# Base path for patient files (can be patched in tests)
PATIENTS_BASE_PATH = Path(__file__).parent.parent.parent / "patients"


def get_metadata_manager() -> MetadataManager:
    """
    Dependency injection for MetadataManager.

    Returns:
        MetadataManager instance
    """
    return MetadataManager(PATIENTS_BASE_PATH)


# ===== API Endpoints =====


@router.get("/{patient_id}/metadata", response_model=MetadataResponse)
async def get_metadata(
    patient_id: int,
    db: Session = Depends(get_db),
    metadata_manager: MetadataManager = Depends(get_metadata_manager),
) -> MetadataResponse:
    """
    Get metadata for a patient.

    Returns metadata from disk, or syncs from database if not found.

    Args:
        patient_id: The patient's ID
        db: Database session
        metadata_manager: MetadataManager instance

    Returns:
        MetadataResponse with patient metadata

    Raises:
        HTTPException 404: Patient not found
        HTTPException 500: Failed to read/sync metadata
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            logger.warning(f"Patient not found for metadata GET: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found",
            )

        logger.info(f"Getting metadata for patient {patient_id}")

        # Get metadata (reads from disk or syncs from database)
        response = metadata_manager.get_metadata_response(patient_id, patient.name, db)

        logger.info(f"Successfully retrieved metadata for patient {patient_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving metadata for patient {patient_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metadata",
        )


@router.post("/{patient_id}/metadata", response_model=MetadataResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_metadata(
    patient_id: int,
    metadata_create: MetadataCreate,
    db: Session = Depends(get_db),
    metadata_manager: MetadataManager = Depends(get_metadata_manager),
) -> MetadataResponse:
    """
    Create or update metadata for a patient.

    Updates the notes field of existing metadata, or creates new metadata
    if it doesn't exist yet.

    Args:
        patient_id: The patient's ID
        metadata_create: Metadata creation/update request
        db: Database session
        metadata_manager: MetadataManager instance

    Returns:
        Updated MetadataResponse

    Raises:
        HTTPException 404: Patient not found
        HTTPException 400: Invalid metadata
        HTTPException 500: Failed to write metadata
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            logger.warning(f"Patient not found for metadata POST: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found",
            )

        logger.info(f"Creating/updating metadata for patient {patient_id}")

        # Sync metadata from database (to get all files and current structure)
        metadata = metadata_manager.sync_from_database(patient_id, patient.name, db)

        # Update notes if provided
        if metadata_create.notes is not None:
            metadata["notes"] = metadata_create.notes
            logger.info(f"Updated notes for patient {patient_id}")

        # Write updated metadata
        metadata_manager.write_metadata(patient_id, patient.name, metadata)

        # Return as validated response
        response = metadata_manager.get_metadata_response(patient_id, patient.name, db)

        logger.info(f"Successfully created/updated metadata for patient {patient_id}")
        return response

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metadata: {str(e)}",
        )
    except Exception as e:
        logger.error(
            f"Error creating/updating metadata for patient {patient_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create/update metadata",
        )


@router.put("/{patient_id}/metadata/{field}", response_model=MetadataResponse)
async def update_metadata_field(
    patient_id: int,
    field: str,
    value: Any,
    db: Session = Depends(get_db),
    metadata_manager: MetadataManager = Depends(get_metadata_manager),
) -> MetadataResponse:
    """
    Update a specific field in patient metadata.

    Currently supports updating the 'notes' field.

    Args:
        patient_id: The patient's ID
        field: The field name to update (e.g., 'notes')
        value: The new value for the field
        db: Database session
        metadata_manager: MetadataManager instance

    Returns:
        Updated MetadataResponse

    Raises:
        HTTPException 404: Patient not found
        HTTPException 400: Invalid field name
        HTTPException 500: Failed to write metadata
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            logger.warning(f"Patient not found for metadata PUT: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found",
            )

        # Validate field name (whitelist to prevent arbitrary updates)
        allowed_fields = ["notes"]
        if field not in allowed_fields:
            logger.warning(f"Invalid field name for update: {field}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' cannot be updated. Allowed fields: {', '.join(allowed_fields)}",
            )

        logger.info(f"Updating field '{field}' for patient {patient_id}")

        # Get current metadata
        metadata = metadata_manager.read_metadata(patient_id, patient.name)
        if metadata is None:
            # Sync from database if doesn't exist
            logger.info(f"Metadata not found, syncing from database for patient {patient_id}")
            metadata = metadata_manager.sync_from_database(patient_id, patient.name, db)

        # Update field
        metadata[field] = value
        logger.info(f"Updated field '{field}' for patient {patient_id}")

        # Write updated metadata
        metadata_manager.write_metadata(patient_id, patient.name, metadata)

        # Return as validated response
        response = metadata_manager.get_metadata_response(patient_id, patient.name, db)

        logger.info(f"Successfully updated metadata field '{field}' for patient {patient_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating metadata field '{field}' for patient {patient_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update metadata",
        )


@router.delete("/{patient_id}/metadata", status_code=status.HTTP_200_OK)
async def delete_metadata(
    patient_id: int,
    db: Session = Depends(get_db),
    metadata_manager: MetadataManager = Depends(get_metadata_manager),
) -> dict:
    """
    Delete metadata for a patient.

    Removes the metadata.json file from disk.

    Args:
        patient_id: The patient's ID
        db: Database session
        metadata_manager: MetadataManager instance

    Returns:
        Success message

    Raises:
        HTTPException 404: Patient not found
        HTTPException 500: Failed to delete metadata
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            logger.warning(f"Patient not found for metadata DELETE: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found",
            )

        logger.info(f"Deleting metadata for patient {patient_id}")

        # Delete metadata
        metadata_manager.delete_metadata(patient_id, patient.name)

        logger.info(f"Successfully deleted metadata for patient {patient_id}")
        return {"message": f"Metadata for patient {patient_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting metadata for patient {patient_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete metadata",
        )
