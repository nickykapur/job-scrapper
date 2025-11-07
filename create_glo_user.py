#!/usr/bin/env python3
"""
Create Glo User Account - Cybersecurity/SOC Analyst
Sets up account for cybersecurity jobs in Spanish-speaking regions
"""

import asyncio
from user_database import UserDatabase


async def create_glo_user():
    """Create Glo user account for Cybersecurity/SOC Analyst job tracking"""

    print("=" * 60)
    print("CREATE GLO USER - CYBERSECURITY/SOC ANALYST")
    print("=" * 60)

    db = UserDatabase()

    if not db.use_postgres:
        print("❌ PostgreSQL required for multi-user support")
        print("   Please set DATABASE_URL environment variable")
        return False

    try:
        # ================================================================
        # STEP 1: Create user account
        # ================================================================

        print("\n[STEP 1] Creating Glo user account...")
        print("-" * 60)

        username = "glo"
        email = "glo@jobtracker.local"
        password = "GloSecure2024!"  # Strong password for cybersecurity professional
        full_name = "Glo - Cybersecurity"

        user = await db.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            is_admin=False  # Regular user
        )

        if not user:
            print("❌ Failed to create user. Possible reasons:")
            print("   - Username already exists")
            print("   - Email already exists")
            return False

        print(f"✅ User account created!")
        print(f"   User ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")

        # ================================================================
        # STEP 2: Set Cybersecurity-specific preferences
        # ================================================================

        print("\n[STEP 2] Setting Cybersecurity/SOC preferences...")
        print("-" * 60)

        # Cybersecurity user preferences
        cyber_preferences = {
            # Job types - Cybersecurity/Security roles
            "job_types": ["cybersecurity", "security", "soc"],

            # Keywords for Cybersecurity jobs (English and Spanish)
            "keywords": [
                # English terms
                "SOC Analyst",
                "Cybersecurity Analyst",
                "Security Analyst",
                "Information Security Analyst",
                "Cyber Security",
                "Security Operations",
                "SOC",
                "SIEM",
                "Threat Detection",
                "Incident Response",
                "Security Engineer",
                "Junior SOC Analyst",
                "Entry Level Cybersecurity",

                # Spanish terms
                "Analista SOC",
                "Analista de Ciberseguridad",
                "Analista de Seguridad",
                "Especialista en Seguridad",
                "Seguridad de la Información",
                "Operaciones de Seguridad",
                "Respuesta a Incidentes",
                "Ingeniero de Seguridad"
            ],

            # Excluded keywords (avoid these)
            "excluded_keywords": [
                "Physical Security",  # Not cybersecurity
                "Security Guard",     # Physical security
                "Consultant",         # Usually requires more experience
            ],

            # Experience levels - All levels
            "experience_levels": ["junior", "mid", "senior"],
            "exclude_senior": False,  # Include senior roles

            # Locations - Spanish-speaking regions
            "preferred_countries": ["Spain", "Panama"],
            "preferred_cities": ["Madrid", "Barcelona", "Panama City"],

            # No company exclusions
            "excluded_companies": [],
            "preferred_companies": [],

            # Filters
            "easy_apply_only": False,  # Show all jobs
            "remote_only": False,      # Include onsite/hybrid

            # Notifications
            "email_notifications": True,
            "daily_digest": False
        }

        success = await db.update_user_preferences(
            user_id=user['id'],
            preferences=cyber_preferences
        )

        if not success:
            print("⚠️  Failed to set preferences, but user account was created")
            return False

        print("✅ Preferences set successfully!")
        print("\nPreference Summary:")
        print(f"   Job Types: Cybersecurity, Security, SOC")
        print(f"   Experience: All levels (Junior to Senior)")
        print(f"   Countries: {', '.join(cyber_preferences['preferred_countries'])}")
        print(f"   Keywords: {len(cyber_preferences['keywords'])} cybersecurity terms (English + Spanish)")

        # ================================================================
        # STEP 3: Verify setup
        # ================================================================

        print("\n[STEP 3] Verifying setup...")
        print("-" * 60)

        # Get user preferences back
        prefs = await db.get_user_preferences(user['id'])

        if prefs:
            print("✅ Preferences verified!")
            print(f"   Job types: {prefs.get('job_types')}")
            print(f"   Countries: {prefs.get('preferred_countries')}")
        else:
            print("⚠️  Could not verify preferences")

        # ================================================================
        # SUMMARY
        # ================================================================

        print("\n" + "=" * 60)
        print("GLO USER SETUP COMPLETE!")
        print("=" * 60)

        print("\n📋 Account Summary:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print(f"   User ID: {user['id']}")
        print(f"   Account Type: Regular User")

        print("\n🔍 Job Preferences:")
        print("   • Job Types: Cybersecurity, SOC Analyst, Security")
        print("   • Experience: Junior to Senior")
        print("   • Locations: Spain, Panama")
        print("   • Languages: English + Spanish search terms")

        print("\n🔍 Search Terms Include:")
        print("   English: SOC Analyst, Cybersecurity Analyst, Security Operations")
        print("   Spanish: Analista SOC, Analista de Ciberseguridad, Seguridad")

        print("\n🚀 Next Steps:")
        print("   1. Update GitHub Actions workflow to scrape for Glo user")
        print("   2. Add cybersecurity search terms to daily_single_country_scraper.py")
        print("   3. Glo can login at:")
        print("      POST /api/auth/login")
        print(f'      {{"username":"{username}","password":"{password}"}}')

        print("\n⚠️  IMPORTANT: Save these credentials!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")

        return True

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys

    print("🎯 Glo User Setup - Cybersecurity/SOC Analyst")
    print()
    print("This script will create the 'Glo' user account for tracking")
    print("cybersecurity and SOC analyst jobs in Spanish-speaking regions.")
    print()
    print("Target Regions: Spain, Panama")
    print("Job Types: SOC Analyst, Cybersecurity Analyst, Security roles")
    print("Languages: English + Spanish")
    print()

    success = asyncio.run(create_glo_user())
    sys.exit(0 if success else 1)
