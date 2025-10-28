#!/usr/bin/env python3
"""
Create Second User Account - HR/Recruitment Specialist
Sets up account with proper preferences for HR job tracking
"""

import asyncio
from user_database import UserDatabase


async def create_hr_user():
    """Create second user account for HR/Recruitment job tracking"""

    print("=" * 60)
    print("CREATE HR/RECRUITMENT USER ACCOUNT")
    print("=" * 60)

    db = UserDatabase()

    if not db.use_postgres:
        print("❌ PostgreSQL required for multi-user support")
        print("   Please set DATABASE_URL environment variable")
        return False

    try:
        # ================================================================
        # STEP 1: Get user details
        # ================================================================

        print("\n[STEP 1] User Account Details")
        print("-" * 60)

        print("\nEnter account details for the HR user:")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        print("Password (min 8 chars, letters + numbers): ", end="")
        password = input().strip()
        full_name = input("Full Name (optional): ").strip() or None

        # ================================================================
        # STEP 2: Create user account
        # ================================================================

        print("\n[STEP 2] Creating user account...")
        print("-" * 60)

        user = await db.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            is_admin=False  # Regular user, not admin
        )

        if not user:
            print("❌ Failed to create user. Possible reasons:")
            print("   - Username already exists")
            print("   - Email already exists")
            print("   - Password doesn't meet requirements")
            return False

        print(f"✅ User account created!")
        print(f"   User ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")

        # ================================================================
        # STEP 3: Set HR-specific preferences
        # ================================================================

        print("\n[STEP 3] Setting HR/Recruitment preferences...")
        print("-" * 60)

        # HR user preferences
        hr_preferences = {
            # Job types - HR/Recruitment only
            "job_types": ["hr", "recruitment"],

            # Keywords for HR jobs
            "keywords": [
                "HR Officer",
                "Talent Acquisition",
                "HR Coordinator",
                "HR Generalist",
                "Junior Recruiter",
                "Recruitment Coordinator",
                "People Operations",
                "HR Assistant"
            ],

            # Exclude senior/lead roles (looking for entry/junior)
            "excluded_keywords": [
                "Senior", "Lead", "Manager", "Director", "Head of",
                "5+ years", "7+ years", "10+ years"
            ],

            # Experience levels - Entry and Junior only
            "experience_levels": ["entry", "junior"],
            "exclude_senior": True,

            # Locations - Ireland and Remote
            "preferred_countries": ["Ireland", "Remote"],
            "preferred_cities": ["Dublin"],

            # No company exclusions for now
            "excluded_companies": [],
            "preferred_companies": [],

            # Filters
            "easy_apply_only": False,  # Show all jobs
            "remote_only": False,  # Include hybrid/onsite in Ireland

            # Notifications
            "email_notifications": True,
            "daily_digest": False
        }

        success = await db.update_user_preferences(
            user_id=user['id'],
            preferences=hr_preferences
        )

        if not success:
            print("⚠️  Failed to set preferences, but user account was created")
            return False

        print("✅ Preferences set successfully!")
        print("\nPreference Summary:")
        print(f"   Job Types: {', '.join(hr_preferences['job_types'])}")
        print(f"   Experience: {', '.join(hr_preferences['experience_levels'])}")
        print(f"   Countries: {', '.join(hr_preferences['preferred_countries'])}")
        print(f"   Keywords: {len(hr_preferences['keywords'])} HR-specific terms")

        # ================================================================
        # STEP 4: Verify setup
        # ================================================================

        print("\n[STEP 4] Verifying setup...")
        print("-" * 60)

        # Get user preferences back
        prefs = await db.get_user_preferences(user['id'])

        if prefs:
            print("✅ Preferences verified!")
            print(f"   Job types: {prefs.get('job_types')}")
            print(f"   Experience levels: {prefs.get('experience_levels')}")
        else:
            print("⚠️  Could not verify preferences")

        # ================================================================
        # SUMMARY
        # ================================================================

        print("\n" + "=" * 60)
        print("USER SETUP COMPLETE!")
        print("=" * 60)

        print("\n📋 Account Summary:")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   User ID: {user['id']}")
        print(f"   Account Type: Regular User")

        print("\n🔍 Job Preferences:")
        print("   • Job Types: HR/Recruitment")
        print("   • Experience: Entry Level, Junior")
        print("   • Locations: Ireland, Remote")
        print("   • Excludes: Senior roles, Lead roles, Manager positions")

        print("\n🚀 Next Steps:")
        print("   1. Share login credentials with user:")
        print(f"      Username: {username}")
        print(f"      Password: {password}")
        print()
        print("   2. User can login at:")
        print("      POST /api/auth/login")
        print(f'      {{"username":"{username}","password":"***"}}')
        print()
        print("   3. GitHub Actions scraper will now fetch:")
        print("      • Software jobs (User 1)")
        print("      • HR jobs (User 2)")
        print()
        print("   4. Each user sees only THEIR job type!")

        return True

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_login(username, password):
    """Test login for the new user"""
    db = UserDatabase()

    print(f"\nTesting login for {username}...")

    user = await db.authenticate_user(username, password)

    if user:
        print(f"✅ Login successful!")
        print(f"   User ID: {user['id']}")
        print(f"   Username: {user['username']}")
        return True
    else:
        print(f"❌ Login failed")
        return False


if __name__ == "__main__":
    import sys

    print("🎯 HR/Recruitment User Setup Tool")
    print()
    print("This script will create a user account for HR/Recruitment job tracking.")
    print()
    print("The user will be able to:")
    print("  • See HR and recruitment jobs only")
    print("  • Filter for entry-level and junior roles")
    print("  • Track their own applied/rejected jobs")
    print("  • Set their own preferences")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test existing user login
        username = input("Username to test: ").strip()
        password = input("Password: ").strip()
        success = asyncio.run(test_login(username, password))
        sys.exit(0 if success else 1)
    else:
        # Create new user
        success = asyncio.run(create_hr_user())
        sys.exit(0 if success else 1)
