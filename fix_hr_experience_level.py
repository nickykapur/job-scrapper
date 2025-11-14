#!/usr/bin/env python3
"""
Fix HR User experience level to include 'mid' level jobs
"""

import asyncio
import os
from user_database import UserDatabase


async def fix_hr_experience():
    """Update HR user to include mid-level jobs"""

    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = "postgresql://postgres:JcWFAlWypXvRisiQPVlOlGVFEIRgsgxl@switchback.proxy.rlwy.net:22276/railway"

    db = UserDatabase()

    print("=" * 70)
    print("FIX HR_USER EXPERIENCE LEVEL")
    print("=" * 70)

    try:
        # Get hr_user
        user = await db.get_user_by_username("hr_user")
        if not user:
            print("❌ HR user not found")
            return False

        print(f"\n✅ Found user: {user['username']} (ID: {user['id']})")

        # Get current preferences
        prefs = await db.get_user_preferences(user['id'])
        if not prefs:
            print("❌ No preferences found")
            return False

        # Get the preferences JSON
        import asyncpg
        conn = await db.get_connection()
        current_prefs = await conn.fetchrow('SELECT * FROM user_preferences WHERE user_id = $1', user['id'])

        current_levels = current_prefs['experience_levels']
        print(f"\nCurrent experience_levels: {current_levels}")

        # Update to include mid-level
        new_levels = ['entry', 'junior', 'mid']
        print(f"New experience_levels: {new_levels}")

        # Update in database
        await conn.execute(
            "UPDATE user_preferences SET experience_levels = $1, updated_at = CURRENT_TIMESTAMP WHERE user_id = $2",
            new_levels,
            user['id']
        )

        print("\n✅ Successfully updated experience_levels!")

        # Also add United Kingdom and Luxembourg to countries
        current_countries = current_prefs['preferred_countries']
        print(f"\nCurrent preferred_countries: {current_countries}")

        if 'United Kingdom' not in current_countries:
            new_countries = current_countries + ['United Kingdom', 'Luxembourg']
            print(f"Adding: United Kingdom, Luxembourg")

            await conn.execute(
                "UPDATE user_preferences SET preferred_countries = $1, updated_at = CURRENT_TIMESTAMP WHERE user_id = $2",
                new_countries,
                user['id']
            )
            print("✅ Updated countries too!")

        await conn.close()

        # Verify
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)

        conn = await db.get_connection()
        updated = await conn.fetchrow('SELECT experience_levels, preferred_countries FROM user_preferences WHERE user_id = $1', user['id'])

        print(f"\n✅ Experience Levels: {updated['experience_levels']}")
        print(f"✅ Preferred Countries: {updated['preferred_countries']}")

        # Count available jobs now
        job_count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM jobs
            WHERE job_type = 'hr'
            AND country = ANY($1)
            AND experience_level = ANY($2)
            AND (applied = FALSE OR applied IS NULL)
            AND (rejected = FALSE OR rejected IS NULL)
        """, updated['preferred_countries'], updated['experience_levels'])

        print(f"\n🎉 HR user can now see {job_count} jobs!")

        await conn.close()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(fix_hr_experience())
    exit(0 if success else 1)
