#!/usr/bin/env python3
"""
Script to delete all German jobs from the Railway database
Uses the Railway API endpoint to delete jobs by country
"""

import requests
import sys

RAILWAY_URL = "https://web-production-110bb.up.railway.app"

def delete_german_jobs():
    """Delete all German jobs from the Railway database"""

    print(f"🗑️  Delete German Jobs Script")
    print("=" * 50)
    print(f"🌐 Railway URL: {RAILWAY_URL}")
    print()

    try:
        # First, check how many German jobs exist
        print("🔍 Checking German jobs in database...")
        response = requests.get(f"{RAILWAY_URL}/api/jobs", timeout=30)
        response.raise_for_status()

        jobs_data = response.json()
        german_jobs = [
            job_id for job_id, job_data in jobs_data.items()
            if not job_id.startswith("_") and job_data.get("country") == "Germany"
        ]

        total_jobs = len([k for k in jobs_data.keys() if not k.startswith("_")])

        print(f"📊 Found {len(german_jobs)} German jobs out of {total_jobs} total jobs")

        if len(german_jobs) == 0:
            print("✅ No German jobs found in the database")
            return True

        # Ask for confirmation
        print()
        response_input = input(f"⚠️  Are you sure you want to delete {len(german_jobs)} German jobs? (yes/no): ")
        if response_input.lower() not in ['yes', 'y']:
            print("❌ Deletion cancelled")
            return False

        # Delete German jobs via API
        print()
        print("🗑️  Deleting German jobs from Railway database...")
        delete_response = requests.delete(
            f"{RAILWAY_URL}/api/jobs/by-country/Germany",
            timeout=30
        )
        delete_response.raise_for_status()

        result = delete_response.json()

        print()
        print("✅ Successfully deleted German jobs!")
        print(f"📊 Jobs deleted: {result.get('jobs_deleted', 0)}")
        print(f"📊 Total jobs remaining in database: {result.get('total_jobs_in_database', 0)}")

        print()
        print("🎉 Database updated successfully!")
        print("📝 The changes are live on Railway immediately.")
        print("   Refresh your frontend to see the updated job counts.")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = delete_german_jobs()
    sys.exit(0 if success else 1)
