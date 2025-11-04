"""
Notion Integration Service
Exports processed psychiatric records to Notion database
"""
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from notion_client import Client
except ImportError:
    # Handle if notion-client not installed
    Client = None

logger = logging.getLogger(__name__)


class NotionExporter:
    """
    Exports processed patient files to Notion database
    Requires: NOTION_API_TOKEN and NOTION_DATABASE_ID in environment
    """

    def __init__(self):
        """Initialize Notion client with API token from environment"""
        self.api_token = os.getenv("NOTION_API_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")

        if not self.api_token:
            raise ValueError("NOTION_API_TOKEN not found in environment variables")
        if not self.database_id:
            raise ValueError("NOTION_DATABASE_ID not found in environment variables")

        if Client is None:
            raise ImportError("notion-client library not installed. Install with: pip install notion-client")

        # Initialize Notion client
        self.client = Client(auth=self.api_token)
        logger.info(f"Notion client initialized with database ID: {self.database_id}")

    def export_to_notion(
        self,
        patient_name: str,
        file_id: int,
        filename: str,
        file_type: str,
        transcribed_content: str,
        upload_date: datetime,
        processed_date: Optional[datetime] = None,
        user_metadata: Optional[str] = None,
        patient_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export a processed file to Notion database

        Args:
            patient_name: Name of the patient
            file_id: ID of the file record
            filename: Original filename
            file_type: Type of file (audio, image, text)
            transcribed_content: Processed/transcribed content
            upload_date: When file was uploaded
            processed_date: When file was processed
            user_metadata: User-provided metadata about the file
            patient_notes: Patient's general notes

        Returns:
            Dictionary with notion_page_id and status

        Raises:
            Exception: If Notion API fails
        """
        try:
            logger.info(f"Exporting file {filename} (ID: {file_id}) to Notion")

            # Prepare page title: "Patient Name - Filename"
            page_title = f"{patient_name} - {filename}"

            # Prepare properties for Notion page (using only available "Name" property)
            properties = {
                "Name": {
                    "title": [{"text": {"content": page_title}}]
                }
            }

            # Prepare blocks (content with metadata)
            children = []

            # Add metadata section
            metadata_blocks = self._build_metadata_blocks(
                patient_name=patient_name,
                file_id=file_id,
                file_type=file_type,
                upload_date=upload_date,
                processed_date=processed_date,
                user_metadata=user_metadata,
                patient_notes=patient_notes
            )
            children.extend(metadata_blocks)

            # Add transcribed content section
            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Transcribed Content"}}],
                    "color": "default"
                }
            })

            # Split long content into paragraphs (Notion has 2000 char limit per block)
            content_blocks = self._split_content_into_blocks(transcribed_content)
            children.extend(content_blocks)

            # Create page in Notion
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )

            notion_page_id = response.get("id")
            logger.info(f"Successfully exported to Notion with page ID: {notion_page_id}")

            return {
                "notion_page_id": notion_page_id,
                "status": "success",
                "patient_name": patient_name,
                "filename": filename
            }

        except Exception as e:
            logger.error(f"Failed to export to Notion: {str(e)}", exc_info=True)
            raise

    def export_batch(
        self,
        patient_name: str,
        files: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Export multiple files for a patient to Notion

        Args:
            patient_name: Name of the patient
            files: List of file dictionaries with export data

        Returns:
            Dictionary with list of exported page IDs and status
        """
        try:
            logger.info(f"Exporting {len(files)} files for patient {patient_name} to Notion")

            exported_ids = []
            failed_files = []

            for file_data in files:
                try:
                    result = self.export_to_notion(
                        patient_name=patient_name,
                        **file_data
                    )
                    exported_ids.append(result["notion_page_id"])
                except Exception as e:
                    logger.error(f"Failed to export file {file_data.get('filename')}: {str(e)}")
                    failed_files.append({
                        "filename": file_data.get("filename"),
                        "error": str(e)
                    })

            status = "success" if failed_files == [] else "partial"

            return {
                "exported_count": len(exported_ids),
                "notion_page_ids": exported_ids,
                "failed_count": len(failed_files),
                "failed_files": failed_files,
                "status": status
            }

        except Exception as e:
            logger.error(f"Batch export failed for patient {patient_name}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def _build_metadata_blocks(
        patient_name: str,
        file_id: int,
        file_type: str,
        upload_date: datetime,
        processed_date: Optional[datetime] = None,
        user_metadata: Optional[str] = None,
        patient_notes: Optional[str] = None
    ) -> list:
        """
        Build metadata blocks for page content

        Returns:
            List of Notion block dictionaries with metadata
        """
        blocks = []

        # Metadata section heading
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"text": {"content": "Metadata"}}],
                "color": "default"
            }
        })

        # Build metadata content
        metadata_text = f"Patient: {patient_name}\n"
        metadata_text += f"File Type: {file_type}\n"
        metadata_text += f"File ID: {file_id}\n"
        metadata_text += f"Upload Date: {upload_date.isoformat() if upload_date else 'N/A'}\n"

        if processed_date:
            metadata_text += f"Processed Date: {processed_date.isoformat()}\n"

        if user_metadata:
            metadata_text += f"User Metadata: {user_metadata}\n"

        if patient_notes:
            metadata_text += f"Patient Notes: {patient_notes}\n"

        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": metadata_text}}],
                "color": "default"
            }
        })

        # Add separator
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })

        return blocks

    @staticmethod
    def _split_content_into_blocks(content: str, chunk_size: int = 2000) -> list:
        """
        Split long content into Notion paragraph blocks (max 2000 chars each)

        Args:
            content: Full content to split
            chunk_size: Max characters per block

        Returns:
            List of Notion block dictionaries
        """
        blocks = []
        paragraphs = content.split("\n")
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 1 > chunk_size:
                if current_chunk:
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": current_chunk}}],
                            "color": "default"
                        }
                    })
                current_chunk = paragraph
            else:
                current_chunk += ("\n" if current_chunk else "") + paragraph

        # Add remaining content
        if current_chunk:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": current_chunk}}],
                    "color": "default"
                }
            })

        return blocks
