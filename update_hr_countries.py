#!/usr/bin/env python3
"""
Update HR User's preferred_countries to include all countries
Fixes the issue where only Ireland and Remote jobs are shown
"""

import asyncio
import os
import json
from user_database import UserDatabase


async def update_hr_countries():
    """Update HR user's country preferences to include all countries"""

    # Ensure DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL not set")
        print("   Please set it using:")
        print("   export DATABASE_URL='your_railway_postgres_url'")
        return False

    db = UserDatabase()

    if not db.use_postgres:
        print("❌ PostgreSQL not available")
        return False

    print("=" * 70)
    print("UPDATE HR USER - PREFERRED COUNTRIES")
    print("=" * 70)

    try:
        # Get hr_user
        print("\n[STEP 1] Finding HR user...")
        user = await db.get_user_by_username("hr_user")

        if not user:
            print("❌ HR user not found!")
            return False

        print(f"✅ Found user: {user['username']} (ID: {user['id']})")

        # Get current preferences
        print("\n[STEP 2] Getting current preferences...")
        prefs = await db.get_user_preferences(user['id'])

        if not prefs:
            print("❌ No preferences found")
            return False

        current_preferences = prefs.get('preferences', {})
        current_countries = current_preferences.get('preferred_countries', [])

        print(f"Current preferred_countries: {current_countries}")

        # Define new country list - European countries + Remote (excluding Chile and Panama)
        new_countries = [
            "Ireland",
            "Spain",
            "Switzerland",
            "Netherlands",
            "Germany",
            "Sweden",
            "Belgium",
            "Denmark",
            "France",
            "Italy",
            "Remote"
        ]

        print(f"\n[STEP 3] Updating to include ALL countries...")
        print(f"New preferred_countries: {new_countries}")

        # Update the preferences
        current_preferences['preferred_countries'] = new_countries

        success = await db.update_user_preferences(
            user_id=user['id'],
            preferences=current_preferences
        )

        if not success:
            print("❌ Failed to update preferences")
            return False

        print("\n✅ Successfully updated preferred_countries!")

        # Verify the update
        print("\n[STEP 4] Verifying update...")
        updated_prefs = await db.get_user_preferences(user['id'])

        if updated_prefs:
            updated_countries = updated_prefs.get('preferences', {}).get('preferred_countries', [])
            print(f"✅ Verified - Preferred countries now: {updated_countries}")
            print(f"   Total countries: {len(updated_countries)}")
        else:
            print("⚠️  Could not verify update")

        print("\n" + "=" * 70)
        print("UPDATE COMPLETE!")
        print("=" * 70)
        print("\n✅ HR user will now see jobs from European countries + Remote:")
        for country in new_countries:
            print(f"   • {country}")

        print("\n🚀 Next Steps:")
        print("   1. The HR user can now see jobs from all countries")
        print("   2. They can further filter by specific countries in the UI if needed")
        print("   3. Next scraping run will show jobs from all these countries")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def show_current_settings():
    """Just show current settings without updating"""

    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL not set")
        return

    db = UserDatabase()

    try:
        user = await db.get_user_by_username("hr_user")
        if not user:
            print("❌ HR user not found")
            return

        prefs = await db.get_user_preferences(user['id'])
        if not prefs:
            print("❌ No preferences found")
            return

        current_preferences = prefs.get('preferences', {})

        print("\n" + "=" * 70)
        print("CURRENT HR USER PREFERENCES")
        print("=" * 70)
        print(json.dumps(current_preferences, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "show":
        # Just show current settings
        asyncio.run(show_current_settings())
    else:
        # Update the settings
        print("\n🎯 HR User Country Preferences Update Tool")
        print()
        print("This will update the HR user's preferred_countries to include European countries")
        print("+ Remote (excludes Chile and Panama).")
        print()

        confirm = input("Continue? (yes/no): ").strip().lower()

        if confirm not in ['yes', 'y']:
            print("Cancelled.")
            sys.exit(0)

        success = asyncio.run(update_hr_countries())
        sys.exit(0 if success else 1)
