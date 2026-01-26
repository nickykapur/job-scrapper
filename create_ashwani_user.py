#!/usr/bin/env python3
"""
Create Ashwani User Account - Digital Marketing & Communications Professional
Sets up account for Ashwani Solanki - 3+ years experience, MSc student in Dublin
"""

import asyncio
from user_database import UserDatabase


async def create_ashwani_user():
    """Create Ashwani user account for tracking digital marketing and communications roles"""

    print("=" * 60)
    print("CREATE ASHWANI USER - DIGITAL MARKETING & COMMUNICATIONS")
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

        print("\n[STEP 1] Creating Ashwani user account...")
        print("-" * 60)

        username = "ashwani"
        email = "ashwani.a.solanki@gmail.com"
        password = "pass123"
        full_name = "Ashwani Solanki"

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
        # STEP 2: Set Digital Marketing & Communications preferences
        # ================================================================

        print("\n[STEP 2] Setting Digital Marketing & Communications preferences...")
        print("-" * 60)

        # Ashwani's preferences based on his CV - 3+ years experience
        ashwani_preferences = {
            # Job types - Digital Marketing & Communications roles
            "job_types": ["digital_marketing", "marketing", "communications", "content"],

            # Keywords from Ashwani's skills and experience
            "keywords": [
                # Digital Marketing
                "Digital Marketing",
                "Digital Marketing Manager",
                "Digital Marketing Executive",
                "Digital Marketing Specialist",
                "Digital Marketing Coordinator",

                # Communications
                "Communications",
                "Communications Manager",
                "Communications Executive",
                "Communications Specialist",
                "Marketing Communications",
                "MarCom",
                "Corporate Communications",
                "Public Relations",
                "PR Executive",

                # Paid Media & Advertising
                "Paid Media",
                "Paid Social",
                "Meta Ads",
                "Facebook Ads",
                "Google Ads",
                "PPC",
                "Performance Marketing",
                "Media Buyer",
                "Advertising",

                # Social Media
                "Social Media",
                "Social Media Manager",
                "Social Media Marketing",
                "Social Media Executive",
                "Community Manager",
                "Content Creator",

                # CRM & Marketing Tech
                "CRM",
                "CRM Manager",
                "HubSpot",
                "Salesforce",
                "Zoho CRM",
                "Marketing Automation",
                "Email Marketing",

                # Content & Creative
                "Content Marketing",
                "Content Manager",
                "Content Strategist",
                "Creative Marketing",
                "Brand Marketing",
                "Brand Manager",
                "Copywriter",

                # SEO & Analytics
                "SEO",
                "SEO Specialist",
                "SEO Executive",
                "Analytics",
                "Marketing Analytics",
                "Google Analytics",

                # General Marketing
                "Marketing Manager",
                "Marketing Executive",
                "Marketing Coordinator",
                "Marketing Specialist",
                "Growth Marketing",
                "Campaign Manager",

                # Sector-specific (from his experience)
                "Fitness Marketing",
                "Hospitality Marketing",
                "Real Estate Marketing",
                "B2B Marketing",
                "Retail Marketing"
            ],

            # Excluded keywords
            "excluded_keywords": [
                "Director",
                "VP",
                "Head of",
                "Chief",
                "CMO",
                "10+ years"
            ],

            # Experience levels - Junior to Mid level (3+ years experience)
            "experience_levels": ["junior", "mid"],
            "exclude_senior": True,

            # Location - Dublin based
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
            preferences=ashwani_preferences
        )

        if not success:
            print("Failed to set preferences, but user account was created")
            return False

        print("Preferences set successfully!")
        print("\nPreference Summary:")
        print(f"   Job Types: Digital Marketing, Marketing, Communications, Content")
        print(f"   Experience: Junior to Mid-Level")
        print(f"   Location: Ireland (Dublin)")
        print(f"   Keywords: {len(ashwani_preferences['keywords'])} marketing terms")

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
        print("ASHWANI USER SETUP COMPLETE!")
        print("=" * 60)

        print("\nAccount Summary:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print(f"   Full Name: {full_name}")
        print(f"   User ID: {user['id']}")

        print("\nJob Preferences:")
        print("   Job Types: Digital Marketing, Communications, Content, Marketing")
        print("   Experience: Junior to Mid-Level (3+ years)")
        print("   Location: Ireland (Dublin)")
        print("   Skills Focus: Meta Ads, Google Ads, SEO, CRM, Content Creation")

        print("\nAshwani's Background:")
        print("   MSc Digital Marketing & Analytics - Dublin Business School")
        print("   MBA (Marketing & IT)")
        print("   Current: Marketing Manager at Fit20 Sandyford")
        print("   Experience: Fitness, Hospitality, Real Estate sectors")
        print("   Certifications: Google Analytics, HubSpot Digital Marketing")

        return True

    except Exception as e:
        print(f"\nSetup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys

    print("Ashwani Solanki User Setup - Digital Marketing & Communications")
    print()
    print("This script will create the 'ashwani' user account for tracking")
    print("digital marketing and communications roles in Ireland.")
    print()

    success = asyncio.run(create_ashwani_user())
    sys.exit(0 if success else 1)
