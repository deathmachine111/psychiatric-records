"""
Patient API Routes
Endpoints for patient CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.database import get_db
from app.models import Patient
from app.schemas import PatientCreate, PatientUpdate, PatientResponse, PatientDetailResponse

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new patient

    - **name**: Patient's full name (required, must be unique)
    - **notes**: Clinical notes (optional)

    Returns: Created patient with ID and timestamps
    """
    try:
        # Create new patient
        db_patient = Patient(
            name=patient.name,
            notes=patient.notes
        )
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)

        logger.info(f"Created patient: {db_patient.id} - {db_patient.name}")
        return db_patient

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Duplicate patient name: {patient.name}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Patient with name '{patient.name}' already exists"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating patient: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient"
        )


@router.get("", response_model=list[PatientResponse])
async def get_all_patients(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all patients

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (pagination)

    Returns: List of patients
    """
    try:
        patients = db.query(Patient).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(patients)} patients")
        return patients
    except Exception as e:
        logger.error(f"Error fetching patients: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch patients"
        )


@router.get("/{patient_id}", response_model=PatientDetailResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a patient by ID

    - **patient_id**: The patient's ID

    Returns: Patient details including timestamps
    """
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            logger.warning(f"Patient not found: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        return patient
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient {patient_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch patient"
        )


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a patient

    - **patient_id**: The patient's ID
    - **name**: Patient's full name (required)
    - **notes**: Clinical notes (optional)

    Returns: Updated patient
    """
    try:
        # Find patient
        db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not db_patient:
            logger.warning(f"Patient not found for update: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )

        # Update fields
        db_patient.name = patient_update.name
        db_patient.notes = patient_update.notes

        db.commit()
        db.refresh(db_patient)

        logger.info(f"Updated patient: {patient_id}")
        return db_patient

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Duplicate patient name during update: {patient_update.name}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Patient with name '{patient_update.name}' already exists"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating patient {patient_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient"
        )


@router.delete("/{patient_id}", status_code=status.HTTP_200_OK)
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a patient

    - **patient_id**: The patient's ID

    Returns: Success message
    """
    try:
        # Find patient
        db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not db_patient:
            logger.warning(f"Patient not found for deletion: {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )

        # Delete patient
        db.delete(db_patient)
        db.commit()

        logger.info(f"Deleted patient: {patient_id}")
        return {"message": f"Patient {patient_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting patient {patient_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete patient"
        )
