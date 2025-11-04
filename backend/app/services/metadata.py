"""
Metadata Management Service

Handles all metadata.json read/write operations with comprehensive error handling,
logging, and Pydantic validation. Single source of truth for metadata operations.

Each patient has a metadata.json file in their directory (PT_{name}/metadata.json)
that tracks patient-level information and file inventory.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Patient, File
from app.schemas import MetadataResponse, MetadataFileEntry

logger = logging.getLogger(__name__)

# Metadata filename (can be patched in tests)
METADATA_FILENAME = "metadata.json"
METADATA_VERSION = "1.0"


class MetadataManager:
    """
    Centralized metadata management for patient records.

    Responsibilities:
    - Read metadata.json files from disk
    - Write metadata.json files atomically
    - Sync metadata from database
    - Validate metadata structure
    - Handle all errors with detailed logging
    """

    def __init__(self, patients_base_path: Path):
        """
        Initialize MetadataManager.

        Args:
            patients_base_path: Base directory for patient folders (backend/patients/)
        """
        self.patients_base_path = Path(patients_base_path)
        logger.info(f"MetadataManager initialized with base path: {self.patients_base_path}")

    def get_patient_metadata_path(self, patient_id: int, patient_name: str) -> Path:
        """
        Get the full path to a patient's metadata.json file.

        Args:
            patient_id: Patient ID (unused but included for consistency)
            patient_name: Patient's name

        Returns:
            Path to metadata.json file

        Raises:
            ValueError: If patient_name is empty or invalid
        """
        if not patient_name or not patient_name.strip():
            raise ValueError("Patient name cannot be empty")

        # Sanitize directory name (only replace path separators - spaces are allowed)
        safe_name = patient_name.replace("/", "_").replace("\\", "_")
        metadata_path = self.patients_base_path / f"PT_{safe_name}" / METADATA_FILENAME

        return metadata_path

    def read_metadata(self, patient_id: int, patient_name: str) -> Optional[dict]:
        """
        Read metadata.json for a patient from disk.

        Args:
            patient_id: Patient ID
            patient_name: Patient's name

        Returns:
            Metadata dict if file exists, None if doesn't exist

        Raises:
            IOError: If file exists but cannot be read
            json.JSONDecodeError: If JSON is corrupted
            ValueError: If patient_name is invalid
        """
        try:
            metadata_path = self.get_patient_metadata_path(patient_id, patient_name)

            # File doesn't exist yet
            if not metadata_path.exists():
                logger.debug(f"Metadata file does not exist: {metadata_path}")
                return None

            # Read file
            logger.info(f"Reading metadata: {metadata_path}")
            content = metadata_path.read_text(encoding="utf-8")

            # Parse JSON
            metadata = json.loads(content)
            logger.info(f"Successfully read metadata for patient {patient_id}")

            return metadata

        except json.JSONDecodeError as e:
            logger.error(
                f"JSON corruption in metadata file for patient {patient_id}: {str(e)}",
                exc_info=True,
            )
            raise
        except IOError as e:
            logger.error(
                f"Failed to read metadata file for patient {patient_id}: {str(e)}",
                exc_info=True,
            )
            raise
        except ValueError as e:
            logger.error(f"Invalid patient data for patient {patient_id}: {str(e)}", exc_info=True)
            raise

    def write_metadata(self, patient_id: int, patient_name: str, metadata: dict) -> None:
        """
        Write metadata.json for a patient to disk with atomic write.

        Uses temp file first, then atomic rename to prevent corruption.

        Args:
            patient_id: Patient ID
            patient_name: Patient's name
            metadata: Metadata dict to write

        Raises:
            ValueError: If patient_name is invalid or metadata fails validation
            IOError: If write fails
        """
        try:
            # Validate metadata structure first
            self.validate_metadata(metadata)

            # Get path
            metadata_path = self.get_patient_metadata_path(patient_id, patient_name)

            # Ensure directory exists
            metadata_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temp file first (atomic write pattern)
            temp_path = metadata_path.parent / f".{METADATA_FILENAME}.tmp"
            logger.info(f"Writing metadata to temp file: {temp_path}")

            json_content = json.dumps(metadata, indent=2, default=str)
            temp_path.write_text(json_content, encoding="utf-8")

            # Atomic rename
            logger.info(f"Renaming temp file to: {metadata_path}")
            temp_path.replace(metadata_path)

            logger.info(f"Successfully wrote metadata for patient {patient_id}")

        except ValueError as e:
            logger.error(f"Metadata validation failed for patient {patient_id}: {str(e)}")
            raise
        except IOError as e:
            logger.error(f"Failed to write metadata for patient {patient_id}: {str(e)}", exc_info=True)
            # Try to clean up temp file
            try:
                temp_path.unlink(missing_ok=True)
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up temp file: {cleanup_error}")
            raise

    def validate_metadata(self, metadata: dict) -> None:
        """
        Validate metadata structure against schema.

        Args:
            metadata: Metadata dict to validate

        Raises:
            ValueError: If metadata fails validation
        """
        try:
            # Required top-level fields
            required_fields = ["patient_id", "patient_name", "created_date", "updated_date"]
            for field in required_fields:
                if field not in metadata:
                    raise ValueError(f"Missing required field: {field}")

            # Validate version if present
            if "version" in metadata:
                if metadata["version"] != METADATA_VERSION:
                    logger.warning(
                        f"Metadata version mismatch. Expected {METADATA_VERSION}, got {metadata['version']}"
                    )

            # Validate files array if present
            if "files" in metadata:
                if not isinstance(metadata["files"], list):
                    raise ValueError("'files' field must be a list")

                for file_entry in metadata["files"]:
                    if not isinstance(file_entry, dict):
                        raise ValueError("Each file entry must be a dict")

                    # Validate file entry structure
                    file_required = ["file_id", "filename", "type", "uploaded_date", "processing_status"]
                    for field in file_required:
                        if field not in file_entry:
                            raise ValueError(f"File entry missing required field: {field}")

            logger.debug(f"Metadata validation successful")

        except ValueError as e:
            logger.error(f"Metadata validation failed: {str(e)}")
            raise

    def sync_from_database(
        self, patient_id: int, patient_name: str, db: Session
    ) -> dict:
        """
        Build metadata from database records and write to disk.

        This is called after file operations (upload, delete) or patient updates
        to keep metadata.json in sync with the database.

        Args:
            patient_id: Patient ID
            patient_name: Patient's name
            db: Database session

        Returns:
            Updated metadata dict

        Raises:
            ValueError: If patient_name is invalid
            IOError: If write fails
        """
        try:
            logger.info(f"Syncing metadata from database for patient {patient_id}")

            # CRITICAL: Expire session cache to see committed data from route handlers
            # When a file is uploaded, it's committed in the route handler's session
            # Then metadata sync is called in the SAME session
            # Without expire_all(), the session's query cache returns 0 files
            db.expire_all()

            # Get patient notes (if patient exists)
            patient_notes = None
            try:
                patient = db.query(Patient).filter(Patient.id == patient_id).first()
                if patient:
                    patient_notes = patient.notes
            except Exception as e:
                logger.warning(f"Could not retrieve patient notes for {patient_id}: {e}")
                # Continue without notes rather than failing

            # Get all files for patient (now sees committed data after expire_all)
            files = db.query(File).filter(File.patient_id == patient_id).all()

            # Debug logging
            logger.info(f"Query returned {len(files)} files for patient {patient_id}")
            for f in files:
                logger.info(f"  - File ID: {f.id}, Filename: {f.filename}")

            # Build file entries list
            file_entries = []
            for file_record in files:
                entry = {
                    "file_id": file_record.id,
                    "filename": file_record.filename,
                    "type": file_record.file_type,
                    "uploaded_date": file_record.upload_date.isoformat() if file_record.upload_date else None,
                    "user_metadata": file_record.user_metadata,
                    "processing_status": file_record.processing_status,
                }
                file_entries.append(entry)

            now = datetime.utcnow()

            # Build metadata dict
            metadata = {
                "version": METADATA_VERSION,
                "patient_id": patient_id,
                "patient_name": patient_name,
                "created_date": now.isoformat(),
                "updated_date": now.isoformat(),
                "notes": patient_notes,
                "files": file_entries,
            }

            logger.info(f"Built metadata with {len(file_entries)} files for patient {patient_id}")

            # Write to disk
            self.write_metadata(patient_id, patient_name, metadata)

            return metadata

        except ValueError as e:
            logger.error(f"Failed to sync metadata for patient {patient_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error syncing metadata for patient {patient_id}: {str(e)}",
                exc_info=True,
            )
            raise

    def get_metadata_response(
        self, patient_id: int, patient_name: str, db: Session
    ) -> MetadataResponse:
        """
        Get metadata as a validated Pydantic response model.

        Reads from disk if available, otherwise syncs from database.

        Args:
            patient_id: Patient ID
            patient_name: Patient's name
            db: Database session

        Returns:
            MetadataResponse with validated structure

        Raises:
            ValueError: If patient not found
            IOError: If read/write fails
        """
        try:
            # Try to read from disk first
            metadata = self.read_metadata(patient_id, patient_name)

            # If doesn't exist, sync from database
            if metadata is None:
                logger.info(f"Metadata file not found, syncing from database for patient {patient_id}")
                metadata = self.sync_from_database(patient_id, patient_name, db)

            # Convert to validated response model
            response = MetadataResponse(
                patient_id=metadata["patient_id"],
                patient_name=metadata["patient_name"],
                created_date=datetime.fromisoformat(metadata["created_date"])
                if isinstance(metadata["created_date"], str)
                else metadata["created_date"],
                updated_date=datetime.fromisoformat(metadata["updated_date"])
                if isinstance(metadata["updated_date"], str)
                else metadata["updated_date"],
                notes=metadata.get("notes"),
                files=[MetadataFileEntry(**entry) for entry in metadata.get("files", [])],
            )

            return response

        except ValueError as e:
            logger.error(f"Failed to get metadata response for patient {patient_id}: {str(e)}")
            raise

    def delete_metadata(self, patient_id: int, patient_name: str) -> None:
        """
        Delete metadata.json file for a patient.

        Called when patient is deleted.

        Args:
            patient_id: Patient ID
            patient_name: Patient's name

        Raises:
            IOError: If deletion fails
        """
        try:
            metadata_path = self.get_patient_metadata_path(patient_id, patient_name)

            if metadata_path.exists():
                logger.info(f"Deleting metadata file: {metadata_path}")
                metadata_path.unlink()
                logger.info(f"Successfully deleted metadata for patient {patient_id}")
            else:
                logger.warning(f"Metadata file not found for deletion: {metadata_path}")

        except IOError as e:
            logger.error(f"Failed to delete metadata for patient {patient_id}: {str(e)}", exc_info=True)
            raise
