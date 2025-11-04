"""
Gemini Processing Tests
Test-Driven Development: These tests MUST FAIL initially
Then we implement code to make them PASS
"""
import io
import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestGeminiAudioTranscription:
    """Test audio file transcription with Gemini"""

    def test_transcribe_audio_mp3_success(self, client, db, mock_patients_path):
        """Test transcribing an MP3 audio file"""
        from app.models import Patient, File
        from pathlib import Path

        # Create patient and audio file
        patient = Patient(name="Audio Test Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create actual file on disk
        patient_dir = mock_patients_path / "PT_Audio_Test_Patient" / "raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        audio_path = patient_dir / "therapy_session.mp3"
        audio_path.write_bytes(b"fake mp3 audio data")

        # Create audio file record
        audio_file = File(
            patient_id=patient_id,
            filename="therapy_session.mp3",
            file_type="audio",
            local_path="PT_Audio_Test_Patient/raw_files/therapy_session.mp3",
            processing_status="pending"
        )
        db.add(audio_file)
        db.commit()
        db.refresh(audio_file)
        file_id = audio_file.id

        # Mock Gemini API response
        with patch('app.services.processing.GeminiProcessor.transcribe_audio') as mock_transcribe:
            mock_transcribe.return_value = "Patient reported symptoms of anxiety and insomnia."

            # Process file
            response = client.post(
                f"/api/patients/{patient_id}/process/{file_id}"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == file_id
        assert data["processing_status"] == "completed"
        assert data["transcribed_content"] == "Patient reported symptoms of anxiety and insomnia."

    def test_transcribe_audio_wav_success(self, client, db, mock_patients_path):
        """Test transcribing a WAV audio file"""
        from app.models import Patient, File

        patient = Patient(name="WAV Audio Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create actual file on disk
        patient_dir = mock_patients_path / "PT_WAV_Audio_Patient" / "raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        audio_path = patient_dir / "session.wav"
        audio_path.write_bytes(b"fake wav audio data")

        audio_file = File(
            patient_id=patient_id,
            filename="session.wav",
            file_type="audio",
            local_path="PT_WAV_Audio_Patient/raw_files/session.wav",
            processing_status="pending"
        )
        db.add(audio_file)
        db.commit()
        db.refresh(audio_file)
        file_id = audio_file.id

        with patch('app.services.processing.GeminiProcessor.transcribe_audio') as mock_transcribe:
            mock_transcribe.return_value = "Transcribed from WAV format."

            response = client.post(f"/api/patients/{patient_id}/process/{file_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["processing_status"] == "completed"

    def test_transcribe_audio_file_not_found(self, client, db):
        """Test transcribing non-existent file"""
        from app.models import Patient

        patient = Patient(name="Audio Not Found Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        response = client.post(f"/api/patients/{patient_id}/process/999")

        assert response.status_code == 404


class TestGeminiImageOCR:
    """Test image/PDF OCR processing with Gemini"""

    def test_ocr_image_jpg_success(self, client, db, mock_patients_path):
        """Test OCR on JPG image"""
        from app.models import Patient, File

        patient = Patient(name="Image OCR Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create actual file on disk
        patient_dir = mock_patients_path / "PT_Image_OCR_Patient" / "raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        image_path = patient_dir / "intake_form.jpg"
        image_path.write_bytes(b"\xFF\xD8\xFF\xE0" + b"fake jpg image data")

        image_file = File(
            patient_id=patient_id,
            filename="intake_form.jpg",
            file_type="image",
            local_path="PT_Image_OCR_Patient/raw_files/intake_form.jpg",
            processing_status="pending"
        )
        db.add(image_file)
        db.commit()
        db.refresh(image_file)
        file_id = image_file.id

        with patch('app.services.processing.GeminiProcessor.ocr_image') as mock_ocr:
            mock_ocr.return_value = "Patient Name: John Doe\nAge: 35\nChief Complaint: Anxiety"

            response = client.post(f"/api/patients/{patient_id}/process/{file_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == file_id
        assert data["processing_status"] == "completed"
        assert "Patient Name" in data["transcribed_content"]

    def test_ocr_pdf_success(self, client, db, mock_patients_path):
        """Test OCR on PDF document"""
        from app.models import Patient, File

        patient = Patient(name="PDF OCR Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create actual file on disk
        patient_dir = mock_patients_path / "PT_PDF_OCR_Patient" / "raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = patient_dir / "medical_history.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n" + b"fake pdf content")

        pdf_file = File(
            patient_id=patient_id,
            filename="medical_history.pdf",
            file_type="image",
            local_path="PT_PDF_OCR_Patient/raw_files/medical_history.pdf",
            processing_status="pending"
        )
        db.add(pdf_file)
        db.commit()
        db.refresh(pdf_file)
        file_id = pdf_file.id

        with patch('app.services.processing.GeminiProcessor.ocr_image') as mock_ocr:
            mock_ocr.return_value = "Medical History:\n- Hypertension diagnosed 2015\n- Treated with medication"

            response = client.post(f"/api/patients/{patient_id}/process/{file_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["processing_status"] == "completed"


class TestGeminiTextCleaning:
    """Test text file cleaning/standardization with Gemini"""

    def test_clean_text_file_success(self, client, db, mock_patients_path):
        """Test cleaning and standardizing text notes"""
        from app.models import Patient, File

        patient = Patient(name="Text Cleaning Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create actual file on disk
        patient_dir = mock_patients_path / "PT_Text_Cleaning_Patient" / "raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        text_path = patient_dir / "session_notes.txt"
        text_path.write_text("Patient notes: messy text with typos", encoding="utf-8")

        text_file = File(
            patient_id=patient_id,
            filename="session_notes.txt",
            file_type="text",
            local_path="PT_Text_Cleaning_Patient/raw_files/session_notes.txt",
            processing_status="pending"
        )
        db.add(text_file)
        db.commit()
        db.refresh(text_file)
        file_id = text_file.id

        with patch('app.services.processing.GeminiProcessor.clean_text') as mock_clean:
            mock_clean.return_value = "Session Notes:\n\nPatient presents with depressive symptoms.\nRecommended: Continue current medication.\nFollow-up: 2 weeks."

            response = client.post(f"/api/patients/{patient_id}/process/{file_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == file_id
        assert data["processing_status"] == "completed"
        assert "depressive symptoms" in data["transcribed_content"]

    def test_clean_markdown_file_success(self, client, db, mock_patients_path):
        """Test cleaning markdown formatted notes"""
        from app.models import Patient, File

        patient = Patient(name="Markdown Cleaning Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create actual file on disk
        patient_dir = mock_patients_path / "PT_Markdown_Cleaning_Patient" / "raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        md_path = patient_dir / "notes.md"
        md_path.write_text("# Session notes\nmessy markdown format", encoding="utf-8")

        md_file = File(
            patient_id=patient_id,
            filename="notes.md",
            file_type="text",
            local_path="PT_Markdown_Cleaning_Patient/raw_files/notes.md",
            processing_status="pending"
        )
        db.add(md_file)
        db.commit()
        db.refresh(md_file)
        file_id = md_file.id

        with patch('app.services.processing.GeminiProcessor.clean_text') as mock_clean:
            mock_clean.return_value = "# Session Notes\n\nPatient appears more relaxed today."

            response = client.post(f"/api/patients/{patient_id}/process/{file_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["processing_status"] == "completed"


class TestProcessingErrorHandling:
    """Test error handling in processing"""

    def test_processing_status_updates_to_processing(self, client, db, mock_patients_path):
        """Test that file status changes to 'processing' during processing"""
        from app.models import Patient, File

        patient = Patient(name="Status Update Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create actual file on disk
        patient_dir = mock_patients_path / "PT_Status_Update_Patient" / "raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        audio_path = patient_dir / "audio.mp3"
        audio_path.write_bytes(b"fake mp3")

        audio_file = File(
            patient_id=patient_id,
            filename="audio.mp3",
            file_type="audio",
            local_path="PT_Status_Update_Patient/raw_files/audio.mp3",
            processing_status="pending"
        )
        db.add(audio_file)
        db.commit()
        db.refresh(audio_file)
        file_id = audio_file.id

        with patch('app.services.processing.GeminiProcessor.transcribe_audio') as mock_transcribe:
            mock_transcribe.return_value = "Transcribed content"

            response = client.post(f"/api/patients/{patient_id}/process/{file_id}")

        # Verify response indicates completion
        assert response.status_code == 200
        data = response.json()
        assert data["processing_status"] == "completed"

    def test_processing_handles_gemini_error(self, client, db, mock_patients_path):
        """Test handling of Gemini API errors"""
        from app.models import Patient, File

        patient = Patient(name="Error Handling Patient")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id

        # Create actual file on disk
        patient_dir = mock_patients_path / "PT_Error_Handling_Patient" / "raw_files"
        patient_dir.mkdir(parents=True, exist_ok=True)
        audio_path = patient_dir / "audio.mp3"
        audio_path.write_bytes(b"fake mp3")

        audio_file = File(
            patient_id=patient_id,
            filename="audio.mp3",
            file_type="audio",
            local_path="PT_Error_Handling_Patient/raw_files/audio.mp3",
            processing_status="pending"
        )
        db.add(audio_file)
        db.commit()
        db.refresh(audio_file)
        file_id = audio_file.id

        with patch('app.services.processing.GeminiProcessor.transcribe_audio') as mock_transcribe:
            mock_transcribe.side_effect = Exception("Gemini API error: rate limit exceeded")

            response = client.post(f"/api/patients/{patient_id}/process/{file_id}")

        # Should return error response, not crash
        assert response.status_code == 500
        data = response.json()
        assert "error" in data or "detail" in data
