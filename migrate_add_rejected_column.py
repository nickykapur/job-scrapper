#!/usr/bin/env python3
"""
Add rejected column to existing PostgreSQL database
Run this script to migrate the database schema
"""

import os
import asyncio
import asyncpg
from database_models import JobDatabase

async def migrate_database():
    """Add rejected column to existing jobs table"""

    print("🔄 Starting database migration: Adding 'rejected' column")

    # Get database URL from environment
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found. Please set the environment variable.")
        return False

    try:
        # Connect to database
        print(f"📡 Connecting to database...")
        conn = await asyncpg.connect(db_url)

        # Check if rejected column already exists
        check_query = """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'jobs' AND column_name = 'rejected'
        );
        """

        column_exists = await conn.fetchval(check_query)

        if column_exists:
            print("✅ Column 'rejected' already exists. No migration needed.")
            await conn.close()
            return True

        print("🔧 Adding 'rejected' column to jobs table...")

        # Add the rejected column
        await conn.execute("""
            ALTER TABLE jobs
            ADD COLUMN rejected BOOLEAN DEFAULT FALSE;
        """)

        print("📊 Creating index on rejected column...")

        # Create index for performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_rejected ON jobs(rejected);
        """)

        print("🔍 Verifying column was added...")

        # Verify the column was added
        verify_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'jobs'
        AND column_name IN ('applied', 'rejected')
        ORDER BY column_name;
        """

        columns = await conn.fetch(verify_query)

        print("📋 Current job table columns:")
        for col in columns:
            print(f"   • {col['column_name']}: {col['data_type']} (default: {col['column_default']})")

        # Test count
        total_jobs = await conn.fetchval("SELECT COUNT(*) FROM jobs")
        rejected_jobs = await conn.fetchval("SELECT COUNT(*) FROM jobs WHERE rejected = TRUE")

        print(f"📊 Database stats after migration:")
        print(f"   • Total jobs: {total_jobs}")
        print(f"   • Rejected jobs: {rejected_jobs}")

        await conn.close()

        print("✅ Migration completed successfully!")
        print("🎉 You can now reject jobs and they will persist in the database!")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🗄️ PostgreSQL Database Migration Tool")
    print("=" * 50)

    success = asyncio.run(migrate_database())

    if success:
        print("\n🎯 Next steps:")
        print("1. Test job rejection in your UI")
        print("2. Verify rejected jobs persist after refresh")
        print("3. Check Railway logs for any remaining errors")
    else:
        print("\n💡 Alternative migration:")
        print("1. Access your Railway PostgreSQL database directly")
        print("2. Run the SQL from 'add_rejected_column.sql'")
        print("3. Or check DATABASE_URL environment variable")