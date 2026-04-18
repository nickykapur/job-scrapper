#!/usr/bin/env python3
"""
Create Carlos user account - Sales, Media Production, Painter, Customer Service
in Long Island NY / Tampa, Jacksonville, Orlando FL
"""

import asyncio
from user_database import UserDatabase


async def create_carlos_user():
    print("=" * 60)
    print("CREATE CARLOS USER - MULTI-ROLE (NY + FL)")
    print("=" * 60)

    db = UserDatabase()

    if not db.use_postgres:
        print("❌ PostgreSQL required for multi-user support")
        return False

    try:
        # STEP 1: Create user account (skip if already exists)
        print("\n[STEP 1] Creating Carlos user account...")
        print("-" * 60)

        user = await db.create_user(
            username="carlos",
            email="carlos@jobtracker.local",
            password="pass123",
            full_name="Carlos",
            is_admin=False
        )

        if not user:
            print("⚠️  User may already exist — fetching existing user...")
            conn = await db.get_connection()
            if conn:
                try:
                    row = await conn.fetchrow("SELECT id, username FROM users WHERE username = 'carlos'")
                    if row:
                        user = {'id': row['id'], 'username': row['username']}
                        print(f"✅ Found existing user ID: {user['id']}")
                    else:
                        print("❌ Could not find or create user")
                        return False
                finally:
                    await db._release(conn)
            else:
                return False
        else:
            print(f"✅ User created! ID: {user['id']}, Username: {user['username']}")

        # STEP 2: Set preferences
        print("\n[STEP 2] Setting preferences...")
        print("-" * 60)

        preferences = {
            # Multiple job types Carlos is open to
            "job_types": ["sales", "media_production", "painter", "customer_service"],

            # Keywords to help match relevant roles in those categories
            "keywords": [
                # Sales
                "Sales Representative", "Sales Associate", "Account Executive",
                "Inside Sales", "Entry Level Sales", "Sales Consultant",
                "Business Development", "SDR", "BDR",

                # Media Production
                "Video Editor", "Video Producer", "Production Assistant",
                "Content Creator", "Videographer", "Media Production",
                "Broadcast", "Motion Graphics", "Multimedia",

                # Painter
                "Painter", "Painting", "Residential Painter",
                "Commercial Painter", "Interior Painter", "Exterior Painter",
                "House Painter",

                # Customer Service
                "Customer Service", "Customer Support", "Customer Care",
                "Call Center", "Customer Success", "Client Services",
                "Service Representative", "Customer Experience",
                "Front Desk", "Guest Services",
            ],

            # Exclude senior/executive roles
            "excluded_keywords": [
                "Director", "VP", "Vice President", "Head of", "Chief",
                "Senior Manager", "General Manager",
            ],

            # Entry to mid level
            "experience_levels": ["entry", "junior", "mid"],
            "exclude_senior": True,

            # United States only
            "preferred_countries": ["United States"],

            # Target cities — enforce_city_filter restricts jobs to these metros
            # Uses substrings that match actual LinkedIn location strings:
            #   "new york" → New York City Metropolitan Area, New York, NY
            #   ", ny" → all New York state locations (covers Long Island cities stored as "City, NY")
            #   "nassau county" → Nassau County, NY (Long Island)
            #   ", fl" → all Florida locations (Tampa, Jacksonville, Orlando once scraped)
            "preferred_cities": [
                "new york",
                ", ny",
                "nassau county",
                ", fl",
                "tampa",
                "jacksonville",
                "orlando",
            ],
            "enforce_city_filter": True,

            "excluded_companies": [],
            "preferred_companies": [],

            "easy_apply_only": False,
            "remote_only": False,

            "email_notifications": True,
            "daily_digest": False,
        }

        success = await db.update_user_preferences(user_id=user['id'], preferences=preferences)

        if not success:
            print("⚠️  Preferences failed to save")
            return False

        print("✅ Preferences saved!")

        # STEP 3: Verify
        print("\n[STEP 3] Verifying...")
        print("-" * 60)

        prefs = await db.get_user_preferences(user['id'])
        if prefs:
            print(f"   Job types:        {prefs.get('job_types')}")
            print(f"   Countries:        {prefs.get('preferred_countries')}")
            print(f"   Cities:           {prefs.get('preferred_cities')}")
            print(f"   Enforce cities:   {prefs.get('enforce_city_filter')}")
            print(f"   Experience:       {prefs.get('experience_levels')}")
            print(f"   Keywords:         {len(prefs.get('keywords', []))} terms")

        print("\n" + "=" * 60)
        print("CARLOS USER SETUP COMPLETE")
        print("=" * 60)
        print(f"\n  Username:  carlos")
        print(f"  Password:  pass123")
        print(f"  Locations: Long Island / New York, Tampa, Jacksonville, Orlando")
        print(f"  Focus:     Sales | Media Production | Painter | Customer Service")

        return True

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = asyncio.run(create_carlos_user())
    sys.exit(0 if success else 1)
