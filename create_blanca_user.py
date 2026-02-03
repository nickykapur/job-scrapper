#!/usr/bin/env python3
"""
Create Blanca User Account - Events & Hospitality Professional
Sets up account for Blanca Diaz Benitez - Events Executive in Dublin
"""

import asyncio
from user_database import UserDatabase


async def create_blanca_user():
    """Create Blanca user account for tracking events and hospitality roles"""

    print("=" * 60)
    print("CREATE BLANCA USER - EVENTS & HOSPITALITY")
    print("=" * 60)

    db = UserDatabase()

    if not db.use_postgres:
        print("PostgreSQL required for multi-user support")
        print("   Please set DATABASE_URL environment variable")
        return False

    try:
        # ================================================================
        # STEP 1: Create user account
        # ================================================================

        print("\n[STEP 1] Creating Blanca user account...")
        print("-" * 60)

        username = "blanca"
        email = "bladiaben@gmail.com"
        password = "pass123"
        full_name = "Blanca Diaz Benitez"

        user = await db.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            is_admin=False
        )

        if not user:
            print("Failed to create user. Possible reasons:")
            print("   - Username already exists")
            print("   - Email already exists")
            return False

        print(f"User account created!")
        print(f"   User ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")

        # ================================================================
        # STEP 2: Set Events/Hospitality preferences
        # ================================================================

        print("\n[STEP 2] Setting Events & Hospitality preferences...")
        print("-" * 60)

        # Blanca's preferences based on her CV
        blanca_preferences = {
            # Job types - Events & Hospitality
            "job_types": ["events", "hospitality", "event_management"],

            # Keywords from Blanca's skills and experience
            "keywords": [
                # Event Management
                "Event Manager",
                "Event Coordinator",
                "Event Executive",
                "Event Planner",
                "Events Manager",
                "Events Coordinator",
                "Events Executive",
                "Junior Event Manager",
                "Event Assistant",
                "Events Assistant",

                # Conference & Meetings
                "Conference Manager",
                "Conference Coordinator",
                "Meeting Planner",
                "Meeting Coordinator",
                "Meetings and Events",
                "Corporate Events",
                "Corporate Event Manager",
                "Corporate Event Coordinator",

                # Hospitality
                "Hospitality Manager",
                "Hospitality Coordinator",
                "Venue Manager",
                "Venue Coordinator",
                "Banquet Manager",
                "Banquet Coordinator",
                "Catering Manager",
                "Catering Coordinator",
                "Hotel Events",

                # Weddings & Social
                "Wedding Planner",
                "Wedding Coordinator",
                "Social Events Manager",
                "Social Events Coordinator",

                # Tourism & MICE
                "Tourism Manager",
                "Business Tourism",
                "MICE",
                "MICE Coordinator",
                "MICE Manager",

                # Marketing & Communications for Events
                "Event Marketing",
                "Event Marketing Manager",
                "Sponsorship Coordinator",
                "Sponsorship Manager",

                # Protocol
                "Protocol Officer",
                "Protocol Manager",

                # Entry level
                "Event Intern",
                "Hospitality Assistant",
                "Events Trainee"
            ],

            # Excluded keywords (avoid these - too senior or unrelated)
            "excluded_keywords": [
                "Director",
                "VP",
                "Head of",
                "Chief",
                "10+ years",
                "15+ years",
                "Senior Director"
            ],

            # Experience levels - Entry to Mid level
            "experience_levels": ["entry", "junior", "mid"],
            "exclude_senior": True,

            # Location - Ireland (Dublin based)
            "preferred_countries": ["Ireland"],
            "preferred_cities": ["Dublin"],

            # Company preferences
            "excluded_companies": [],
            "preferred_companies": [],

            # Filters
            "easy_apply_only": False,
            "remote_only": False,

            # Notifications
            "email_notifications": True,
            "daily_digest": True
        }

        success = await db.update_user_preferences(
            user_id=user['id'],
            preferences=blanca_preferences
        )

        if not success:
            print("Failed to set preferences, but user account was created")
            return False

        print("Preferences set successfully!")
        print("\nPreference Summary:")
        print(f"   Job Types: Events, Hospitality, Event Management")
        print(f"   Experience: Entry to Mid-Level")
        print(f"   Location: Ireland (Dublin)")
        print(f"   Keywords: {len(blanca_preferences['keywords'])} events/hospitality terms")

        # ================================================================
        # STEP 3: Verify setup
        # ================================================================

        print("\n[STEP 3] Verifying setup...")
        print("-" * 60)

        prefs = await db.get_user_preferences(user['id'])

        if prefs:
            print("Preferences verified!")
            print(f"   Job types: {prefs.get('job_types')}")
            print(f"   Countries: {prefs.get('preferred_countries')}")
        else:
            print("Could not verify preferences")

        # ================================================================
        # SUMMARY
        # ================================================================

        print("\n" + "=" * 60)
        print("BLANCA USER SETUP COMPLETE!")
        print("=" * 60)

        print("\nAccount Summary:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print(f"   Full Name: {full_name}")
        print(f"   User ID: {user['id']}")

        print("\nJob Preferences:")
        print("   Job Types: Events, Hospitality, Event Management")
        print("   Experience: Entry to Mid-Level")
        print("   Location: Ireland (Dublin)")
        print("   Skills Focus: Event Planning, Conference Management, Hospitality, MICE")

        print("\nBlanca's Background:")
        print("   Master's in Event Organization, Protocol & Business Tourism")
        print("   - Ostelea School / EAE Business School, Barcelona")
        print("   Current: Events Executive - Ashville Media Group, Dublin")
        print("   Previous: Junior Meeting & Events Coordinator - Clontarf Castle Hotel")
        print("   Languages: Spanish (Native), English (C1), Italian (A2)")

        print("\n" + "=" * 60)
        print("SETUP COMPLETE - READY TO RUN")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\nSetup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys

    print("Blanca Diaz Benitez User Setup - Events & Hospitality")
    print()
    print("This script will create the 'blanca' user account for tracking")
    print("events and hospitality roles in Ireland.")
    print()

    success = asyncio.run(create_blanca_user())
    sys.exit(0 if success else 1)
