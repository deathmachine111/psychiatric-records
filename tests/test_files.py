"""
File Upload Tests
Test-Driven Development: These tests MUST FAIL initially
Then we implement code to make them PASS
"""
import io
import pytest


class TestFileUpload:
    """Test file upload endpoints"""

    def test_upload_audio_mp3_success(self, client, db, mock_patients_path):
        """Test uploading a valid MP3 file"""
        # Create patient
        from app.models import Patient
        patient = Patient(name="Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create fake audio file
        fake_audio = io.BytesIO(b"fake mp3 audio data")
        files = {"file": ("session_1.mp3", fake_audio, "audio/mpeg")}

        # Upload file
        response = client.post(
            f"/api/patients/{patient.id}/files",
            files=files
        )

        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "session_1.mp3"
        assert data["file_type"] == "audio"
        assert data["patient_id"] == patient.id
        assert "id" in data
        assert "upload_date" in data

    def test_upload_audio_wav_success(self, client, db, mock_patients_path):
        """Test uploading a valid WAV file"""
        from app.models import Patient
        patient = Patient(name="WAV Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        fake_audio = io.BytesIO(b"fake wav audio data")
        files = {"file": ("session.wav", fake_audio, "audio/wav")}

        response = client.post(f"/api/patients/{patient.id}/files", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "session.wav"
        assert data["file_type"] == "audio"

    def test_upload_with_metadata(self, client, db, mock_patients_path):
        """Test uploading file with metadata"""
        from app.models import Patient
        patient = Patient(name="Metadata Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        fake_audio = io.BytesIO(b"fake audio")
        files = {"file": ("test.mp3", fake_audio, "audio/mpeg")}
        data = {"user_metadata": "Second therapy session with parents"}

        response = client.post(
            f"/api/patients/{patient.id}/files",
            files=files,
            data=data
        )

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["user_metadata"] == "Second therapy session with parents"

    def test_upload_invalid_file_type(self, client, db, mock_patients_path):
        """Test that non-audio files are rejected"""
        from app.models import Patient
        patient = Patient(name="Invalid Type Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        fake_text = io.BytesIO(b"this is a text file")
        files = {"file": ("document.txt", fake_text, "text/plain")}

        response = client.post(f"/api/patients/{patient.id}/files", files=files)

        assert response.status_code == 400
        assert "not supported" in response.json()["detail"].lower()

    def test_upload_file_too_large(self, client, db, mock_patients_path):
        """Test that files > 50MB are rejected"""
        from app.models import Patient
        patient = Patient(name="Large File Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create 51MB fake file
        large_data = io.BytesIO(b"x" * (51 * 1024 * 1024))
        files = {"file": ("huge.mp3", large_data, "audio/mpeg")}

        response = client.post(f"/api/patients/{patient.id}/files", files=files)

        assert response.status_code == 400
        assert "exceeds" in response.json()["detail"].lower()

    def test_upload_no_file_provided(self, client, db, mock_patients_path):
        """Test that missing file is rejected"""
        from app.models import Patient
        patient = Patient(name="No File Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        response = client.post(f"/api/patients/{patient.id}/files", files={})

        # FastAPI returns 422 for missing required parameters
        assert response.status_code == 422

    def test_upload_patient_not_found(self, client, db, mock_patients_path):
        """Test that uploading to non-existent patient returns 404"""
        fake_audio = io.BytesIO(b"fake audio")
        files = {"file": ("test.mp3", fake_audio, "audio/mpeg")}

        response = client.post("/api/patients/999/files", files=files)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_upload_file_saved_to_correct_path(self, client, db, mock_patients_path):
        """Test that file is saved to correct filesystem location"""
        from app.models import Patient

        patient = Patient(name="Path Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        fake_audio = io.BytesIO(b"fake audio content for path test")
        files = {"file": ("therapy_session.mp3", fake_audio, "audio/mpeg")}

        response = client.post(f"/api/patients/{patient.id}/files", files=files)

        assert response.status_code == 201

        # Verify file exists in correct location
        # Note: Directory name uses underscore for spaces
        expected_path = (
            mock_patients_path / "PT_Path_Test_Patient" / "raw_files" / "therapy_session.mp3"
        )
        assert expected_path.exists(), f"File not found at {expected_path}"
        content = expected_path.read_bytes()
        assert content == b"fake audio content for path test", f"Content mismatch: {content}"

    def test_upload_database_entry_created(self, client, db, mock_patients_path):
        """Test that database entry is created for uploaded file"""
        from app.models import Patient, File

        patient = Patient(name="DB Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        fake_audio = io.BytesIO(b"fake audio")
        files = {"file": ("test.mp3", fake_audio, "audio/mpeg")}

        response = client.post(f"/api/patients/{patient.id}/files", files=files)

        assert response.status_code == 201
        file_id = response.json()["id"]

        # Verify database entry
        file_record = db.query(File).filter(File.id == file_id).first()
        assert file_record is not None
        assert file_record.patient_id == patient.id
        assert file_record.filename == "test.mp3"
        assert file_record.file_type == "audio"
        assert file_record.processing_status == "pending"


class TestFileList:
    """Test file listing endpoints"""

    def test_list_patient_files_empty(self, client, db):
        """Test listing files when patient has none"""
        from app.models import Patient

        patient = Patient(name="Empty Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        response = client.get(f"/api/patients/{patient.id}/files")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_patient_files_multiple(self, client, db, mock_patients_path):
        """Test listing multiple files for a patient"""
        from app.models import Patient, File
        from datetime import datetime

        patient = Patient(name="Multi File Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create multiple file records
        file1 = File(
            patient_id=patient.id,
            filename="file1.mp3",
            file_type="audio",
            local_path="PT_Multi_File_Patient/raw_files/file1.mp3",
            processing_status="pending"
        )
        file2 = File(
            patient_id=patient.id,
            filename="file2.wav",
            file_type="audio",
            local_path="PT_Multi_File_Patient/raw_files/file2.wav",
            processing_status="pending"
        )
        db.add(file1)
        db.add(file2)
        db.commit()

        response = client.get(f"/api/patients/{patient.id}/files")

        assert response.status_code == 200
        files = response.json()
        assert len(files) == 2
        assert files[0]["filename"] == "file1.mp3"
        assert files[1]["filename"] == "file2.wav"

    def test_get_file_details_success(self, client, db, mock_patients_path):
        """Test getting details of a specific file"""
        from app.models import Patient, File

        patient = Patient(name="Details Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        file_record = File(
            patient_id=patient.id,
            filename="details.mp3",
            file_type="audio",
            local_path="PT_Details_Patient/raw_files/details.mp3",
            processing_status="pending",
            user_metadata="Important session"
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        response = client.get(f"/api/patients/{patient.id}/files/{file_record.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == file_record.id
        assert data["filename"] == "details.mp3"
        assert data["user_metadata"] == "Important session"

    def test_get_file_details_not_found(self, client, db):
        """Test getting details of non-existent file"""
        from app.models import Patient

        patient = Patient(name="Not Found Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        response = client.get(f"/api/patients/{patient.id}/files/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestFileDelete:
    """Test file deletion endpoints"""

    def test_delete_file_success(self, client, db, mock_patients_path):
        """Test successful file deletion"""
        from app.models import Patient, File
        from pathlib import Path

        patient = Patient(name="Delete Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # Create actual file on filesystem
        patients_dir = mock_patients_path / "PT_Delete_Patient" / "raw_files"
        patients_dir.mkdir(parents=True, exist_ok=True)
        test_file = patients_dir / "delete_me.mp3"
        test_file.write_text("fake audio")

        # Create database entry
        file_record = File(
            patient_id=patient.id,
            filename="delete_me.mp3",
            file_type="audio",
            local_path="PT_Delete_Patient/raw_files/delete_me.mp3",
            processing_status="pending"
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # Delete file
        response = client.delete(f"/api/patients/{patient.id}/files/{file_record.id}")

        assert response.status_code == 200

        # Verify file deleted from filesystem
        assert not test_file.exists()

        # Verify file deleted from database
        deleted_record = db.query(File).filter(File.id == file_record.id).first()
        assert deleted_record is None

    def test_delete_file_not_found(self, client, db):
        """Test deleting non-existent file"""
        from app.models import Patient

        patient = Patient(name="Delete Not Found Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)

        response = client.delete(f"/api/patients/{patient.id}/files/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
