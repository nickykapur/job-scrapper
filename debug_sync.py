#!/usr/bin/env python3
"""
Debug sync to find the exact type issue
"""

import json
import asyncio
import asyncpg
import os
from datetime import datetime

async def debug_sync():
    """Debug the sync issue with a single job"""
    # Load one job from database
    with open('jobs_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get first job
    first_job_id = None
    first_job = None
    for k, v in data.items():
        if not k.startswith('_'):
            first_job_id = k
            first_job = v
            break

    if not first_job:
        print("No jobs found")
        return

    print("🔍 Debug Job Data:")
    print(f"ID: {first_job_id}")
    for key, value in first_job.items():
        print(f"  {key}: {repr(value)} (type: {type(value).__name__})")

    # Try to connect to Railway database
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/jobsdb')

    try:
        conn = await asyncpg.connect(db_url)
        print("\n✅ Connected to database")

        # Test the exact insert with debug data
        job_id = first_job_id
        job_data = first_job

        # Clean data exactly like in the main code
        applied_bool = bool(job_data.get('applied', False))
        is_new_bool = bool(job_data.get('is_new', True))

        title = str(job_data['title'])[:500] if job_data.get('title') else 'No title'
        company = str(job_data['company'])[:300] if job_data.get('company') else 'Unknown'
        location = str(job_data['location'])[:300] if job_data.get('location') else ''
        posted_date = str(job_data['posted_date'])[:100] if job_data.get('posted_date') else ''
        category = str(job_data.get('category', ''))[:50] if job_data.get('category') else None

        print(f"\n🧪 Testing INSERT with cleaned data:")
        print(f"  1. job_id: {repr(job_id)} ({type(job_id).__name__})")
        print(f"  2. title: {repr(title)} ({type(title).__name__})")
        print(f"  3. company: {repr(company)} ({type(company).__name__})")
        print(f"  4. location: {repr(location)} ({type(location).__name__})")
        print(f"  5. posted_date: {repr(posted_date)} ({type(posted_date).__name__})")
        print(f"  6. job_url: {repr(job_data['job_url'])} ({type(job_data['job_url']).__name__})")
        print(f"  7. scraped_at: None (will be NULL)")
        print(f"  8. applied: {repr(applied_bool)} ({type(applied_bool).__name__})")
        print(f"  9. is_new: {repr(is_new_bool)} ({type(is_new_bool).__name__})")
        print(f" 10. category: {repr(category)} ({type(category).__name__ if category else 'NoneType'})")
        print(f" 11. first_seen: {datetime.now()} ({type(datetime.now()).__name__})")

        # Try the insert
        await conn.execute("""
            INSERT INTO jobs (id, title, company, location, posted_date, job_url,
                            scraped_at, applied, is_new, category, first_seen)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """, job_id, title, company, location, posted_date, job_data['job_url'], None,
            applied_bool, is_new_bool, category, datetime.now())

        print("✅ INSERT successful!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_sync())