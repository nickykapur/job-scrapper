#!/usr/bin/env python3
"""
Remove jobs from disabled countries: Belgium, Sweden, Germany, Denmark, Netherlands
"""

import asyncio
import asyncpg
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

# Countries to remove
DISABLED_COUNTRIES = ['Belgium', 'Sweden', 'Germany', 'Denmark', 'Netherlands']

async def remove_disabled_countries():
    """Remove jobs from disabled countries"""
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set")
        return

    print("🔧 Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Get count of jobs from disabled countries
        for country in DISABLED_COUNTRIES:
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM jobs WHERE country = $1
            """, country)
            print(f"📊 Found {count} jobs in {country}")

        # Total count
        total_count = await conn.fetchval("""
            SELECT COUNT(*) FROM jobs WHERE country = ANY($1::text[])
        """, DISABLED_COUNTRIES)

        print(f"\n📊 Total jobs to remove: {total_count}")

        if total_count == 0:
            print("✅ No jobs to remove!")
            return

        # Confirm deletion
        print(f"\n⚠️  About to delete {total_count} jobs from disabled countries...")

        # Delete jobs from disabled countries
        # Note: This will cascade and delete related user_job_interactions
        deleted = await conn.execute("""
            DELETE FROM jobs WHERE country = ANY($1::text[])
        """, DISABLED_COUNTRIES)

        print(f"✅ Successfully deleted jobs from disabled countries!")
        print(f"   Removed: {total_count} jobs")

        # Show remaining jobs by country
        print("\n📊 Remaining jobs by country:")
        remaining = await conn.fetch("""
            SELECT country, COUNT(*) as count
            FROM jobs
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY count DESC
        """)

        for row in remaining:
            print(f"   {row['country']}: {row['count']} jobs")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(remove_disabled_countries())
