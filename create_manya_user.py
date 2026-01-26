#!/usr/bin/env python3
"""
Create Manya User Account - Digital Marketing & Analytics Professional
Sets up account for Manya Gahlot - MSc Digital Marketing student in Dublin
"""

import asyncio
from user_database import UserDatabase


async def create_manya_user():
    """Create Manya user account for tracking digital marketing and analytics roles"""

    print("=" * 60)
    print("CREATE MANYA USER - DIGITAL MARKETING & ANALYTICS")
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

        print("\n[STEP 1] Creating Manya user account...")
        print("-" * 60)

        username = "manya"
        email = "gahlot1manya@gmail.com"
        password = "pass123"
        full_name = "Manya Gahlot"

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
        # STEP 2: Set Digital Marketing preferences
        # ================================================================

        print("\n[STEP 2] Setting Digital Marketing & Analytics preferences...")
        print("-" * 60)

        # Manya's preferences based on her CV
        manya_preferences = {
            # Job types - Digital Marketing & CRM roles
            "job_types": ["digital_marketing", "marketing", "crm", "analytics"],

            # Keywords from Manya's skills and experience
            "keywords": [
                # Digital Marketing
                "Digital Marketing",
                "Digital Marketing Executive",
                "Digital Marketing Manager",
                "Digital Marketing Specialist",
                "Digital Marketing Coordinator",

                # PPC & Paid Media
                "PPC",
                "PPC Executive",
                "Paid Media",
                "Paid Social",
                "Google Ads",
                "Meta Ads",
                "LinkedIn Ads",
                "Campaign Manager",

                # Social Media
                "Social Media",
                "Social Media Manager",
                "Social Media Executive",
                "Social Media Marketing",
                "Social Media Coordinator",
                "Content Creator",

                # Analytics & Data
                "Marketing Analytics",
                "Analytics",
                "GA4",
                "Google Analytics",
                "Data Analyst Marketing",

                # CRM & Email
                "CRM",
                "CRM Manager",
                "CRM Executive",
                "Email Marketing",
                "Marketing Automation",
                "HubSpot",
                "Salesforce Marketing",

                # SEO & Content
                "SEO",
                "SEO Executive",
                "SEO Specialist",
                "Content Marketing",
                "Content Strategy",

                # General Marketing
                "Marketing Executive",
                "Marketing Coordinator",
                "Marketing Manager",
                "Marketing Specialist",
                "Junior Marketing",
                "Entry Level Marketing",
                "Graduate Marketing",

                # E-commerce
                "E-commerce Marketing",
                "Performance Marketing",
                "Growth Marketing"
            ],

            # Excluded keywords (avoid these - too senior or unrelated)
            "excluded_keywords": [
                "Director",
                "VP",
                "Head of",
                "Chief",
                "CMO",
                "10+ years",
                "Senior Manager"
            ],

            # Experience levels - Entry to Mid level (recent MSc student)
            "experience_levels": ["entry", "junior", "mid"],
            "exclude_senior": True,

            # Location - Dublin based with Stamp 2 visa
            "preferred_countries": ["Ireland"],
            "preferred_cities": ["Dublin"],

            # No specific company exclusions
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
            preferences=manya_preferences
        )

        if not success:
            print("Failed to set preferences, but user account was created")
            return False

        print("Preferences set successfully!")
        print("\nPreference Summary:")
        print(f"   Job Types: Digital Marketing, Marketing, CRM, Analytics")
        print(f"   Experience: Entry to Mid-Level")
        print(f"   Location: Ireland (Dublin)")
        print(f"   Keywords: {len(manya_preferences['keywords'])} marketing terms")

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
        print("MANYA USER SETUP COMPLETE!")
        print("=" * 60)

        print("\nAccount Summary:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print(f"   Full Name: {full_name}")
        print(f"   User ID: {user['id']}")

        print("\nJob Preferences:")
        print("   Job Types: Digital Marketing, CRM, Analytics, Marketing")
        print("   Experience: Entry to Mid-Level")
        print("   Location: Ireland (Dublin)")
        print("   Skills Focus: PPC, Google Ads, Meta Ads, Social Media, SEO, CRM")

        print("\nManya's Background:")
        print("   MSc Digital Marketing & Analytics - Dublin Business School")
        print("   MBA Marketing - O.P. Jindal Global University")
        print("   Experience: CRM & Marketing Manager, Relationship Manager")
        print("   Certifications: Google Digital Marketing, Google Project Management")

        return True

    except Exception as e:
        print(f"\nSetup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys

    print("Manya Gahlot User Setup - Digital Marketing & Analytics")
    print()
    print("This script will create the 'manya' user account for tracking")
    print("digital marketing and analytics roles in Ireland.")
    print()

    success = asyncio.run(create_manya_user())
    sys.exit(0 if success else 1)
