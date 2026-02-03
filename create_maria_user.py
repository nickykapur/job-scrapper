#!/usr/bin/env python3
"""
Create Maria User Account - Mechanical & Manufacturing Engineering Professional
Sets up account for Maria Huidobro Segura - Dual Master's in Mechanical and Aerospace Engineering in Chicago
"""

import asyncio
from user_database import UserDatabase


async def create_maria_user():
    """Create Maria user account for tracking engineering and manufacturing roles"""

    print("=" * 60)
    print("CREATE MARIA USER - MECHANICAL & MANUFACTURING ENGINEERING")
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

        print("\n[STEP 1] Creating Maria user account...")
        print("-" * 60)

        username = "maria"
        email = "huidobrosegura.maria@gmail.com"
        password = "pass123"
        full_name = "Maria Huidobro Segura"

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
        # STEP 2: Set Engineering preferences
        # ================================================================

        print("\n[STEP 2] Setting Engineering & Manufacturing preferences...")
        print("-" * 60)

        # Maria's preferences based on her CV
        maria_preferences = {
            # Job types - Engineering & Manufacturing
            "job_types": ["engineering", "manufacturing", "mechanical"],

            # Keywords from Maria's skills and experience
            "keywords": [
                # Mechanical Engineering
                "Mechanical Engineer",
                "Junior Mechanical Engineer",
                "Mechanical Design Engineer",
                "Mechanical Engineer Entry Level",
                "Design Engineer",
                "CAD Engineer",
                "Product Design Engineer",

                # Manufacturing Engineering
                "Manufacturing Engineer",
                "Junior Manufacturing Engineer",
                "Production Engineer",
                "Process Engineer",
                "Manufacturing Process Engineer",
                "Manufacturing Systems Engineer",

                # Industrial Engineering
                "Industrial Engineer",
                "Junior Industrial Engineer",
                "Operations Engineer",
                "Continuous Improvement Engineer",
                "Lean Engineer",
                "Six Sigma",

                # Aerospace Engineering
                "Aerospace Engineer",
                "Junior Aerospace Engineer",
                "Propulsion Engineer",
                "Flight Systems Engineer",

                # Quality & Testing
                "Quality Engineer",
                "Test Engineer",
                "Reliability Engineer",
                "Quality Assurance Engineer",

                # Data & Simulation
                "Simulation Engineer",
                "FlexSim",
                "MATLAB Engineer",
                "Data Analyst Manufacturing",
                "Process Optimization",
                "ANSYS",

                # R&D
                "R&D Engineer",
                "Research Engineer",
                "Development Engineer",

                # Entry level
                "Entry Level Engineer",
                "Associate Engineer",
                "Engineering Trainee",
                "Graduate Engineer",
                "Junior Engineer",

                # Specific tools/skills
                "AutoCAD",
                "SolidWorks",
                "CNC",
                "Robotics Engineer",
                "Automation Engineer"
            ],

            # Excluded keywords (avoid these - too senior or unrelated)
            "excluded_keywords": [
                "Director",
                "VP",
                "Head of",
                "Chief",
                "Principal Engineer",
                "10+ years",
                "15+ years",
                "Senior Director",
                "Staff Engineer",
                "Lead Engineer"
            ],

            # Experience levels - Entry to Mid level (Master's student)
            "experience_levels": ["entry", "junior", "mid"],
            "exclude_senior": True,

            # Location - United States (Chicago based)
            "preferred_countries": ["United States"],
            "preferred_cities": ["Chicago", "Detroit", "Indianapolis", "Milwaukee", "Cleveland", "St. Louis"],

            # Company preferences - Manufacturing & Aerospace companies
            "excluded_companies": [],
            "preferred_companies": [
                "Boeing",
                "Lockheed Martin",
                "Caterpillar",
                "John Deere",
                "General Electric",
                "Honeywell",
                "3M",
                "Abbott",
                "Northrop Grumman",
                "Raytheon"
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
            preferences=maria_preferences
        )

        if not success:
            print("Failed to set preferences, but user account was created")
            return False

        print("Preferences set successfully!")
        print("\nPreference Summary:")
        print(f"   Job Types: Engineering, Manufacturing, Mechanical")
        print(f"   Experience: Entry to Mid-Level")
        print(f"   Location: United States (Chicago area)")
        print(f"   Keywords: {len(maria_preferences['keywords'])} engineering terms")

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
        print("MARIA USER SETUP COMPLETE!")
        print("=" * 60)

        print("\nAccount Summary:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print(f"   Full Name: {full_name}")
        print(f"   User ID: {user['id']}")

        print("\nJob Preferences:")
        print("   Job Types: Engineering, Manufacturing, Mechanical")
        print("   Experience: Entry to Mid-Level")
        print("   Location: United States (Chicago, Detroit, Indianapolis, etc.)")
        print("   Skills Focus: FlexSim, AutoCAD, MATLAB, ANSYS, Manufacturing Systems")

        print("\nMaria's Background:")
        print("   Dual Master's - Mechanical & Aerospace Engineering")
        print("   - Illinois Institute of Technology, Chicago")
        print("   - Universidad Politecnica de Madrid")
        print("   BSc Industrial Engineering - UPM Madrid")
        print("   Experience: Repsol Research, UPM Laser Center")
        print("   Skills: FlexSim, AutoCAD, MATLAB, Simulink, C++, ANSYS, RStudio")

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

    print("Maria Huidobro Segura User Setup - Mechanical & Manufacturing Engineering")
    print()
    print("This script will create the 'maria' user account for tracking")
    print("engineering and manufacturing roles in the United States.")
    print()

    success = asyncio.run(create_maria_user())
    sys.exit(0 if success else 1)
