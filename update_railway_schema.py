#!/usr/bin/env python3
"""
Update Railway database schema to match current schema
"""

import requests
import json

def update_railway_schema(railway_url):
    """Update Railway database schema via API"""

    # Schema update commands
    schema_updates = [
        # Add missing columns if they don't exist
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS country VARCHAR(100);",
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS excluded BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;",
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;",

        # Create indexes if they don't exist
        "CREATE INDEX IF NOT EXISTS idx_jobs_country ON jobs(country);",
        "CREATE INDEX IF NOT EXISTS idx_jobs_excluded ON jobs(excluded);",
    ]

    print(f"🔧 Updating Railway database schema...")
    print(f"📡 Target: {railway_url}")

    try:
        for i, sql_command in enumerate(schema_updates, 1):
            print(f"   {i}. {sql_command}")

            # Try to execute via API (this is a mock - Railway might not have direct SQL API)
            # In practice, you'd need to connect to the database directly
            # For now, just print the commands that should be run

        print(f"\n✅ Schema update commands prepared!")
        print(f"📝 To apply these changes:")
        print(f"   1. Connect to your Railway PostgreSQL database")
        print(f"   2. Run each command above manually")
        print(f"   3. Or add them to a migration script")

        return True

    except Exception as e:
        print(f"❌ Schema update failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        railway_url = sys.argv[1]
        update_railway_schema(railway_url)
    else:
        print("Usage: python3 update_railway_schema.py <railway_url>")