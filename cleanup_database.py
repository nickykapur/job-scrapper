#!/usr/bin/env python3
"""
Database cleanup script - Enforce 300 jobs per country limit
Removes oldest jobs per country, keeping the 300 most recent
"""

import asyncio
import os
import sys
from database_models import JobDatabase

async def cleanup_database():
    """Clean up database to maintain 300 jobs per country"""

    print("=" * 60)
    print("🧹 Database Cleanup - 300 Jobs Per Country")
    print("=" * 60)
    print()

    # Check if using PostgreSQL
    db = JobDatabase()
    if not db.use_postgres:
        print("❌ Not using PostgreSQL")
        print("   Set DATABASE_URL environment variable")
        return False

    conn = await db.get_connection()
    if not conn:
        print("❌ Could not connect to database")
        return False

    try:
        # Step 1: Show current state
        print("📊 Current State:")
        print("-" * 60)

        current_counts = await conn.fetch("""
            SELECT
                country,
                COUNT(*) as job_count
            FROM jobs
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY job_count DESC
        """)

        total_jobs = 0
        jobs_to_delete = 0

        for row in current_counts:
            country = row['country']
            count = row['job_count']
            total_jobs += count

            status = "✅" if count <= 300 else "❌"
            over = max(0, count - 300)
            jobs_to_delete += over

            print(f"  {status} {country}: {count} jobs", end="")
            if over > 0:
                print(f" (will delete {over} old jobs)")
            else:
                print()

        print()
        print(f"📈 Total jobs: {total_jobs}")
        print(f"🗑️  Jobs to delete: {jobs_to_delete}")
        print()

        if jobs_to_delete == 0:
            print("✅ Database is already within limits!")
            return True

        # Step 2: Confirm deletion
        print("⚠️  WARNING: This will permanently delete old jobs!")
        print(f"   {jobs_to_delete} jobs will be removed from the database.")
        print()

        confirm = input("Continue with cleanup? (yes/no): ").lower().strip()
        if confirm not in ['yes', 'y']:
            print("❌ Cleanup cancelled")
            return False

        print()

        # Step 3: Perform cleanup for each country
        print("🧹 Cleaning up...")
        print("-" * 60)

        for row in current_counts:
            country = row['country']
            count = row['job_count']

            if count > 300:
                # Delete old jobs, keep 300 newest
                deleted = await conn.execute("""
                    DELETE FROM jobs
                    WHERE id IN (
                        SELECT id
                        FROM (
                            SELECT
                                id,
                                ROW_NUMBER() OVER (
                                    PARTITION BY country
                                    ORDER BY scraped_at DESC NULLS LAST
                                ) as rn
                            FROM jobs
                            WHERE country = $1
                        ) ranked
                        WHERE rn > 300
                    )
                """, country)

                # Extract number from result like "DELETE 700"
                deleted_count = int(deleted.split()[-1]) if deleted else 0
                print(f"  ✂️  {country}: Deleted {deleted_count} old jobs (kept 300 newest)")
            else:
                print(f"  ✅ {country}: No cleanup needed ({count} jobs)")

        print()

        # Step 4: Show final state
        print("📊 Final State:")
        print("-" * 60)

        final_counts = await conn.fetch("""
            SELECT
                country,
                COUNT(*) as job_count,
                MAX(scraped_at) as newest_job,
                MIN(scraped_at) as oldest_job
            FROM jobs
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY job_count DESC
        """)

        for row in final_counts:
            country = row['country']
            count = row['job_count']
            newest = row['newest_job'].strftime('%Y-%m-%d') if row['newest_job'] else 'N/A'
            oldest = row['oldest_job'].strftime('%Y-%m-%d') if row['oldest_job'] else 'N/A'

            print(f"  ✅ {country}: {count} jobs (from {oldest} to {newest})")

        print()

        # Verify all countries are within limit
        over_limit = [r for r in final_counts if r['job_count'] > 300]
        if over_limit:
            print("❌ Some countries still over limit:")
            for row in over_limit:
                print(f"   {row['country']}: {row['job_count']} jobs")
            return False

        print("🎉 All countries within 300 job limit!")
        print()

        return True

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await conn.close()

async def main():
    """Main function"""

    # Run cleanup
    success = await cleanup_database()

    if success:
        print("=" * 60)
        print("✅ Cleanup Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Rebuild frontend: cd job-manager-ui && npm run build")
        print("  2. Wait for next scraper run (or trigger manually)")
        print("  3. Check UI for ⚡ Easy Apply badges")
        print()
        return 0
    else:
        print()
        print("=" * 60)
        print("❌ Cleanup Failed")
        print("=" * 60)
        print()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
