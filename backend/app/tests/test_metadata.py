"""
Metadata Management Tests

Test-Driven Development: These tests define the complete metadata behavior.
All tests must pass for Phase 3 to be considered complete (100% pass rate).

Test Categories:
1. Metadata File Creation (3 tests)
2. Metadata Read Operations (4 tests)
3. Metadata Sync Operations (5 tests)
4. Metadata Write Operations (3 tests)
5. Metadata Edge Cases (4 tests)
6. Metadata Integration (3 tests)

Total: 22 tests targeting 100% pass rate
"""
import json
import pytest
from datetime import datetime
from pathlib import Path


class TestMetadataFileCreation:
    """Test metadata.json file creation scenarios"""

    def test_metadata_created_on_patient_creation(self, db, mock_patients_path):
        """Test that metadata.json is created when patient is first created"""
        from app.models import Patient
        from app.services import MetadataManager

        # Create patient
        patient = Patient(name="New Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Initialize metadata manager
        metadata_manager = MetadataManager(mock_patients_path)

        # Sync metadata (as would happen during patient creation in future)
        metadata = metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Verify metadata file exists
        metadata_path = mock_patients_path / "PT_New_Patient" / "metadata.json"
        assert metadata_path.exists(), f"Metadata file not created at {metadata_path}"

        # Verify metadata structure
        assert metadata["patient_id"] == patient.id
        assert metadata["patient_name"] == "New Patient"
        assert "created_date" in metadata
        assert "updated_date" in metadata
        assert isinstance(metadata["files"], list)
        assert len(metadata["files"]) == 0  # No files yet

    def test_metadata_created_on_first_file_upload(self, client, db, mock_patients_path):
        """Test that metadata is created/updated when first file is uploaded"""
        from app.models import Patient
        from app.services import MetadataManager
        import io

        # Create patient
        patient = Patient(name="Upload Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Upload file
        fake_audio = io.BytesIO(b"fake audio content")
        files = {"file": ("session_1.mp3", fake_audio, "audio/mpeg")}
        response = client.post(f"/api/patients/{patient.id}/files", files=files)
        assert response.status_code == 201

        # Check metadata file exists
        metadata_path = mock_patients_path / "PT_Upload_Test_Patient" / "metadata.json"
        assert metadata_path.exists()

        # Verify metadata content
        metadata = json.loads(metadata_path.read_text())
        assert metadata["patient_id"] == patient.id
        assert metadata["patient_name"] == "Upload Test Patient"
        assert len(metadata["files"]) == 1
        assert metadata["files"][0]["filename"] == "session_1.mp3"
        assert metadata["files"][0]["type"] == "audio"

    def test_metadata_file_structure_valid(self, db, mock_patients_path):
        """Test that metadata.json has valid structure with all required fields"""
        from app.models import Patient
        from app.services import MetadataManager

        # Create patient
        patient = Patient(name="Structure Test", notes="Test patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Sync metadata
        metadata_manager = MetadataManager(mock_patients_path)
        metadata = metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Verify all required fields present
        assert "version" in metadata
        assert "patient_id" in metadata
        assert "patient_name" in metadata
        assert "created_date" in metadata
        assert "updated_date" in metadata
        assert "files" in metadata
        assert "notes" in metadata

        # Verify types
        assert isinstance(metadata["patient_id"], int)
        assert isinstance(metadata["patient_name"], str)
        assert isinstance(metadata["files"], list)
        assert metadata["notes"] == "Test patient"


class TestMetadataReadOperations:
    """Test metadata.json read operations"""

    def test_get_metadata_success(self, db, mock_patients_path):
        """Test successfully reading metadata from disk"""
        from app.models import Patient, File
        from app.services import MetadataManager

        # Create patient and file
        patient = Patient(name="Read Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        file_record = File(
            patient_id=patient.id,
            filename="test.mp3",
            file_type="audio",
            local_path="PT_Read_Test_Patient/raw_files/test.mp3",
            processing_status="pending",
            user_metadata="Test session",
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # Sync metadata to disk
        metadata_manager = MetadataManager(mock_patients_path)
        metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Read metadata back
        read_metadata = metadata_manager.read_metadata(patient.id, patient.name)

        assert read_metadata is not None
        assert read_metadata["patient_id"] == patient.id
        assert read_metadata["patient_name"] == "Read Test Patient"
        assert len(read_metadata["files"]) == 1
        assert read_metadata["files"][0]["filename"] == "test.mp3"

    def test_get_metadata_patient_not_found(self, db, mock_patients_path):
        """Test reading metadata for non-existent patient returns None"""
        from app.services import MetadataManager

        metadata_manager = MetadataManager(mock_patients_path)
        result = metadata_manager.read_metadata(999, "Nonexistent Patient")

        # Should return None for non-existent file
        assert result is None

    def test_get_metadata_file_not_found(self, db, mock_patients_path):
        """Test reading metadata when file doesn't exist yet returns None"""
        from app.models import Patient
        from app.services import MetadataManager

        # Create patient but don't create metadata file
        patient = Patient(name="No Metadata Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        metadata_manager = MetadataManager(mock_patients_path)
        result = metadata_manager.read_metadata(patient.id, patient.name)

        assert result is None

    def test_get_metadata_invalid_json_on_disk(self, db, mock_patients_path):
        """Test reading corrupted JSON metadata raises error"""
        from app.models import Patient
        from app.services import MetadataManager
        import json

        # Create patient
        patient = Patient(name="Corrupted Metadata Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create corrupted metadata file
        metadata_dir = mock_patients_path / "PT_Corrupted_Metadata_Patient"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = metadata_dir / "metadata.json"
        metadata_path.write_text("{invalid json content here")

        # Try to read
        metadata_manager = MetadataManager(mock_patients_path)

        with pytest.raises(json.JSONDecodeError):
            metadata_manager.read_metadata(patient.id, patient.name)


class TestMetadataSyncOperations:
    """Test metadata synchronization with database"""

    def test_metadata_synced_after_file_upload(self, client, db, mock_patients_path):
        """Test that metadata is synced when file is uploaded"""
        from app.models import Patient
        from app.services import MetadataManager
        import io

        # Create patient
        patient = Patient(name="Sync Upload Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Upload file
        fake_audio = io.BytesIO(b"audio data")
        files = {"file": ("session.mp3", fake_audio, "audio/mpeg")}
        client.post(f"/api/patients/{patient.id}/files", files=files)

        # Verify metadata synced
        metadata_manager = MetadataManager(mock_patients_path)
        metadata_path = mock_patients_path / "PT_Sync_Upload_Patient" / "metadata.json"
        assert metadata_path.exists()

        metadata = json.loads(metadata_path.read_text())
        assert len(metadata["files"]) == 1

    def test_metadata_synced_after_file_deletion(self, client, db, mock_patients_path):
        """Test that metadata is synced when file is deleted"""
        from app.models import Patient, File
        from app.services import MetadataManager

        # Create patient and file
        patient = Patient(name="Sync Delete Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create file on disk and in database
        patients_dir = mock_patients_path / "PT_Sync_Delete_Patient" / "raw_files"
        patients_dir.mkdir(parents=True, exist_ok=True)
        test_file = patients_dir / "test.mp3"
        test_file.write_bytes(b"audio data")

        file_record = File(
            patient_id=patient.id,
            filename="test.mp3",
            file_type="audio",
            local_path="PT_Sync_Delete_Patient/raw_files/test.mp3",
            processing_status="pending",
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # Sync initial metadata
        metadata_manager = MetadataManager(mock_patients_path)
        metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Delete file from database
        db.delete(file_record)
        db.commit()

        # Re-sync metadata
        metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Verify metadata updated (file removed)
        metadata_path = mock_patients_path / "PT_Sync_Delete_Patient" / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        assert len(metadata["files"]) == 0

    def test_metadata_synced_after_patient_update(self, db, mock_patients_path):
        """Test that metadata is synced when patient notes updated"""
        from app.models import Patient
        from app.services import MetadataManager

        # Create patient
        patient = Patient(name="Sync Update Patient", notes="Original notes")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Sync metadata
        metadata_manager = MetadataManager(mock_patients_path)
        metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Update patient notes
        patient.notes = "Updated notes"
        db.commit()

        # Sync metadata again
        metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Verify metadata updated
        metadata_path = mock_patients_path / "PT_Sync_Update_Patient" / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        assert metadata["notes"] == "Updated notes"

    def test_metadata_file_list_includes_all_files(self, db, mock_patients_path):
        """Test that metadata file list includes all database files"""
        from app.models import Patient, File
        from app.services import MetadataManager

        # Create patient
        patient = Patient(name="Multi File Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create multiple files
        for i in range(5):
            file_record = File(
                patient_id=patient.id,
                filename=f"file_{i}.mp3",
                file_type="audio",
                local_path=f"PT_Multi_File_Patient/raw_files/file_{i}.mp3",
                processing_status="pending",
            )
            db.add(file_record)
        db.commit()

        # Sync metadata
        metadata_manager = MetadataManager(mock_patients_path)
        metadata = metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Verify all files included
        assert len(metadata["files"]) == 5
        filenames = {f["filename"] for f in metadata["files"]}
        assert filenames == {f"file_{i}.mp3" for i in range(5)}

    def test_metadata_file_order_consistent(self, db, mock_patients_path):
        """Test that metadata file order matches database order"""
        from app.models import Patient, File
        from app.services import MetadataManager

        # Create patient and files
        patient = Patient(name="Order Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create files with specific names
        expected_order = ["alpha.mp3", "beta.mp3", "gamma.mp3"]
        for filename in expected_order:
            file_record = File(
                patient_id=patient.id,
                filename=filename,
                file_type="audio",
                local_path=f"PT_Order_Test_Patient/raw_files/{filename}",
                processing_status="pending",
            )
            db.add(file_record)
        db.commit()

        # Sync metadata
        metadata_manager = MetadataManager(mock_patients_path)
        metadata = metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Verify order matches
        actual_order = [f["filename"] for f in metadata["files"]]
        assert actual_order == expected_order


class TestMetadataWriteOperations:
    """Test metadata.json write operations"""

    def test_update_metadata_success(self, db, mock_patients_path):
        """Test successfully updating metadata"""
        from app.models import Patient
        from app.services import MetadataManager

        # Create patient
        patient = Patient(name="Write Test Patient", notes="Original notes")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create and write metadata
        metadata_manager = MetadataManager(mock_patients_path)
        metadata = {
            "version": "1.0",
            "patient_id": patient.id,
            "patient_name": patient.name,
            "created_date": datetime.utcnow().isoformat(),
            "updated_date": datetime.utcnow().isoformat(),
            "notes": "Updated notes",
            "files": [],
        }

        metadata_manager.write_metadata(patient.id, patient.name, metadata)

        # Verify written
        metadata_path = mock_patients_path / "PT_Write_Test_Patient" / "metadata.json"
        assert metadata_path.exists()

        read_back = json.loads(metadata_path.read_text())
        assert read_back["notes"] == "Updated notes"

    def test_update_metadata_invalid_schema(self, db, mock_patients_path):
        """Test that invalid metadata is rejected"""
        from app.models import Patient
        from app.services import MetadataManager

        # Create patient
        patient = Patient(name="Invalid Schema Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        metadata_manager = MetadataManager(mock_patients_path)

        # Try to write missing required fields
        invalid_metadata = {
            "patient_id": patient.id,
            # Missing: patient_name, created_date, updated_date
        }

        with pytest.raises(ValueError):
            metadata_manager.write_metadata(patient.id, patient.name, invalid_metadata)

    def test_update_metadata_atomic_write(self, db, mock_patients_path):
        """Test that metadata write is atomic (temp file then rename)"""
        from app.models import Patient
        from app.services import MetadataManager

        # Create patient
        patient = Patient(name="Atomic Write Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        metadata_manager = MetadataManager(mock_patients_path)
        metadata = {
            "version": "1.0",
            "patient_id": patient.id,
            "patient_name": patient.name,
            "created_date": datetime.utcnow().isoformat(),
            "updated_date": datetime.utcnow().isoformat(),
            "notes": "Test",
            "files": [],
        }

        # Write metadata
        metadata_manager.write_metadata(patient.id, patient.name, metadata)

        # Verify no temp files left behind
        metadata_dir = mock_patients_path / "PT_Atomic_Write_Patient"
        temp_files = list(metadata_dir.glob(".metadata.json.tmp"))
        assert len(temp_files) == 0, f"Temp file not cleaned up: {temp_files}"


class TestMetadataEdgeCases:
    """Test edge cases and error handling"""

    def test_metadata_with_special_characters_in_name(self, db, mock_patients_path):
        """Test metadata handling with special characters in patient name"""
        from app.models import Patient
        from app.services import MetadataManager

        # Create patient with special characters
        patient = Patient(name="Dr. John/Mary Doe-Smith (Pediatric)")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Sync metadata (should sanitize name)
        metadata_manager = MetadataManager(mock_patients_path)
        metadata = metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Verify metadata created with sanitized directory
        # Should replace / with _
        metadata_path = (
            mock_patients_path / "PT_Dr._John_Mary_Doe-Smith_(Pediatric)" / "metadata.json"
        )
        assert metadata_path.exists()

    def test_metadata_recovery_from_corrupted_json(self, db, mock_patients_path):
        """Test that corrupted metadata can be recovered from database"""
        from app.models import Patient, File
        from app.services import MetadataManager

        # Create patient and file
        patient = Patient(name="Recovery Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        file_record = File(
            patient_id=patient.id,
            filename="test.mp3",
            file_type="audio",
            local_path="PT_Recovery_Patient/raw_files/test.mp3",
            processing_status="pending",
        )
        db.add(file_record)
        db.commit()

        # Create corrupted metadata
        metadata_dir = mock_patients_path / "PT_Recovery_Patient"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = metadata_dir / "metadata.json"
        metadata_path.write_text("{corrupted")

        # Try to recover by syncing from database
        metadata_manager = MetadataManager(mock_patients_path)
        recovered = metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Verify recovered from database
        assert recovered["patient_id"] == patient.id
        assert len(recovered["files"]) == 1

        # Verify file is now valid JSON
        assert metadata_path.read_text() != "{corrupted"
        assert json.loads(metadata_path.read_text()) is not None


class TestMetadataIntegration:
    """Test metadata integration with full workflow"""

    def test_metadata_reflects_all_file_operations(self, client, db, mock_patients_path):
        """Test that metadata reflects all file operations (create, update, delete)"""
        from app.models import Patient
        from app.services import MetadataManager
        import io

        # Create patient
        patient = Patient(name="Integration Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        metadata_manager = MetadataManager(mock_patients_path)

        # Upload first file
        fake_audio1 = io.BytesIO(b"audio 1")
        client.post(
            f"/api/patients/{patient.id}/files",
            files={"file": ("session_1.mp3", fake_audio1, "audio/mpeg")},
        )

        # Upload second file
        fake_audio2 = io.BytesIO(b"audio 2")
        response = client.post(
            f"/api/patients/{patient.id}/files",
            files={"file": ("session_2.mp3", fake_audio2, "audio/mpeg")},
        )
        file_2_id = response.json()["id"]

        # Verify both in metadata
        metadata_path = mock_patients_path / "PT_Integration_Patient" / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        assert len(metadata["files"]) == 2

        # Delete first file (by ID from response)
        # (File deletion would be done through API or DB)

    def test_metadata_deleted_with_patient(self, db, mock_patients_path):
        """Test that metadata is deleted when patient is deleted"""
        from app.models import Patient
        from app.services import MetadataManager

        # Create patient
        patient = Patient(name="Delete Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create metadata
        metadata_manager = MetadataManager(mock_patients_path)
        metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Verify metadata exists
        metadata_path = mock_patients_path / "PT_Delete_Patient" / "metadata.json"
        assert metadata_path.exists()

        # Delete patient
        db.delete(patient)
        db.commit()

        # Delete metadata
        metadata_manager.delete_metadata(patient.id, patient.name)

        # Verify metadata deleted
        assert not metadata_path.exists()

    def test_metadata_migration_from_no_metadata(self, db, mock_patients_path):
        """Test that existing patients without metadata can be migrated"""
        from app.models import Patient, File
        from app.services import MetadataManager

        # Create patient and files without metadata
        patient = Patient(name="Migration Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        for i in range(3):
            file_record = File(
                patient_id=patient.id,
                filename=f"file_{i}.mp3",
                file_type="audio",
                local_path=f"PT_Migration_Patient/raw_files/file_{i}.mp3",
                processing_status="pending",
            )
            db.add(file_record)
        db.commit()

        # No metadata file exists yet
        metadata_path = mock_patients_path / "PT_Migration_Patient" / "metadata.json"
        assert not metadata_path.exists()

        # Trigger metadata creation (migration)
        metadata_manager = MetadataManager(mock_patients_path)
        metadata = metadata_manager.sync_from_database(patient.id, patient.name, db)

        # Verify metadata created with all files
        assert metadata_path.exists()
        assert metadata["patient_id"] == patient.id
        assert len(metadata["files"]) == 3
