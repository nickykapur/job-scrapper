#!/usr/bin/env python3
"""
Migration script to add job deduplication support.
This script:
1. Adds new database tables and fields for deduplication
2. Backfills job signatures for all jobs marked as applied
"""

import os
import asyncio
import asyncpg
from database_models import JobDatabase


async def run_migration():
    """Run the deduplication migration"""
    db_url = os.environ.get('DATABASE_URL')

    if not db_url:
        print("❌ DATABASE_URL not set. Please set it to run the migration.")
        return False

    print("🚀 Starting job deduplication migration...")

    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("✅ Connected to database")

        # Read and execute migration SQL
        migration_file = 'database_migrations/002_add_job_deduplication.sql'

        if not os.path.exists(migration_file):
            print(f"❌ Migration file not found: {migration_file}")
            return False

        print(f"📄 Reading migration file: {migration_file}")
        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        print("🔄 Executing migration SQL...")
        await conn.execute(migration_sql)
        print("✅ Migration SQL executed successfully")

        # Backfill job signatures for existing applied jobs
        print("\n🔄 Backfilling job signatures for existing applied jobs...")

        applied_jobs = await conn.fetch("""
            SELECT id, title, company, country
            FROM jobs
            WHERE applied = TRUE
            ORDER BY scraped_at DESC
        """)

        print(f"📊 Found {len(applied_jobs)} applied jobs")

        db = JobDatabase()
        backfilled = 0

        for job in applied_jobs:
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
                continue

        print(f"✅ Backfilled {backfilled} job signatures")

        # Show summary
        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        print(f"📊 Summary:")
        print(f"   - Applied jobs found: {len(applied_jobs)}")
        print(f"   - Job signatures created: {backfilled}")
        print()
        print("🎯 Next steps:")
        print("   1. Your scraper will now automatically detect and skip reposted jobs")
        print("   2. When you mark a job as 'applied', it will be tracked to prevent duplicates")
        print("   3. Jobs are considered duplicates if the same company posts a similar")
        print("      job title within 30 days")
        print()

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_migration())
    exit(0 if success else 1)
