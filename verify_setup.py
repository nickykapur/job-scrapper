#!/usr/bin/env python3
"""
Verification script to check if Easy Apply and 300 jobs limit are working
Run this after deploying to verify everything is set up correctly
"""

import os
import sys
import json
import asyncio
from database_models import JobDatabase

async def verify_database_schema():
    """Verify database has easy_apply column"""
    print("🔍 Checking database schema...")

    db = JobDatabase()

    if not db.use_postgres:
        print("❌ Not using PostgreSQL - using JSON fallback")
        print("   Run with DATABASE_URL environment variable to check PostgreSQL")
        return False

    conn = await db.get_connection()
    if not conn:
        print("❌ Could not connect to database")
        return False

    try:
        # Check if easy_apply column exists
        result = await conn.fetchrow("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'jobs' AND column_name = 'easy_apply'
        """)

        if result:
            print(f"✅ easy_apply column exists: {result['data_type']} DEFAULT {result['column_default']}")
            return True
        else:
            print("❌ easy_apply column NOT FOUND")
            print("   Run: psql $DATABASE_URL -f add_easy_apply_column.sql")
            return False

    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        return False
    finally:
        await conn.close()

async def verify_jobs_per_country():
    """Verify no country has more than 300 jobs"""
    print("\n🔍 Checking jobs per country...")

    db = JobDatabase()

    if not db.use_postgres:
        print("⚠️  Using JSON - checking local file")
        if os.path.exists('jobs_database.json'):
            with open('jobs_database.json', 'r') as f:
                jobs = json.load(f)

            country_counts = {}
            for job_id, job_data in jobs.items():
                if job_id.startswith('_'):
                    continue
                country = job_data.get('country', 'Unknown')
                country_counts[country] = country_counts.get(country, 0) + 1

            print("\nJob counts by country:")
            over_limit = []
            for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
                status = "✅" if count <= 300 else "❌"
                print(f"  {status} {country}: {count} jobs")
                if count > 300:
                    over_limit.append((country, count))

            if over_limit:
                print(f"\n❌ {len(over_limit)} countries over 300 job limit:")
                for country, count in over_limit:
                    print(f"   {country}: {count} jobs (remove {count - 300})")
                return False
            else:
                print("\n✅ All countries within 300 job limit")
                return True
        else:
            print("❌ jobs_database.json not found")
            return False

    conn = await db.get_connection()
    if not conn:
        print("❌ Could not connect to database")
        return False

    try:
        # Check jobs per country
        result = await conn.fetch("""
            SELECT country, COUNT(*) as job_count
            FROM jobs
            GROUP BY country
            ORDER BY job_count DESC
        """)

        print("\nJob counts by country:")
        over_limit = []
        for row in result:
            country = row['country'] or 'Unknown'
            count = row['job_count']
            status = "✅" if count <= 300 else "❌"
            print(f"  {status} {country}: {count} jobs")
            if count > 300:
                over_limit.append((country, count))

        if over_limit:
            print(f"\n❌ {len(over_limit)} countries over 300 job limit:")
            for country, count in over_limit:
                print(f"   {country}: {count} jobs (remove {count - 300})")
            print("\n   Run: psql $DATABASE_URL -f cleanup_old_jobs.sql")
            return False
        else:
            print("\n✅ All countries within 300 job limit")
            return True

    except Exception as e:
        print(f"❌ Error checking job counts: {e}")
        return False
    finally:
        await conn.close()

async def verify_easy_apply_data():
    """Verify jobs have easy_apply data"""
    print("\n🔍 Checking Easy Apply data...")

    db = JobDatabase()

    if not db.use_postgres:
        print("⚠️  Using JSON - checking local file")
        if os.path.exists('jobs_database.json'):
            with open('jobs_database.json', 'r') as f:
                jobs = json.load(f)

            total_jobs = 0
            easy_apply_count = 0
            has_field = 0

            for job_id, job_data in jobs.items():
                if job_id.startswith('_'):
                    continue
                total_jobs += 1
                if 'easy_apply' in job_data:
                    has_field += 1
                    if job_data['easy_apply']:
                        easy_apply_count += 1

            print(f"\n  Total jobs: {total_jobs}")
            print(f"  Jobs with easy_apply field: {has_field}")
            print(f"  Jobs with Easy Apply: {easy_apply_count}")

            if has_field == 0:
                print("\n❌ No jobs have easy_apply field")
                print("   Re-run scraper to populate Easy Apply data")
                return False
            elif easy_apply_count == 0:
                print("\n⚠️  Jobs have easy_apply field but all are false")
                print("   This is normal if no jobs have LinkedIn Easy Apply")
                print("   OR scraper detection needs improvement")
                return True
            else:
                percentage = (easy_apply_count / total_jobs) * 100
                print(f"\n✅ {percentage:.1f}% of jobs have Easy Apply")
                return True
        else:
            print("❌ jobs_database.json not found")
            return False

    conn = await db.get_connection()
    if not conn:
        print("❌ Could not connect to database")
        return False

    try:
        # Check Easy Apply statistics
        result = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_jobs,
                COUNT(*) FILTER (WHERE easy_apply = true) as easy_apply_count,
                ROUND(100.0 * COUNT(*) FILTER (WHERE easy_apply = true) / COUNT(*), 1) as percentage
            FROM jobs
        """)

        print(f"\n  Total jobs: {result['total_jobs']}")
        print(f"  Jobs with Easy Apply: {result['easy_apply_count']}")
        print(f"  Percentage: {result['percentage']}%")

        # Check per country
        country_stats = await conn.fetch("""
            SELECT
                country,
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE easy_apply = true) as easy_apply
            FROM jobs
            GROUP BY country
            ORDER BY total DESC
        """)

        print("\n  Easy Apply by country:")
        for row in country_stats:
            country = row['country'] or 'Unknown'
            total = row['total']
            easy = row['easy_apply']
            pct = (easy / total * 100) if total > 0 else 0
            print(f"    {country}: {easy}/{total} ({pct:.1f}%)")

        if result['easy_apply_count'] == 0:
            print("\n⚠️  No jobs have Easy Apply enabled")
            print("   This is normal if no jobs have LinkedIn Easy Apply")
            print("   OR scraper detection needs improvement")
            return True
        else:
            print(f"\n✅ Easy Apply data present ({result['percentage']}% of jobs)")
            return True

    except Exception as e:
        print(f"❌ Error checking Easy Apply data: {e}")
        return False
    finally:
        await conn.close()

