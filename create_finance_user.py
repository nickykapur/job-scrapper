#!/usr/bin/env python3
"""
Create Finance User Account - FP&A Analyst, Fund Accounting, Credit Analyst
Sets up account for finance, accounting, and financial analysis roles
"""

import asyncio
from user_database import UserDatabase


async def create_finance_user():
    """Create Finance user account for tracking finance and accounting roles"""

    print("=" * 60)
    print("CREATE FINANCE USER - FP&A, FUND ACCOUNTING, CREDIT ANALYST")
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

        print("\n[STEP 1] Creating Finance user account...")
        print("-" * 60)

        username = "finance"
        email = "finance@jobtracker.local"
        password = "FinancePro2024!"  # Strong password for finance professional
        full_name = "Finance - FP&A & Accounting"

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
        # STEP 2: Set Finance-specific preferences
        # ================================================================

        print("\n[STEP 2] Setting Finance/Accounting preferences...")
        print("-" * 60)

        # Finance user preferences
        finance_preferences = {
            # Job types - Finance/Accounting roles
            "job_types": ["finance", "accounting", "financial_analysis"],

            # Keywords for Finance jobs
            "keywords": [
                # FP&A Roles
                "FP&A Analyst",
                "FP&A",
                "Financial Planning and Analysis",
                "Financial Planning Analyst",
                "Financial Analyst",
                "Junior Financial Analyst",
                "Financial Planning",
                "Budgeting Analyst",
                "Forecasting Analyst",

                # Fund Accounting
                "Fund Accounting",
                "Fund Accountant",
                "Fund Accounting Associate",
                "Fund Administrator",
                "Investment Accounting",
                "Portfolio Accounting",

                # Fund Operations
                "Fund Operations",
                "Fund Operations Analyst",
                "Fund Operations Associate",
                "Investment Operations",
                "Asset Management Operations",

                # Credit Analysis
                "Credit Analyst",
                "Credit Risk Analyst",
                "Junior Credit Analyst",
                "Credit Analysis",
                "Risk Analyst",

                # General Finance/Accounting
                "Financial Reporting",
                "Management Accountant",
                "Accountant",
                "Junior Accountant",
                "Accounting Analyst",
                "Finance Associate",
                "Finance Analyst",
                "Financial Controller",
                "Assistant Controller",

                # Treasury & Cash Management
                "Treasury Analyst",
                "Cash Management",
                "Treasury Associate",

                # Corporate Finance
                "Corporate Finance",
                "Finance Business Partner",
                "Financial Reporting Analyst",

                # Related Skills
                "Financial Modeling",
                "Variance Analysis",
                "Financial Statements",
                "Month End Close",
                "Consolidation"
            ],

            # Excluded keywords (avoid these)
            "excluded_keywords": [
                "CFO",             # Too senior
                "Director",        # Too senior
                "VP",             # Too senior
                "Head of",        # Too senior
                "Chief",          # Too senior
                "10+ years",      # Too senior
                "15+ years",      # Too senior
                "Tax",            # Different specialization
                "Audit Partner",  # Too senior
                "Managing Director"  # Too senior
            ],

            # Experience levels - Entry to Mid level
            "experience_levels": ["entry", "junior", "mid"],
            "exclude_senior": True,  # Exclude senior roles

            # English-speaking countries only (excluding Panama, Spain, Chile; adding UK)
            "preferred_countries": [
                "Ireland",
                "United Kingdom",
                "Netherlands",
                "Germany",
                "Sweden",
                "Belgium",
                "Denmark",
                "Luxembourg"
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
            preferences=finance_preferences
        )

        if not success:
            print("⚠️  Failed to set preferences, but user account was created")
            return False

        print("✅ Preferences set successfully!")
        print("\nPreference Summary:")
        print(f"   Job Types: Finance, Accounting, FP&A")
        print(f"   Experience: Entry to Mid-Level")
        print(f"   Countries: {len(finance_preferences['preferred_countries'])} English-speaking countries")
        print(f"   Keywords: {len(finance_preferences['keywords'])} finance terms")

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
        print("FINANCE USER SETUP COMPLETE!")
        print("=" * 60)

        print("\n📋 Account Summary:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print(f"   User ID: {user['id']}")
        print(f"   Account Type: Regular User")

        print("\n🔍 Job Preferences:")
        print("   • Job Types: FP&A, Fund Accounting, Credit Analysis, Finance")
        print("   • Experience: Entry to Mid-Level (excluding senior)")
        print("   • Locations: 8 English-speaking countries (excl. Panama, Spain, Chile)")
        print("   • Focus: Financial Planning, Fund Operations, Accounting")

        print("\n🔍 Search Terms Include:")
        print("   • FP&A Analyst, Financial Planning and Analysis")
        print("   • Fund Accounting Associate, Fund Accountant")
        print("   • Fund Operations Analyst, Investment Operations")
        print("   • Credit Analyst, Credit Risk Analyst")
        print("   • Financial Analyst, Accounting Analyst")

        print("\n🌍 Countries Covered:")
        print("   • Ireland, United Kingdom")
        print("   • Netherlands, Germany, Sweden")
        print("   • Belgium, Denmark, Luxembourg")
        print("   ❌ Excluded: Panama, Spain, Chile (non-English focus)")

        print("\n🚀 Next Steps:")
        print("   1. Update GitHub Actions workflow to scrape for Finance user")
        print("   2. Add finance search terms to daily_single_country_scraper.py")
        print("   3. Finance user can login at:")
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

    print("🎯 Finance User Setup - FP&A, Fund Accounting, Credit Analyst")
    print()
    print("This script will create the 'finance' user account for tracking")
    print("finance and accounting roles across English-speaking countries.")
    print()
    print("Job Types: FP&A Analyst, Fund Accounting, Fund Operations, Credit Analyst")
    print("Countries: Ireland, UK, Netherlands, Germany, Sweden, Belgium, Denmark, Luxembourg")
    print("Excluded: Panama, Spain, Chile (non-English speaking)")
    print()

    success = asyncio.run(create_finance_user())
    sys.exit(0 if success else 1)
