#!/usr/bin/env python3
"""
Clear all jobs from the PostgreSQL database
Use this to start fresh with a clean database
"""

import os
import asyncio
import asyncpg
from database_models import JobDatabase

async def clear_database():
    """Delete all jobs from the database"""

    print("🗑️  Starting database cleanup - DELETE ALL JOBS")
    print("⚠️  This will permanently delete all job data!")

    # Confirm before proceeding
    confirm = input("Type 'DELETE ALL' to confirm: ")
    if confirm != 'DELETE ALL':
        print("❌ Operation cancelled")
        return False

    # Get database URL from environment
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found. Please set the environment variable.")
        return False

    try:
        # Connect to database
        print(f"📡 Connecting to database...")
        conn = await asyncpg.connect(db_url)

        # Count existing jobs before deletion
        total_jobs_before = await conn.fetchval("SELECT COUNT(*) FROM jobs")
        print(f"📊 Found {total_jobs_before} jobs in database")

        if total_jobs_before == 0:
            print("✅ Database is already empty")
            await conn.close()
            return True

        print(f"🗑️  Deleting all {total_jobs_before} jobs...")

        # Delete all jobs
        deleted_count = await conn.execute("DELETE FROM jobs")

        # Also clear scraping sessions if you want a complete reset
        print("🗑️  Clearing scraping sessions...")
        await conn.execute("DELETE FROM scraping_sessions")

        # Verify deletion
        total_jobs_after = await conn.fetchval("SELECT COUNT(*) FROM jobs")
        sessions_after = await conn.fetchval("SELECT COUNT(*) FROM scraping_sessions")

        print(f"✅ Database cleared successfully!")
        print(f"   📊 Jobs deleted: {total_jobs_before}")
        print(f"   📊 Jobs remaining: {total_jobs_after}")
        print(f"   📊 Scraping sessions cleared: {sessions_after}")

        await conn.close()

        print("\n🎉 Database is now empty and ready for fresh data!")
        print("💡 Next steps:")
        print("   1. Run your multi-country scraper to populate with new jobs")
        print("   2. Or sync existing jobs from local JSON files")

        return True

    except Exception as e:
        print(f"❌ Database clearing failed: {e}")
        return False

async def clear_database_keep_structure():
    """Alternative: Clear data but keep table structure"""

    print("🗑️  Starting selective database cleanup")
    print("⚠️  This will delete job data but keep table structure")

    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found")
        return False

    try:
        conn = await asyncpg.connect(db_url)

        # Get stats before
        jobs_count = await conn.fetchval("SELECT COUNT(*) FROM jobs")
        sessions_count = await conn.fetchval("SELECT COUNT(*) FROM scraping_sessions")

        print(f"📊 Current data:")
        print(f"   Jobs: {jobs_count}")
        print(f"   Sessions: {sessions_count}")

        # Clear data
        await conn.execute("TRUNCATE TABLE jobs RESTART IDENTITY CASCADE")
        await conn.execute("TRUNCATE TABLE scraping_sessions RESTART IDENTITY CASCADE")

        print("✅ All data cleared, tables preserved")
        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🗄️ PostgreSQL Database Cleanup Tool")
    print("=" * 50)

    print("\nChoose cleanup method:")
    print("1. DELETE - Remove all job records (recommended)")
    print("2. TRUNCATE - Clear all data and reset IDs")
    print("3. Cancel")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        success = asyncio.run(clear_database())
    elif choice == "2":
        success = asyncio.run(clear_database_keep_structure())
    else:
        print("❌ Operation cancelled")
        success = False

    if success:
        print("\n✅ Database cleanup completed!")
    else:
        print("\n❌ Database cleanup failed!")