async def main():
    print("=" * 60)
    print("🔧 Job Scraper Setup Verification")
    print("=" * 60)

    results = []

    # Test 1: Database Schema
    schema_ok = await verify_database_schema()
    results.append(("Database Schema (easy_apply column)", schema_ok))

    # Test 2: Jobs per country limit
    limit_ok = await verify_jobs_per_country()
    results.append(("300 jobs per country limit", limit_ok))

    # Test 3: Easy Apply data
    easy_apply_ok = await verify_easy_apply_data()
    results.append(("Easy Apply data present", easy_apply_ok))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 All checks passed! Setup is complete.")
        print("\n💡 Next steps:")
        print("   1. Rebuild frontend: cd job-manager-ui && npm run build")
        print("   2. Wait for next GitHub Action run to populate Easy Apply data")
        print("   3. Check UI to see ⚡ Easy Apply badges")
        return 0
    else:
        print("\n⚠️  Some checks failed. Review the errors above.")
        print("\n💡 Quick fixes:")
        print("   - Add easy_apply column: psql $DATABASE_URL -f add_easy_apply_column.sql")
        print("   - Clean up old jobs: psql $DATABASE_URL -f cleanup_old_jobs.sql")
        print("   - Re-run scraper: python daily_multi_country_update.py")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
