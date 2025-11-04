#!/usr/bin/env python3
"""
Inspect Notion database properties
Find out what fields your PSYRECORDS database has
"""
import os
from dotenv import load_dotenv
import sys
import json

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from notion_client import Client

def main():
    """Query database schema"""
    print("=" * 70)
    print("NOTION DATABASE SCHEMA INSPECTOR")
    print("=" * 70)

    api_token = os.getenv("NOTION_API_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")

    print(f"\nDatabase ID: {db_id}")

    try:
        client = Client(auth=api_token)

        # Query the database to get its schema
        print("\n[1] Querying database schema...")
        response = client.databases.retrieve(db_id)

        properties = response.get("properties", {})

        if not properties:
            print("[FAIL] No properties found in database")
            return 1

        print(f"\n[OK] Found {len(properties)} properties:\n")

        for prop_name, prop_config in properties.items():
            prop_type = prop_config.get("type", "unknown")
            print(f"  - {prop_name}")
            print(f"    Type: {prop_type}")
            if prop_type == "select":
                options = prop_config.get("select", {}).get("options", [])
                if options:
                    print(f"    Options: {[opt['name'] for opt in options]}")
            print()

        print("\n" + "=" * 70)
        print("USE THESE PROPERTY NAMES IN THE NOTION EXPORTER")
        print("=" * 70)
        print("\nExample mapping (you need to adjust):")
        print("  'Patient Name' -> use actual property name from list above")
        print("  'File Name' -> use actual property name from list above")
        print("\nThen update backend/app/services/notion.py")

        return 0

    except Exception as e:
        print(f"\n[FAIL] Error: {type(e).__name__}: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
