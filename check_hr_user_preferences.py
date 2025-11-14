#!/usr/bin/env python3
"""
Check HR User preferences to see why other countries are not appearing
"""

import asyncio
import os
from user_database import UserDatabase


async def check_hr_user():
    """Check HR user preferences"""

    # Get DATABASE_URL from Railway
    db_url = os.environ.get('DATABASE_URL')

    if not db_url:
        # Use Railway database URL directly
        db_url = "postgresql://postgres:JcWFAlWypXvRisiQPVlOlGVFEIRgsgxl@oregon-postgres.render.com:5432/railway"
        os.environ['DATABASE_URL'] = db_url
        print(f"✅ Set DATABASE_URL")

    db = UserDatabase()

    if not db.use_postgres:
        print("❌ PostgreSQL not available")
        return

    try:
        print("=" * 60)
        print("CHECKING HR_USER PREFERENCES")
        print("=" * 60)

        # Get all users to find hr_user
        import asyncpg
        import ssl

        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        conn = await asyncpg.connect(db_url, ssl=ssl_context)

        # Get hr_user
        users = await conn.fetch("SELECT id, username, email, preferences FROM users WHERE username LIKE '%hr%'")

        if not users:
            print("❌ No HR user found")
            await conn.close()
            return

        for user in users:
            print(f"\n📋 User: {user['username']}")
            print(f"   ID: {user['id']}")
            print(f"   Email: {user['email']}")
            print(f"\n🔧 Preferences:")

            if user['preferences']:
                import json
                prefs = user['preferences']

                # Pretty print preferences
                print(json.dumps(prefs, indent=2))

                # Check preferred_countries specifically
                if 'preferred_countries' in prefs:
                    print(f"\n🌍 Preferred Countries: {prefs['preferred_countries']}")
                else:
                    print(f"\n⚠️  No 'preferred_countries' key found in preferences")

                # Check other relevant fields
                if 'job_types' in prefs:
                    print(f"💼 Job Types: {prefs['job_types']}")

                if 'experience_levels' in prefs:
                    print(f"📊 Experience Levels: {prefs['experience_levels']}")
            else:
                print("   No preferences set")

        await conn.close()

        print("\n" + "=" * 60)
        print("ANALYSIS")
        print("=" * 60)
        print("\nThe issue is likely:")
        print("1. The 'preferred_countries' field is set to only ['Ireland', 'Remote']")
        print("2. This filters OUT all other countries like Spain, Panama, Chile, etc.")
        print("\nTo fix this, you need to UPDATE the preferences to include more countries.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_hr_user())
