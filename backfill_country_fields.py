#!/usr/bin/env python3
"""
Backfill country, job_type, and experience_level for existing jobs
Run this ONCE after deploying database_models.py fix
"""

import asyncio
import asyncpg
import os
from linkedin_job_scraper import LinkedInJobScraper

async def backfill_job_fields():
    """Update existing jobs with missing country, job_type, experience_level"""

    # Get database connection
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL not set")
        return

    conn = await asyncpg.connect(database_url)

    try:
        # Get all jobs
        jobs = await conn.fetch("SELECT id, title, location FROM jobs")

        print(f"[INFO] Found {len(jobs)} jobs to update")

        # Initialize scraper just for utility functions
        scraper = LinkedInJobScraper(headless=True)

        updated = 0
        errors = 0

        for job in jobs:
            try:
                job_id = job['id']
                title = job['title']
                location = job['location']

                # Extract country from location
                country = scraper.get_country_from_location(location)

                # Detect job type
                job_type = scraper.detect_job_type(title)

                # Detect experience level
                experience_level = scraper.detect_experience_level(title)

                # Update job
                await conn.execute("""
                    UPDATE jobs
                    SET country = $2, job_type = $3, experience_level = $4
                    WHERE id = $1
                """, job_id, country, job_type, experience_level)

                updated += 1

                if updated % 50 == 0:
                    print(f"[INFO] Updated {updated}/{len(jobs)} jobs...")

            except Exception as e:
                print(f"[WARNING] Error updating job {job_id}: {e}")
                errors += 1

        print(f"\n[SUCCESS] Backfill complete!")
        print(f"  Updated: {updated} jobs")
        print(f"  Errors: {errors}")

        # Show country distribution
        country_counts = await conn.fetch("""
            SELECT country, COUNT(*) as count
            FROM jobs
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY count DESC
        """)

        print(f"\n[INFO] Jobs per country:")
        for row in country_counts:
            print(f"  {row['country']}: {row['count']} jobs")

        # Show job type distribution
        type_counts = await conn.fetch("""
            SELECT job_type, COUNT(*) as count
            FROM jobs
            WHERE job_type IS NOT NULL
            GROUP BY job_type
            ORDER BY count DESC
        """)

        print(f"\n[INFO] Jobs per type:")
        for row in type_counts:
            print(f"  {row['job_type']}: {row['count']} jobs")

    finally:
        scraper.close()
        await conn.close()


if __name__ == "__main__":
    asyncio.run(backfill_job_fields())
