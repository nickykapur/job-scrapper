#!/usr/bin/env python3
"""
Reset password for inigotrabaja user
"""

import asyncio
import os
import asyncpg
from auth_utils import hash_password
from datetime import datetime


async def reset_password():
    """Reset password for inigotrabaja user"""

    print("=" * 60)
    print("RESET PASSWORD: inigotrabaja")
    print("=" * 60)

    db_url = os.environ.get('DATABASE_URL')

    if not db_url:
        print("❌ DATABASE_URL not set")
        return False

    try:
        conn = await asyncpg.connect(db_url)

        print("\n[STEP 1] Finding user...")
        print("-" * 60)

        user = await conn.fetchrow(
            "SELECT id, username, email FROM users WHERE username = $1",
            "inigotrabaja"
        )

        if not user:
            print("❌ User 'inigotrabaja' not found")
            await conn.close()
            return False

        print(f"✅ User found!")
        print(f"   User ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")

        print("\n[STEP 2] Resetting password...")
        print("-" * 60)

        # Hash the new password
        new_password_hash = hash_password("pass123")

        # Update the password
        await conn.execute(
            """
            UPDATE users
            SET password_hash = $1, updated_at = $2
            WHERE id = $3
            """,
            new_password_hash, datetime.utcnow(), user['id']
        )

        print("✅ Password reset successfully!")

        print("\n" + "=" * 60)
        print("PASSWORD RESET COMPLETE!")
        print("=" * 60)

        print("\n📋 New Credentials:")
        print(f"   Username: inigotrabaja")
        print(f"   Password: pass123")

        await conn.close()
        return True

    except Exception as e:
        print(f"\n❌ Password reset failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = asyncio.run(reset_password())
    sys.exit(0 if success else 1)
