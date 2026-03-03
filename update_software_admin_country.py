#!/usr/bin/env python3
"""
Update software_admin preferred countries to Panama only
"""

import asyncio
from user_database import UserDatabase


async def update():
    db = UserDatabase()
    if not db.use_postgres:
        print("❌ PostgreSQL required")
        return False

    user = await db.get_user_by_username("software_admin")
    if not user:
        print("❌ User 'software_admin' not found")
        return False

    print(f"✅ Found user: {user['username']} (ID: {user['id']})")

    success = await db.update_user_preferences(
        user_id=user['id'],
        preferences={"preferred_countries": ["Panama"]}
    )

    if not success:
        print("❌ Failed to update preferences")
        return False

    prefs = await db.get_user_preferences(user['id'])
    print(f"✅ Updated! preferred_countries = {prefs.get('preferred_countries')}")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if asyncio.run(update()) else 1)
