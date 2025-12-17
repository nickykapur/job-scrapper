#!/usr/bin/env python3
"""
Fix URL-encoded characters in job titles, companies, and locations
Converts things like %C3%B3 to ó, %25 to %, etc.
"""

import asyncio
import asyncpg
import os
from urllib.parse import unquote

DATABASE_URL = os.environ.get('DATABASE_URL')

async def fix_url_encoding():
    """Fix URL-encoded characters in the database"""
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set")
        return

    print("🔧 Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Get all jobs with potential encoding issues
        jobs = await conn.fetch("""
            SELECT id, title, company, location
            FROM jobs
            WHERE title LIKE '%25%'
               OR title LIKE '%C3%'
               OR title LIKE '%E2%'
               OR company LIKE '%25%'
               OR company LIKE '%C3%'
               OR company LIKE '%E2%'
               OR location LIKE '%25%'
               OR location LIKE '%C3%'
               OR location LIKE '%E2%'
        """)

        print(f"📊 Found {len(jobs)} jobs with potential encoding issues")

        if len(jobs) == 0:
            print("✅ No jobs need fixing!")
            return

        # Fix each job
        fixed_count = 0
        for job in jobs:
            job_id = job['id']
            old_title = job['title']
            old_company = job['company']
            old_location = job['location']

            # Decode URL-encoded characters
            new_title = unquote(old_title) if old_title else old_title
            new_company = unquote(old_company) if old_company else old_company
            new_location = unquote(old_location) if old_location else old_location

            # Only update if something changed
            if new_title != old_title or new_company != old_company or new_location != old_location:
                await conn.execute("""
                    UPDATE jobs
                    SET title = $1, company = $2, location = $3, updated_at = CURRENT_TIMESTAMP
                    WHERE id = $4
                """, new_title, new_company, new_location, job_id)

                fixed_count += 1

                if old_title != new_title:
                    print(f"✅ Fixed title: '{old_title[:50]}...' -> '{new_title[:50]}...'")
                if old_company != new_company:
                    print(f"✅ Fixed company: '{old_company}' -> '{new_company}'")
                if old_location != new_location:
                    print(f"✅ Fixed location: '{old_location}' -> '{new_location}'")

        print(f"\n🎉 Successfully fixed {fixed_count} jobs!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_url_encoding())
