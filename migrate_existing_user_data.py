#!/usr/bin/env python3
"""
Migration Script: Convert Single-User Data to Multi-User
Migrates existing applied/rejected jobs to a user account
"""

import asyncio
import asyncpg
import os
from user_database import UserDatabase
from auth_utils import hash_password

async def migrate_existing_user_data():
    """
    Migrate existing job data to new multi-user system

    Steps:
    1. Create admin user account (you)
    2. Migrate all applied/rejected jobs to your user_job_interactions
    3. Set default preferences based on current system
    4. Verify migration
    """

    print("=" * 60)
    print("MIGRATE EXISTING USER DATA TO MULTI-USER SYSTEM")
    print("=" * 60)

    # Get database URL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not set. Please set it first.")
        return False

    conn = await asyncpg.connect(db_url)

    try:
        # ====================================================================
        # STEP 1: CREATE YOUR ADMIN USER ACCOUNT
        # ====================================================================

        print("\n[STEP 1] Creating your admin user account...")
        print("-" * 60)

        # Check if users table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'users'
            )
        """)

        if not table_exists:
            print("❌ Users table doesn't exist. Please run the migration SQL first:")
            print("   database_migrations/001_add_multi_user_support.sql")
            return False

        # Check if admin user already exists
        existing_user = await conn.fetchrow(
            "SELECT id, username FROM users WHERE username = $1",
            'admin'
        )

        if existing_user:
            print(f"✅ Admin user already exists (ID: {existing_user['id']})")
            admin_user_id = existing_user['id']
        else:
            # Create admin user
            print("\n🔐 Creating admin user account...")
            print("   Username: admin")
            print("   Email: admin@yourdomain.com (change this later)")
            print("   Password: ChangeThisPassword123 (CHANGE THIS IMMEDIATELY!)")

            password_hash = hash_password("ChangeThisPassword123")

            admin_user = await conn.fetchrow("""
                INSERT INTO users (username, email, password_hash, full_name, is_admin)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, username
            """, 'admin', 'admin@yourdomain.com', password_hash, 'Admin User', True)

            admin_user_id = admin_user['id']
            print(f"✅ Admin user created (ID: {admin_user_id})")

            # Create default preferences
            await conn.execute("""
                INSERT INTO user_preferences (
                    user_id,
                    job_types,
                    experience_levels,
                    exclude_senior,
                    preferred_countries
                )
                VALUES ($1, $2, $3, $4, $5)
            """,
                admin_user_id,
                ['software'],  # Current system focuses on software
                ['entry', 'junior', 'mid'],  # Current system excludes senior
                True,
                ['Ireland', 'Spain', 'Panama', 'Chile', 'Netherlands', 'Germany', 'Sweden']
            )

            print("✅ Default preferences created")

        # ====================================================================
        # STEP 2: ANALYZE EXISTING JOB DATA
        # ====================================================================

        print("\n[STEP 2] Analyzing existing job data...")
        print("-" * 60)

        # Count total jobs
        total_jobs = await conn.fetchval("SELECT COUNT(*) FROM jobs")
        print(f"📊 Total jobs in database: {total_jobs}")

        # Count jobs with applied/rejected flags
        applied_jobs = await conn.fetchval(
            "SELECT COUNT(*) FROM jobs WHERE applied = TRUE"
        )
        rejected_jobs = await conn.fetchval(
            "SELECT COUNT(*) FROM jobs WHERE rejected = TRUE"
        )

        print(f"✅ Applied jobs: {applied_jobs}")
        print(f"❌ Rejected jobs: {rejected_jobs}")
        print(f"📝 Untracked jobs: {total_jobs - applied_jobs - rejected_jobs}")

        # ====================================================================
        # STEP 3: MIGRATE APPLIED/REJECTED JOBS
        # ====================================================================

        print("\n[STEP 3] Migrating applied/rejected jobs to your account...")
        print("-" * 60)

        # Check if data already migrated
        existing_interactions = await conn.fetchval(
            "SELECT COUNT(*) FROM user_job_interactions WHERE user_id = $1",
            admin_user_id
        )

        if existing_interactions > 0:
            print(f"⚠️  Found {existing_interactions} existing interactions for admin user")
            print("   Do you want to re-migrate (this will update existing data)? [y/N]")
            response = input().strip().lower()
            if response != 'y':
                print("❌ Migration cancelled")
                return False

        # Migrate applied jobs
        if applied_jobs > 0:
            print(f"\n📤 Migrating {applied_jobs} applied jobs...")

            applied_job_ids = await conn.fetch(
                "SELECT id, scraped_at FROM jobs WHERE applied = TRUE"
            )

            for job in applied_job_ids:
                await conn.execute("""
                    INSERT INTO user_job_interactions
                    (user_id, job_id, applied, applied_at)
                    VALUES ($1, $2, TRUE, $3)
                    ON CONFLICT (user_id, job_id)
                    DO UPDATE SET applied = TRUE, applied_at = $3
                """, admin_user_id, job['id'], job['scraped_at'])

            print(f"✅ Migrated {applied_jobs} applied jobs")

        # Migrate rejected jobs
        if rejected_jobs > 0:
            print(f"\n📤 Migrating {rejected_jobs} rejected jobs...")

            rejected_job_ids = await conn.fetch(
                "SELECT id, scraped_at FROM jobs WHERE rejected = TRUE"
            )

            for job in rejected_job_ids:
                await conn.execute("""
                    INSERT INTO user_job_interactions
                    (user_id, job_id, rejected, rejected_at)
                    VALUES ($1, $2, TRUE, $3)
                    ON CONFLICT (user_id, job_id)
                    DO UPDATE SET rejected = TRUE, rejected_at = $3
                """, admin_user_id, job['id'], job['scraped_at'])

            print(f"✅ Migrated {rejected_jobs} rejected jobs")

        # ====================================================================
        # STEP 4: VERIFY MIGRATION
        # ====================================================================

        print("\n[STEP 4] Verifying migration...")
        print("-" * 60)

        # Count migrated interactions
        migrated_applied = await conn.fetchval("""
            SELECT COUNT(*) FROM user_job_interactions
            WHERE user_id = $1 AND applied = TRUE
        """, admin_user_id)

        migrated_rejected = await conn.fetchval("""
            SELECT COUNT(*) FROM user_job_interactions
            WHERE user_id = $1 AND rejected = TRUE
        """, admin_user_id)

        print(f"✅ Applied jobs in user_job_interactions: {migrated_applied}")
        print(f"✅ Rejected jobs in user_job_interactions: {migrated_rejected}")

        if migrated_applied == applied_jobs and migrated_rejected == rejected_jobs:
            print("\n✨ Migration successful! All data migrated correctly.")
        else:
            print("\n⚠️  Migration counts don't match:")
            print(f"   Expected applied: {applied_jobs}, Got: {migrated_applied}")
            print(f"   Expected rejected: {rejected_jobs}, Got: {migrated_rejected}")

        # ====================================================================
        # STEP 5: CLEANUP (OPTIONAL)
        # ====================================================================

        print("\n[STEP 5] Cleanup...")
        print("-" * 60)
        print("⚠️  The old 'applied' and 'rejected' columns in the jobs table")
        print("   are no longer needed, but we'll keep them for backward compatibility.")
        print("   You can remove them later if you want:")
        print("   ALTER TABLE jobs DROP COLUMN applied, DROP COLUMN rejected;")

        # ====================================================================
        # SUMMARY
        # ====================================================================

        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE!")
        print("=" * 60)

        print("\n📋 What was done:")
        print(f"   ✅ Created admin user (ID: {admin_user_id})")
        print(f"   ✅ Migrated {migrated_applied} applied jobs")
        print(f"   ✅ Migrated {migrated_rejected} rejected jobs")
        print(f"   ✅ Created default preferences")

        print("\n🔐 Your Login Credentials:")
        print("   Username: admin")
        print("   Password: ChangeThisPassword123")
        print("   ⚠️  IMPORTANT: Change your password immediately!")

        print("\n🚀 Next Steps:")
        print("   1. Login to your account:")
        print("      POST /api/auth/login")
        print('      {"username":"admin","password":"ChangeThisPassword123"}')
        print()
        print("   2. Change your password:")
        print("      POST /api/auth/change-password")
        print('      {"old_password":"ChangeThisPassword123","new_password":"YourNewPassword"}')
        print()
        print("   3. Update your preferences:")
        print("      GET /api/auth/preferences")
        print("      PUT /api/auth/preferences")
        print()
        print("   4. Invite friends/family to register!")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await conn.close()


async def check_migration_status():
    """Check if migration has already been done"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not set")
        return

    conn = await asyncpg.connect(db_url)

    try:
        # Check if tables exist
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'user_preferences', 'user_job_interactions')
        """)

        print("📊 Multi-User System Status:")
        print("-" * 60)

        if len(tables) == 3:
            print("✅ All multi-user tables exist")

            # Check for users
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            print(f"👥 Users: {user_count}")

            # Check for admin
            admin = await conn.fetchrow("SELECT id, username FROM users WHERE is_admin = TRUE LIMIT 1")
            if admin:
                print(f"🔑 Admin user: {admin['username']} (ID: {admin['id']})")

                # Check interactions
                interactions = await conn.fetchval(
                    "SELECT COUNT(*) FROM user_job_interactions WHERE user_id = $1",
                    admin['id']
                )
                print(f"📝 Job interactions: {interactions}")
            else:
                print("⚠️  No admin user found")

            # Check old job data
            old_applied = await conn.fetchval("SELECT COUNT(*) FROM jobs WHERE applied = TRUE")
            old_rejected = await conn.fetchval("SELECT COUNT(*) FROM jobs WHERE rejected = TRUE")

            print(f"\n📊 Old System (jobs table):")
            print(f"   Applied: {old_applied}")
            print(f"   Rejected: {old_rejected}")

        else:
            print(f"⚠️  Only {len(tables)}/3 tables exist")
            print("   Run database migration first:")
            print("   database_migrations/001_add_multi_user_support.sql")

    finally:
        await conn.close()


if __name__ == "__main__":
    import sys

    print("🔄 User Data Migration Tool")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == "status":
        # Just check status
        asyncio.run(check_migration_status())
    else:
        # Run full migration
        print("This will migrate your existing job data to the new multi-user system.")
        print()
        print("⚠️  BACKUP RECOMMENDATION:")
        print("   It's recommended to backup your database first.")
        print("   (Railway: Settings → Create Snapshot)")
        print()
        print("Do you want to continue? [y/N]: ", end="")

        response = input().strip().lower()

        if response == 'y':
            success = asyncio.run(migrate_existing_user_data())
            sys.exit(0 if success else 1)
        else:
            print("❌ Migration cancelled")
            sys.exit(1)
