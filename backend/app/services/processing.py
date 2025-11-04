"""
Gemini AI Processing Service
Handles transcription, OCR, and text cleaning using Google's Gemini API
"""
import logging
import os
from pathlib import Path
from typing import Optional

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

# Setup logging
logger = logging.getLogger(__name__)


class GeminiProcessor:
    """
    Handles file processing with Google Gemini API
    Supports: Audio transcription, Image/PDF OCR, Text cleaning
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini processor

        Args:
            api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set - processing will fail at runtime")
        else:
            genai.configure(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def transcribe_audio(self, file_path: str) -> str:
        """
        Transcribe audio file using Gemini

        Args:
            file_path: Path to audio file (mp3, wav, ogg, webm, aac, flac)

        Returns:
            Transcribed text

        Raises:
            FileNotFoundError: If audio file doesn't exist
            Exception: If Gemini API fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        logger.info(f"Transcribing audio: {file_path}")

        try:
            # Upload file to Gemini
            audio_file = genai.upload_file(str(file_path))
            logger.info(f"Audio uploaded to Gemini: {audio_file.name}")

            # Create prompt for transcription
            prompt = """You are a clinical transcriber for a psychiatrist's practice.
Transcribe this therapy session audio into clean, readable text.
The language may be Hindi, Bengali, Assamese, or English.
Preserve speaker turns and key clinical information.
Output: Plain text only, no markdown or formatting."""

            # Generate transcription
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([prompt, audio_file])

            transcribed_text = response.text

            logger.info(f"Audio transcription complete: {len(transcribed_text)} characters")

            return transcribed_text

        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}", exc_info=True)
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def ocr_image(self, file_path: str) -> str:
        """
        Extract text from image/PDF using Gemini OCR

        Args:
            file_path: Path to image/PDF file (jpg, png, gif, webp, pdf)

        Returns:
            Extracted text

        Raises:
            FileNotFoundError: If image file doesn't exist
            Exception: If Gemini API fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        logger.info(f"Extracting text from image/PDF: {file_path}")

        try:
            # Upload file to Gemini
            image_file = genai.upload_file(str(file_path))
            logger.info(f"Image/PDF uploaded to Gemini: {image_file.name}")

            # Create prompt for OCR
            prompt = """You are a psychiatric document analyzer.
Extract all text from this clinical document (form, assessment, notes, intake form, etc).
Preserve structure, headings, and clinical relevance.
Correct obvious typos while preserving clinical accuracy.
Output: Plain text only, clean and organized."""

            # Generate OCR
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([prompt, image_file])

            extracted_text = response.text

            logger.info(f"OCR extraction complete: {len(extracted_text)} characters")

            return extracted_text

        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}", exc_info=True)
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def clean_text(self, file_path: str) -> str:
        """
        Clean and standardize text notes using Gemini

        Args:
            file_path: Path to text file (txt, md)

        Returns:
            Cleaned text

        Raises:
            FileNotFoundError: If text file doesn't exist
            Exception: If Gemini API fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")

        logger.info(f"Cleaning text: {file_path}")

        try:
            # Read text file
            text_content = file_path.read_text(encoding="utf-8")

            # Create prompt for text cleaning
            prompt = f"""You are a clinical text processor for psychiatric notes.
Clean and organize this clinical note while preserving all clinical information.
Fix typos and formatting issues. Ensure consistency.
Preserve clinical accuracy and all important details.
Output: Plain text only, clean and professional.

Text to clean:
{text_content}"""

            # Generate cleaned text
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            cleaned_text = response.text

            logger.info(f"Text cleaning complete: {len(cleaned_text)} characters")

            return cleaned_text

        except Exception as e:
            logger.error(f"Text cleaning failed: {str(e)}", exc_info=True)
            raise
