#!/usr/bin/env python3
"""
Update preferences for inigotrabaja user - Spain jobs only
"""

import asyncio
from user_database import UserDatabase


async def update_inigotrabaja_preferences():
    """Update preferences for inigotrabaja to see Spain jobs only"""

    print("=" * 60)
    print("UPDATE PREFERENCES: inigotrabaja")
    print("=" * 60)

    db = UserDatabase()

    if not db.use_postgres:
        print("❌ PostgreSQL required")
        return False

    try:
        # Get user
        print("\n[STEP 1] Finding user...")
        print("-" * 60)

        user = await db.get_user_by_username("inigotrabaja")

        if not user:
            print("❌ User 'inigotrabaja' not found")
            return False

        print(f"✅ User found!")
        print(f"   User ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")

        # Update preferences for Spain
        print("\n[STEP 2] Updating preferences for Spain...")
        print("-" * 60)

        spain_preferences = {
            # Job types - SOFTWARE ONLY
            "job_types": ["software"],

            # Keywords - Software engineering
            "keywords": [
                "Software Engineer",
                "Software Developer",
                "Full Stack",
                "Backend Developer",
                "Frontend Developer",
                "Python Developer",
                "JavaScript Developer",
                "Web Developer"
            ],

            # No excluded keywords
            "excluded_keywords": [],

            # Experience levels - All levels
            "experience_levels": ["entry", "junior", "mid", "senior", "lead"],
            "exclude_senior": False,

            # SPAIN ONLY
            "preferred_countries": ["Spain"],
            "preferred_cities": [],
            "exclude_locations": [],

            # No company filters
            "excluded_companies": [],
            "preferred_companies": [],

            # Filters - Show all jobs
            "easy_apply_only": False,
            "remote_only": False,

            # Notifications
            "email_notifications": True,
            "daily_digest": False
        }

        success = await db.update_user_preferences(
            user_id=user['id'],
            preferences=spain_preferences
        )

        if not success:
            print("❌ Failed to update preferences")
            return False

        print("✅ Preferences updated successfully!")

        # Verify
        print("\n[STEP 3] Verifying preferences...")
        print("-" * 60)

        prefs = await db.get_user_preferences(user['id'])

        if prefs:
            print("✅ Preferences verified!")
            print(f"   Preferred Countries: {prefs.get('preferred_countries')}")
            print(f"   Job Types: {prefs.get('job_types')}")
            print(f"   Experience Levels: {prefs.get('experience_levels')}")
        else:
            print("⚠️  Could not verify preferences")

        print("\n" + "=" * 60)
        print("PREFERENCES UPDATE COMPLETE!")
        print("=" * 60)

        print("\n📋 Updated Settings:")
        print("   Country Filter: Spain ONLY")
        print("   Job Types: SOFTWARE ONLY")
        print("   Experience Levels: All levels")
        print("   Remote Filter: Disabled (shows all locations)")

        print("\n🚀 Next Steps:")
        print("   1. User 'inigotrabaja' will now see ONLY software jobs from Spain")
        print("   2. Refresh the job list in the UI")
        print("   3. Jobs will be filtered by preferred_countries = ['Spain'] AND job_types = ['software']")

        return True

    except Exception as e:
        print(f"\n❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = asyncio.run(update_inigotrabaja_preferences())
    sys.exit(0 if success else 1)
