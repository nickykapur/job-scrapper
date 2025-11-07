#!/usr/bin/env python3
"""
Fix analytics by:
1. Verifying user_job_interactions table exists
2. Migrating existing applied/rejected jobs to user_job_interactions
3. Testing the analytics query
"""

import os
import asyncio
import asyncpg
from datetime import datetime


async def fix_analytics():
    """Fix analytics tracking"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not set")
        return False

    conn = await asyncpg.connect(db_url)

    try:
        print("🔍 Step 1: Checking if user_job_interactions table exists...")

        # Check if table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'user_job_interactions'
            )
        """)

        if not table_exists:
            print("❌ user_job_interactions table does not exist!")
            print("   Running multi-user migration...")

            # Read and execute migration
            with open('database_migrations/001_add_multi_user_support.sql', 'r') as f:
                migration_sql = f.read()

            await conn.execute(migration_sql)
            print("✅ Migration executed successfully")
        else:
            print("✅ user_job_interactions table exists")

        # Check how many records exist
        interaction_count = await conn.fetchval("SELECT COUNT(*) FROM user_job_interactions")
        print(f"📊 Current user_job_interactions records: {interaction_count}")

        print("\n🔄 Step 2: Migrating existing applied/rejected jobs...")

        # Get all users
        users = await conn.fetch("SELECT id, username FROM users")
        print(f"👥 Found {len(users)} users")

        total_migrated = 0

        for user in users:
            user_id = user['id']
            username = user['username']

            # Migrate applied jobs
            applied_count = await conn.fetchval("""
                INSERT INTO user_job_interactions (user_id, job_id, applied, applied_at, created_at, updated_at)
                SELECT $1, id, TRUE, COALESCE(updated_at, created_at), COALESCE(updated_at, created_at), CURRENT_TIMESTAMP
                FROM jobs
                WHERE applied = TRUE
                ON CONFLICT (user_id, job_id) DO UPDATE SET
                    applied = TRUE,
                    applied_at = COALESCE(EXCLUDED.applied_at, user_job_interactions.applied_at),
                    updated_at = CURRENT_TIMESTAMP
                RETURNING 1
            """, user_id)

            # Get count
            applied_jobs = await conn.fetchval("""
                SELECT COUNT(*) FROM jobs WHERE applied = TRUE
            """)

            # Migrate rejected jobs
            rejected_count = await conn.fetchval("""
                INSERT INTO user_job_interactions (user_id, job_id, rejected, rejected_at, created_at, updated_at)
                SELECT $1, id, TRUE, COALESCE(updated_at, created_at), COALESCE(updated_at, created_at), CURRENT_TIMESTAMP
                FROM jobs
                WHERE rejected = TRUE
                ON CONFLICT (user_id, job_id) DO UPDATE SET
                    rejected = TRUE,
                    rejected_at = COALESCE(EXCLUDED.rejected_at, user_job_interactions.rejected_at),
                    updated_at = CURRENT_TIMESTAMP
                RETURNING 1
            """, user_id)

            rejected_jobs = await conn.fetchval("""
                SELECT COUNT(*) FROM jobs WHERE rejected = TRUE
            """)

            print(f"   ✅ {username}: Migrated {applied_jobs} applied, {rejected_jobs} rejected jobs")
            total_migrated += applied_jobs + rejected_jobs

        print(f"\n✅ Total interactions migrated: {total_migrated}")

        print("\n🧪 Step 3: Testing analytics query...")

        # Test the analytics query
        users_stats = await conn.fetch("""
            SELECT
                u.id,
                u.username,
                u.email,
                u.full_name,
                u.last_login,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE) as jobs_applied,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.rejected = TRUE) as jobs_rejected,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.saved = TRUE) as jobs_saved
            FROM users u
            LEFT JOIN user_job_interactions uji ON u.id = uji.user_id
            GROUP BY u.id, u.username, u.email, u.full_name, u.last_login
            ORDER BY u.created_at DESC
        """)

        print("\n📊 Analytics Preview:")
        print("-" * 80)
        for user_stat in users_stats:
            print(f"User: {user_stat['username']}")
            print(f"  Applied: {user_stat['jobs_applied']}")
            print(f"  Rejected: {user_stat['jobs_rejected']}")
            print(f"  Saved: {user_stat['jobs_saved']}")
            print(f"  Last Login: {user_stat['last_login'] or 'Never'}")
            print()

        print("=" * 80)
        print("✅ Analytics fix completed successfully!")
        print("\n🎯 Next steps:")
        print("   1. Analytics should now work correctly")
        print("   2. Test with: python send_analytics_to_slack.py")
        print("   3. GitHub Actions will send daily reports")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await conn.close()


if __name__ == "__main__":
    success = asyncio.run(fix_analytics())
    exit(0 if success else 1)
