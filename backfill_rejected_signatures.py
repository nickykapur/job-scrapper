#!/usr/bin/env python3
"""
Backfill job signatures for rejected jobs.
This ensures rejected jobs won't show up again if companies repost them.
"""

import os
import asyncio
import asyncpg
from database_models import JobDatabase


async def backfill_rejected_signatures():
    """Backfill job signatures for all rejected jobs"""
    db_url = os.environ.get('DATABASE_URL')

    if not db_url:
        print("❌ DATABASE_URL not set.")
        return False

    print("🚀 Backfilling job signatures for rejected jobs...")

    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("✅ Connected to database")

        # Get all rejected jobs
        rejected_jobs = await conn.fetch("""
            SELECT id, title, company, country
            FROM jobs
            WHERE rejected = TRUE
            ORDER BY scraped_at DESC
        """)

        print(f"📊 Found {len(rejected_jobs)} rejected jobs")

        if len(rejected_jobs) == 0:
            print("✅ No rejected jobs to backfill")
            await conn.close()
            return True

        db = JobDatabase()
        backfilled = 0
        errors = 0

        for job in rejected_jobs:
            try:
                # Add job signature
                success = await db.add_job_signature(
                    company=job['company'],
                    title=job['title'],
                    country=job['country'],
                    job_id=job['id']
                )

                if success:
                    backfilled += 1

            except Exception as e:
                print(f"⚠️  Error backfilling signature for job {job['id']}: {e}")
                errors += 1
                continue

        print(f"\n✅ Backfilled {backfilled} job signatures for rejected jobs")
        if errors > 0:
            print(f"⚠️  {errors} errors encountered")

        print("\n" + "="*60)
        print("✅ Backfill completed!")
        print("="*60)
        print(f"📊 Summary:")
        print(f"   - Rejected jobs found: {len(rejected_jobs)}")
        print(f"   - Signatures created: {backfilled}")
        print(f"   - Errors: {errors}")
        print()
        print("🎯 Result:")
        print("   - Companies that repost jobs you've rejected will now be skipped")
        print("   - Reduces noise in your job feed")
        print()

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Backfill failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(backfill_rejected_signatures())
    exit(0 if success else 1)
