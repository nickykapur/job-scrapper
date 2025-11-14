#!/usr/bin/env python3
"""
Check HR User preferences - Simpler version using UserDatabase class
"""

import asyncio
import os
import json
from user_database import UserDatabase


async def check_hr_user():
    """Check HR user preferences"""

    # Set DATABASE_URL if not already set
    if not os.environ.get('DATABASE_URL'):
        # Railway production database
        os.environ['DATABASE_URL'] = "postgresql://postgres:JcWFAlWypXvRisiQPVlOlGVFEIRgsgxl@oregon-postgres.render.com:5432/railway"
        print("✅ DATABASE_URL set")

    db = UserDatabase()

    if not db.use_postgres:
        print("❌ PostgreSQL not available")
        return

    print("=" * 70)
    print("CHECKING HR_USER PREFERENCES")
    print("=" * 70)

    try:
        # Get hr_user by username
        user = await db.get_user_by_username("hr_user")

        if not user:
            print("\n❌ HR user not found!")
            print("   Trying to find any users with 'hr' in username...")

            # Try to get all users (admin function)
            conn = await db.get_connection()
            if conn:
                users = await conn.fetch("SELECT id, username FROM users WHERE username LIKE '%hr%'")
                if users:
                    print(f"\n   Found {len(users)} users:")
                    for u in users:
                        print(f"   - {u['username']} (ID: {u['id']})")
                else:
                    print("   No users found with 'hr' in username")
                await conn.close()
            return

        print(f"\n✅ Found user: {user['username']}")
        print(f"   ID: {user['id']}")
        print(f"   Email: {user['email']}")

        # Get user preferences
        print(f"\n🔧 Fetching preferences...")
        prefs = await db.get_user_preferences(user['id'])

        if not prefs:
            print("   ❌ No preferences found")
            return

        print("\n" + "=" * 70)
        print("CURRENT PREFERENCES")
        print("=" * 70)

        # Parse preferences JSON field
        preferences = prefs.get('preferences', {})

        if preferences:
            print("\n📋 Full Preferences:")
            print(json.dumps(preferences, indent=2))

            # Highlight key fields
            print("\n" + "=" * 70)
            print("KEY SETTINGS")
            print("=" * 70)

            if 'preferred_countries' in preferences:
                countries = preferences['preferred_countries']
                print(f"\n🌍 Preferred Countries: {countries}")
                print(f"   Count: {len(countries)}")
            else:
                print(f"\n⚠️  'preferred_countries' not found in preferences")

            if 'job_types' in preferences:
                print(f"\n💼 Job Types: {preferences['job_types']}")

            if 'experience_levels' in preferences:
                print(f"\n📊 Experience Levels: {preferences['experience_levels']}")

            if 'keywords' in preferences:
                keywords = preferences['keywords']
                print(f"\n🔑 Keywords ({len(keywords)} total):")
                for kw in keywords[:5]:  # Show first 5
                    print(f"   - {kw}")
                if len(keywords) > 5:
                    print(f"   ... and {len(keywords) - 5} more")

            if 'excluded_keywords' in preferences:
                excluded = preferences['excluded_keywords']
                print(f"\n🚫 Excluded Keywords ({len(excluded)} total):")
                for kw in excluded:
                    print(f"   - {kw}")

        else:
            print("\n⚠️  Preferences field is empty or NULL")

        print("\n" + "=" * 70)
        print("DIAGNOSIS")
        print("=" * 70)

        if 'preferred_countries' in preferences:
            countries = preferences['preferred_countries']
            if len(countries) == 2 and "Ireland" in countries and "Remote" in countries:
                print(f"\n❗ ISSUE IDENTIFIED:")
                print(f"   The 'preferred_countries' is set to ONLY {countries}")
                print(f"   This FILTERS OUT all jobs from other countries!")
                print(f"\n💡 SOLUTION:")
                print(f"   You need to ADD more countries to the 'preferred_countries' list.")
                print(f"   For example: Ireland, Spain, Panama, Chile, Switzerland, Remote")
                print(f"\n📝 To fix this, run the script 'update_hr_user_countries.py'")
            elif len(countries) > 2:
                print(f"\n✅ Countries look good: {countries}")
            else:
                print(f"\n⚠️  Unusual country configuration: {countries}")
        else:
            print(f"\n⚠️  No 'preferred_countries' field found")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_hr_user())
