#!/usr/bin/env python3
"""
Create Melis User Account - Molecular Biology & Biotechnology Professional
Sets up account for Melis Niyazieva - MSc Molecular and Cellular Biology student in Munich
"""

import asyncio
from user_database import UserDatabase


async def create_melis_user():
    """Create Melis user account for tracking biotech and life sciences roles"""

    print("=" * 60)
    print("CREATE MELIS USER - MOLECULAR BIOLOGY & BIOTECHNOLOGY")
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

        print("\n[STEP 1] Creating Melis user account...")
        print("-" * 60)

        username = "melis"
        email = "melisniyazieva@gmail.com"
        password = "pass123"
        full_name = "Melis Niyazieva"

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
        # STEP 2: Set Biotech/Life Sciences preferences
        # ================================================================

        print("\n[STEP 2] Setting Biotech & Life Sciences preferences...")
        print("-" * 60)

        # Melis's preferences based on her CV
        melis_preferences = {
            # Job types - Biotech & Life Sciences
            # NOTE: "biotech" job type needs to be added to the scraper
            "job_types": ["biotech", "life_sciences"],

            # Keywords from Melis's skills and experience
            "keywords": [
                # Research Scientist roles
                "Research Scientist",
                "Scientist",
                "Research Associate",
                "Junior Scientist",
                "Associate Scientist",
                "R&D Scientist",
                "Staff Scientist",

                # Molecular Biology specific
                "Molecular Biologist",
                "Molecular Biology",
                "Cell Biologist",
                "Cell Biology",
                "Cellular Biology",

                # Gene Editing & Gene Therapy
                "Gene Editing",
                "Gene Therapy",
                "CRISPR",
                "CRISPR Scientist",
                "Genome Editing",
                "Genetic Engineering",

                # Cell Culture & Lab
                "Cell Culture",
                "Cell Culture Scientist",
                "Lab Scientist",
                "Laboratory Scientist",
                "Lab Technician",
                "Research Technician",

                # Viral Vectors
                "AAV",
                "Viral Vector",
                "Vector Production",
                "VLP",
                "Virus-Like Particle",

                # Biotech specific
                "Biotechnology",
                "Biotech",
                "Biologics",
                "Biopharmaceutical",
                "Biopharma",

                # Process Development
                "Process Development",
                "Upstream Process",
                "Downstream Process",
                "Process Scientist",

                # Analytical
                "Flow Cytometry",
                "FACS",
                "qPCR",
                "ddPCR",
                "ELISA",
                "Western Blot",

                # Other relevant
                "Life Sciences",
                "Stem Cell",
                "iPS Cell",
                "Cardiomyocyte",
                "Immunology",
                "Preclinical",

                # German terms (for Germany)
                "Wissenschaftler",
                "Laborant",
                "Biotechnologe",
                "Molekularbiologe",
                "Forschung"
            ],

            # Excluded keywords (avoid these - too senior or unrelated)
            "excluded_keywords": [
                "Director",
                "VP",
                "Head of",
                "Chief",
                "CSO",
                "Principal Scientist",
                "10+ years",
                "15+ years",
                "Senior Director",
                "Executive"
            ],

            # Experience levels - Entry to Mid level (MSc student)
            "experience_levels": ["entry", "junior", "mid"],
            "exclude_senior": True,

            # Location - Germany & Switzerland (EU work eligible)
            "preferred_countries": ["Germany", "Switzerland"],
            "preferred_cities": ["Munich", "Berlin", "Frankfurt", "Hamburg", "Basel", "Zurich", "Geneva", "Bern"],

            # Company preferences - Pharma & Biotech companies
            "excluded_companies": [],
            "preferred_companies": [
                "Roche",
                "Novartis",
                "Bayer",
                "Merck",
                "Boehringer Ingelheim",
                "BioNTech",
                "CureVac",
                "Helmholtz",
                "Max Planck",
                "Fraunhofer"
            ],

            # Filters
            "easy_apply_only": False,
            "remote_only": False,

            # Notifications
            "email_notifications": True,
            "daily_digest": True
        }

        success = await db.update_user_preferences(
            user_id=user['id'],
            preferences=melis_preferences
        )

        if not success:
            print("Failed to set preferences, but user account was created")
            return False

        print("Preferences set successfully!")
        print("\nPreference Summary:")
        print(f"   Job Types: Biotech, Life Sciences")
        print(f"   Experience: Entry to Mid-Level")
        print(f"   Location: Germany (Munich, Berlin, Frankfurt, Hamburg)")
        print(f"   Keywords: {len(melis_preferences['keywords'])} biotech/life sciences terms")

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
        print("MELIS USER SETUP COMPLETE!")
        print("=" * 60)

        print("\nAccount Summary:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print(f"   Full Name: {full_name}")
        print(f"   User ID: {user['id']}")

        print("\nJob Preferences:")
        print("   Job Types: Biotech, Life Sciences")
        print("   Experience: Entry to Mid-Level")
        print("   Location: Germany & Switzerland")
        print("   Cities: Munich, Berlin, Frankfurt, Hamburg, Basel, Zurich, Geneva, Bern")
        print("   Skills Focus: CRISPR, Cell Culture, AAV, VLP, Molecular Cloning")

        print("\nMelis's Background:")
        print("   MSc Molecular and Cellular Biology - LMU Munich")
        print("   BSc Molecular Biology and Genetics - METU, Turkey")
        print("   Master's Thesis: VLP Engineering at Helmholtz Zentrum")
        print("   Experience: Roche, Max Delbruck Center, LMU Klinikum")
        print("   Certifications: CRISPR, AAV production, Flow Cytometry")

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

    print("Melis Niyazieva User Setup - Molecular Biology & Biotechnology")
    print()
    print("This script will create the 'melis' user account for tracking")
    print("biotech and life sciences roles.")
    print()

    success = asyncio.run(create_melis_user())
    sys.exit(0 if success else 1)
