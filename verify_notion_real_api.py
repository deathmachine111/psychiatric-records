#!/usr/bin/env python3
"""
Manual verification script for Notion export with REAL API
This tests the actual Notion database export end-to-end
"""
import os
from datetime import datetime
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.notion import NotionExporter


def main():
    """Test Notion export with real API"""
    print("=" * 70)
    print("NOTION EXPORT - REAL API VERIFICATION")
    print("=" * 70)

    # Check environment variables
    api_token = os.getenv("NOTION_API_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")

    print(f"\n[OK] API Token: {api_token[:20]}...{api_token[-10:] if len(api_token) > 30 else ''}")
    print(f"[OK] Database ID: {db_id}")

    try:
        # Initialize exporter
        print("\n[1] Initializing Notion client...")
        exporter = NotionExporter()
        print("[OK] Notion client initialized successfully")

        # Test single file export
        print("\n[2] Testing single file export...")
        result = exporter.export_to_notion(
            patient_name="Test Patient - Claude Verification",
            file_id=999,
            filename="verification_test.txt",
            file_type="text",
            transcribed_content="This is a test export from Claude Code.\n\n"
                                "Session: Verification Test\n"
                                "Purpose: Testing Notion API integration\n"
                                "Status: Working correctly",
            upload_date=datetime.now(),
            processed_date=datetime.now(),
            user_metadata="Automated test by Claude Code",
            patient_notes="Test verification - can be deleted"
        )

        print(f"[OK] Export successful!")
        print(f"  Notion Page ID: {result['notion_page_id']}")
        print(f"  Status: {result['status']}")

        # Verify page was created
        if result.get('status') == 'success' and result.get('notion_page_id'):
            print("\n[OK] VERIFICATION PASSED - Notion export is working correctly!")
            print("\nYou can view the test page here:")
            print(f"  https://www.notion.so/{result['notion_page_id']}")
            print("\nNote: This is a test page and can be deleted from Notion.")
            return 0
        else:
            print("\n[FAIL] VERIFICATION FAILED - Export returned unexpected response")
            print(f"  Response: {result}")
            return 1

    except Exception as e:
        print(f"\n[FAIL] VERIFICATION FAILED - {type(e).__name__}: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Verify NOTION_API_TOKEN is correct in .env")
        print("  2. Verify NOTION_DATABASE_ID is correct in .env")
        print("  3. Check that your Notion token has permission to add pages to the database")
        print("  4. Ensure the Notion database connection is authorized")
        return 1


if __name__ == "__main__":
    exit_code = main()
    print("\n" + "=" * 70)
    sys.exit(exit_code)
