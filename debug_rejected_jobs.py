#!/usr/bin/env python3
"""
Debug script to check rejected jobs in the database
"""

import os
import asyncio
from database_models import JobDatabase

async def check_rejected_jobs():
    """Check what rejected jobs are in the database"""

    print("🔍 Checking rejected jobs in database...")

    # Initialize database
    db = JobDatabase()

    try:
        # Initialize database connection
        await db.init_database()
        print(f"✅ Database connected successfully")

        # Get all jobs
        all_jobs = await db.get_all_jobs()

        # Filter out metadata
        actual_jobs = {k: v for k, v in all_jobs.items() if not k.startswith('_')}

        total_jobs = len(actual_jobs)
        print(f"📊 Total jobs in database: {total_jobs}")

        # Count rejected jobs
        rejected_jobs = {k: v for k, v in actual_jobs.items() if v.get('rejected', False)}
        rejected_count = len(rejected_jobs)
        print(f"🚫 Rejected jobs in database: {rejected_count}")

        # Count applied jobs
        applied_jobs = {k: v for k, v in actual_jobs.items() if v.get('applied', False)}
        applied_count = len(applied_jobs)
        print(f"✅ Applied jobs in database: {applied_count}")

        # Show some sample rejected jobs if any exist
        if rejected_count > 0:
            print(f"\n🚫 Sample rejected jobs:")
            for i, (job_id, job) in enumerate(list(rejected_jobs.items())[:5]):
                title = job.get('title', 'Unknown')[:50]
                company = job.get('company', 'Unknown')[:30]
                print(f"   ID: {job_id[:12]}... | {title} | {company} | Rejected: {job.get('rejected')} | Applied: {job.get('applied')}")

        # Show some sample non-rejected jobs
        active_jobs = {k: v for k, v in actual_jobs.items() if not v.get('rejected', False)}
        print(f"\n📝 Sample active jobs:")
        for i, (job_id, job) in enumerate(list(active_jobs.items())[:5]):
            title = job.get('title', 'Unknown')[:50]
            company = job.get('company', 'Unknown')[:30]
            print(f"   ID: {job_id[:12]}... | {title} | {company} | Rejected: {job.get('rejected', False)} | Applied: {job.get('applied', False)}")

        # Check for any jobs with missing rejected field
        missing_rejected = {k: v for k, v in actual_jobs.items() if 'rejected' not in v}
        if missing_rejected:
            print(f"⚠️  WARNING: {len(missing_rejected)} jobs missing 'rejected' field")

        return True

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(check_rejected_jobs())
    if success:
        print(f"\n✅ Database check completed!")
    else:
        print(f"\n❌ Database check failed!")