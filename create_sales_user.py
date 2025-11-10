#!/usr/bin/env python3
"""
Create Sales User Account - Account Manager, BDR, Sales Development
Sets up account for sales, SaaS, and business development roles
"""

import asyncio
from user_database import UserDatabase


async def create_sales_user():
    """Create Sales user account for tracking sales and business development roles"""

    print("=" * 60)
    print("CREATE SALES USER - ACCOUNT MANAGER, BDR, SDR, AE")
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

        print("\n[STEP 1] Creating Sales user account...")
        print("-" * 60)

        username = "sales"
        email = "sales@jobtracker.local"
        password = "SalesPro2024!"  # Strong password for sales professional
        full_name = "Sales - Business Development"

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
        # STEP 2: Set Sales-specific preferences
        # ================================================================

        print("\n[STEP 2] Setting Sales/Business Development preferences...")
        print("-" * 60)

        # Sales user preferences
        sales_preferences = {
            # Job types - Sales/Business Development roles
            "job_types": ["sales", "business_development", "account_management"],

            # Keywords for Sales jobs
            "keywords": [
                # Account Management
                "Account Manager",
                "Account Executive",
                "Customer Success Manager",
                "Client Success",

                # Business Development
                "BDR",
                "Business Development Representative",
                "Business Development Manager",
                "Sales Development Representative",
                "SDR",

                # Sales Roles
                "Sales",
                "Inside Sales",
                "Outbound Sales",
                "Sales Representative",
                "Sales Associate",
                "Junior Sales",
                "Entry Level Sales",

                # SaaS Specific
                "SaaS Sales",
                "SaaS BDR",
                "SaaS SDR",
                "SaaS Account Executive",
                "B2B Sales",
                "Enterprise Sales",

                # Related
                "Revenue",
                "Pipeline",
                "Lead Generation",
                "Prospecting"
            ],

            # Excluded keywords (avoid these)
            "excluded_keywords": [
                "Director",       # Too senior
                "VP",            # Too senior
                "Head of",       # Too senior
                "Chief",         # Too senior
                "Retail",        # Not SaaS/B2B
                "Insurance",     # Different sales type
                "Real Estate"    # Different sales type
            ],

            # Experience levels - Entry to Mid level
            "experience_levels": ["entry", "junior", "mid"],
            "exclude_senior": True,  # Exclude senior roles

            # All countries
            "preferred_countries": [
                "Ireland", "Spain", "Panama", "Chile",
                "Netherlands", "Germany", "Sweden", "Belgium",
                "Denmark", "Luxembourg"
            ],
            "preferred_cities": [],

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
            preferences=sales_preferences
        )

        if not success:
            print("⚠️  Failed to set preferences, but user account was created")
            return False

        print("✅ Preferences set successfully!")
        print("\nPreference Summary:")
        print(f"   Job Types: Sales, BDR, Account Management")
        print(f"   Experience: Entry to Mid-Level")
        print(f"   Countries: All 10 countries")
        print(f"   Keywords: {len(sales_preferences['keywords'])} sales terms")

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
            print(f"   Countries: {len(prefs.get('preferred_countries', []))} countries")
        else:
            print("⚠️  Could not verify preferences")

        # ================================================================
        # SUMMARY
        # ================================================================

        print("\n" + "=" * 60)
        print("SALES USER SETUP COMPLETE!")
        print("=" * 60)

        print("\n📋 Account Summary:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print(f"   User ID: {user['id']}")
        print(f"   Account Type: Regular User")

        print("\n🔍 Job Preferences:")
        print("   • Job Types: Sales, BDR, SDR, Account Executive")
        print("   • Experience: Entry to Mid-Level (excluding senior)")
        print("   • Locations: All 10 countries")
        print("   • Focus: SaaS, B2B Sales")

        print("\n🔍 Search Terms Include:")
        print("   • Account Manager, Account Executive")
        print("   • BDR, Business Development Representative")
        print("   • SDR, Sales Development Representative")
        print("   • SaaS Sales, B2B Sales")

        print("\n🚀 Next Steps:")
        print("   1. Update GitHub Actions workflow to scrape for Sales user")
        print("   2. Add sales search terms to daily_single_country_scraper.py")
        print("   3. Sales user can login at:")
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

    print("🎯 Sales User Setup - Account Manager, BDR, SDR, AE")
    print()
    print("This script will create the 'sales' user account for tracking")
    print("sales and business development roles across all countries.")
    print()
    print("Job Types: Account Manager, Account Executive, BDR, SDR, Sales")
    print("Focus: SaaS, B2B Sales, Business Development")
    print()

    success = asyncio.run(create_sales_user())
    sys.exit(0 if success else 1)
