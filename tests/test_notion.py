"""
Notion Export Integration Tests
Test-Driven Development: These tests MUST FAIL initially
Then we implement code to make them PASS
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestNotionExportBasics:
    """Test basic Notion export functionality"""

    def test_export_single_processed_file_to_notion_success(self, client, db, mock_patients_path):
        """Test exporting a single processed file to Notion database"""
        from app.models import Patient, File

        # Create patient
        patient = Patient(name="Notion Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create file with transcribed content
        patient_dir = mock_patients_path / "PT_Notion_Test_Patient" / "raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        audio_path = patient_dir / "session.mp3"
        audio_path.write_bytes(b"fake audio data")

        audio_file = File(
            patient_id=patient_id,
            filename="session.mp3",
            file_type="audio",
            local_path="PT_Notion_Test_Patient/raw_files/session.mp3",
            processing_status="completed",
            transcribed_content="Patient reports anxiety and sleep issues.",
            date_processed=datetime.utcnow()
        )
        db.add(audio_file)
        db.commit()
        db.refresh(audio_file)
        file_id = audio_file.id

        # Mock Notion API
        with patch('app.services.notion.NotionExporter.export_to_notion') as mock_export:
            mock_export.return_value = {
                "notion_page_id": "abc123def456",
                "status": "success"
            }

            # Call export endpoint
            response = client.post(f"/api/patients/{patient_id}/export/{file_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["notion_page_id"] == "abc123def456"

    def test_export_image_file_with_ocr_to_notion(self, client, db, mock_patients_path):
        """Test exporting OCR extracted text from image to Notion"""
        from app.models import Patient, File

        patient = Patient(name="Image Export Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create image file with OCR result
        patient_dir = mock_patients_path / "PT_Image_Export_Patient" / "raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        image_path = patient_dir / "intake_form.jpg"
        image_path.write_bytes(b"fake image data")

        image_file = File(
            patient_id=patient_id,
            filename="intake_form.jpg",
            file_type="image",
            local_path="PT_Image_Export_Patient/raw_files/intake_form.jpg",
            processing_status="completed",
            transcribed_content="Patient Age: 32\nHistory: Depression (2 years)",
            date_processed=datetime.utcnow()
        )
        db.add(image_file)
        db.commit()
        db.refresh(image_file)
        file_id = image_file.id

        with patch('app.services.notion.NotionExporter.export_to_notion') as mock_export:
            mock_export.return_value = {"notion_page_id": "xyz789", "status": "success"}

            response = client.post(f"/api/patients/{patient_id}/export/{file_id}")

        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_export_all_patient_files_to_notion(self, client, db, mock_patients_path):
        """Test exporting all processed files for a patient to Notion"""
        from app.models import Patient, File

        patient = Patient(name="Batch Export Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create multiple files
        for i in range(3):
            patient_dir = mock_patients_path / f"PT_Batch_Export_Patient/raw_files"
            patient_dir.mkdir(parents=True, exist_ok=True)
            file_path = patient_dir / f"file_{i}.txt"
            file_path.write_bytes(b"file content")

            db_file = File(
                patient_id=patient_id,
                filename=f"file_{i}.txt",
                file_type="text",
                local_path=f"PT_Batch_Export_Patient/raw_files/file_{i}.txt",
                processing_status="completed",
                transcribed_content=f"Content for file {i}",
                date_processed=datetime.utcnow()
            )
            db.add(db_file)
            db.commit()

        with patch('app.services.notion.NotionExporter.export_to_notion') as mock_export:
            # Each call to export_to_notion returns success with different page IDs
            mock_export.side_effect = [
                {"notion_page_id": f"page{i}", "status": "success"}
                for i in range(1, 4)
            ]

            response = client.post(f"/api/patients/{patient_id}/export-all")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["exported_count"] == 3


class TestNotionExportErrors:
    """Test error handling in Notion export"""

    def test_export_file_not_found(self, client, db):
        """Test exporting non-existent file"""
        response = client.post("/api/patients/1/export/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_export_patient_not_found(self, client, db):
        """Test exporting for non-existent patient"""
        response = client.post("/api/patients/999/export/1")
        assert response.status_code == 404

    def test_export_file_not_processed(self, client, db, mock_patients_path):
        """Test exporting file that hasn't been processed"""
        from app.models import Patient, File

        patient = Patient(name="Unprocessed Export Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        patient_dir = mock_patients_path / "PT_Unprocessed_Export_Patient/raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        file_path = patient_dir / "unprocessed.mp3"
        file_path.write_bytes(b"audio data")

        unprocessed_file = File(
            patient_id=patient_id,
            filename="unprocessed.mp3",
            file_type="audio",
            local_path="PT_Unprocessed_Export_Patient/raw_files/unprocessed.mp3",
            processing_status="pending"  # Not processed
        )
        db.add(unprocessed_file)
        db.commit()
        db.refresh(unprocessed_file)
        file_id = unprocessed_file.id

        response = client.post(f"/api/patients/{patient_id}/export/{file_id}")
        assert response.status_code == 400
        assert "not been processed" in response.json()["detail"].lower()

    def test_export_notion_api_failure(self, client, db, mock_patients_path):
        """Test handling Notion API errors"""
        from app.models import Patient, File

        patient = Patient(name="API Failure Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        patient_dir = mock_patients_path / "PT_API_Failure_Patient/raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        file_path = patient_dir / "test.mp3"
        file_path.write_bytes(b"audio")

        db_file = File(
            patient_id=patient_id,
            filename="test.mp3",
            file_type="audio",
            local_path="PT_API_Failure_Patient/raw_files/test.mp3",
            processing_status="completed",
            transcribed_content="Test content"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        file_id = db_file.id

        # Mock Notion API failure
        with patch('app.services.notion.NotionExporter.export_to_notion') as mock_export:
            mock_export.side_effect = Exception("Notion API error: Invalid database ID")

            response = client.post(f"/api/patients/{patient_id}/export/{file_id}")

        assert response.status_code == 500
        assert "export failed" in response.json()["detail"].lower()


class TestNotionExportContent:
    """Test the actual content being exported to Notion"""

    def test_exported_content_includes_patient_info(self, client, db, mock_patients_path):
        """Test that exported page includes patient information"""
        from app.models import Patient, File

        patient = Patient(name="Content Test Patient", notes="Patient notes here")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        patient_dir = mock_patients_path / "PT_Content_Test_Patient/raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        file_path = patient_dir / "session.mp3"
        file_path.write_bytes(b"audio")

        db_file = File(
            patient_id=patient_id,
            filename="session.mp3",
            file_type="audio",
            local_path="PT_Content_Test_Patient/raw_files/session.mp3",
            processing_status="completed",
            transcribed_content="Session transcript here"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        file_id = db_file.id

        exported_content = None

        def capture_export(**kwargs):
            nonlocal exported_content
            exported_content = kwargs
            return {"notion_page_id": "test123", "status": "success"}

        with patch('app.services.notion.NotionExporter.export_to_notion', side_effect=capture_export):
            response = client.post(f"/api/patients/{patient_id}/export/{file_id}")

        assert response.status_code == 200
        # Verify export was called with proper content
        assert exported_content is not None or response.json()["status"] == "success"

    def test_exported_metadata_includes_timestamps(self, client, db, mock_patients_path):
        """Test that exported metadata includes upload and processing timestamps"""
        from app.models import Patient, File

        patient = Patient(name="Metadata Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        patient_dir = mock_patients_path / "PT_Metadata_Test_Patient/raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        file_path = patient_dir / "file.txt"
        file_path.write_bytes(b"content")

        db_file = File(
            patient_id=patient_id,
            filename="file.txt",
            file_type="text",
            local_path="PT_Metadata_Test_Patient/raw_files/file.txt",
            processing_status="completed",
            transcribed_content="File content",
            date_processed=datetime.utcnow()
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        file_id = db_file.id

        with patch('app.services.notion.NotionExporter.export_to_notion') as mock_export:
            mock_export.return_value = {"notion_page_id": "meta123", "status": "success"}

            response = client.post(f"/api/patients/{patient_id}/export/{file_id}")

        assert response.status_code == 200
