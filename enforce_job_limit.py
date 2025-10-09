#!/usr/bin/env python3
"""
Script to enforce the 300 jobs per country limit on the Railway database
Removes oldest jobs from each country that exceeds the limit
"""

import requests
import sys

RAILWAY_URL = "https://web-production-110bb.up.railway.app"
MAX_JOBS_PER_COUNTRY = 300

def enforce_job_limit():
    """Enforce the 300 jobs per country limit"""

    print(f"✂️  Enforce Job Limit Script")
    print("=" * 50)
    print(f"🌐 Railway URL: {RAILWAY_URL}")
    print(f"🔢 Max jobs per country: {MAX_JOBS_PER_COUNTRY}")
    print()

    try:
        # First, check current job counts
        print("🔍 Checking current job counts...")
        response = requests.get(f"{RAILWAY_URL}/api/jobs", timeout=30)
        response.raise_for_status()

        jobs_data = response.json()

        # Group jobs by country
        jobs_by_country = {}
        for job_id, job_data in jobs_data.items():
            if job_id.startswith("_"):
                continue

            country = job_data.get("country", "Unknown")
            if country not in jobs_by_country:
                jobs_by_country[country] = 0
            jobs_by_country[country] += 1

        print()
        print("📊 Current job counts by country:")
        total_jobs = sum(jobs_by_country.values())
        countries_over_limit = []

        for country, count in sorted(jobs_by_country.items(), key=lambda x: x[1], reverse=True):
            status = f"⚠️  OVER LIMIT (+{count - MAX_JOBS_PER_COUNTRY})" if count > MAX_JOBS_PER_COUNTRY else "✅"
            print(f"   {country}: {count} jobs {status}")
            if count > MAX_JOBS_PER_COUNTRY:
                countries_over_limit.append(country)

        print(f"\n📊 Total jobs: {total_jobs}")
        print(f"📊 Countries over limit: {len(countries_over_limit)}")

        if len(countries_over_limit) == 0:
            print("\n✅ All countries are within the limit!")
            return True

        # Ask for confirmation
        print()
        response_input = input(f"⚠️  Enforce the {MAX_JOBS_PER_COUNTRY} job limit? This will delete old jobs. (yes/no): ")
        if response_input.lower() not in ['yes', 'y']:
            print("❌ Operation cancelled")
            return False

        # Enforce the limit via API
        print()
        print("✂️  Enforcing job limit on Railway database...")
        enforce_response = requests.post(
            f"{RAILWAY_URL}/api/jobs/enforce-country-limit",
            params={"max_jobs": MAX_JOBS_PER_COUNTRY},
            timeout=60
        )
        enforce_response.raise_for_status()

        result = enforce_response.json()

        print()
        print("✅ Successfully enforced job limit!")
        print(f"📊 Jobs deleted: {result.get('jobs_deleted', 0)}")
        print(f"📊 Total jobs remaining: {result.get('total_jobs_remaining', 0)}")
        print(f"📊 Countries processed: {result.get('countries_processed', 0)}")

        print()
        print("🎉 Database cleaned up successfully!")
        print("📝 The changes are live on Railway immediately.")
        print("   Refresh your frontend to see the updated job counts.")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = enforce_job_limit()
    sys.exit(0 if success else 1)
