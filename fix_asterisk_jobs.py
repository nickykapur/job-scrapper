#!/usr/bin/env python3
"""
Fix jobs with asterisks in the database by extracting data from their URLs.
LinkedIn bot detection causes some job data to be replaced with asterisks.
This script attempts to recover the original data from the job URLs.
"""

import asyncio
import asyncpg
import os
import re
import urllib.parse
from datetime import datetime


def is_asterisk_text(text):
    """Check if text is mostly asterisks"""
    if not text:
        return False
    asterisk_ratio = text.count('*') / len(text)
    return asterisk_ratio > 0.5


def extract_from_url(job_url):
    """Extract title, company, and location from LinkedIn URL"""
    try:
        parsed_url = urllib.parse.urlparse(job_url)
        path_parts = parsed_url.path.split('/')

        title = None
        company = None
        location = None

        # Try to extract from 'at-company' pattern
        for part in path_parts:
            if '-at-' in part and len(part) > 10:
                title_part, company_part = part.split('-at-', 1)
                title = title_part.replace('-', ' ').title()
                company = company_part.replace('-', ' ').title()
                # Clean company name (remove trailing numbers)
                company = re.sub(r'\s+\d{4,}$', '', company).strip()
                break

        # Extract location from domain
        domain = parsed_url.netloc
        domain_location_map = {
            'ie.linkedin.com': 'Ireland',
            'es.linkedin.com': 'Spain',
            'nl.linkedin.com': 'Netherlands',
            'de.linkedin.com': 'Germany',
            'se.linkedin.com': 'Sweden',
            'ch.linkedin.com': 'Switzerland',
            'dk.linkedin.com': 'Denmark',
            'be.linkedin.com': 'Belgium',
            'fr.linkedin.com': 'France',
            'it.linkedin.com': 'Italy'
        }
        if domain in domain_location_map:
            location = domain_location_map[domain]

        return title, company, location
    except Exception as e:
        print(f"Error extracting from URL: {e}")
        return None, None, None


async def fix_asterisk_jobs():
    """Fix jobs with asterisks in the database"""

    # Connect to database
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:JcWFAlWypXvRisiQPVlOlGVFEIRgsgxl@switchback.proxy.rlwy.net:22276/railway')

    print("Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        # Find jobs with asterisks
        print("\nFinding jobs with asterisks...")
        jobs_with_asterisks = await conn.fetch("""
            SELECT id, title, company, location, job_url
            FROM jobs
            WHERE (title LIKE '%*%' OR company LIKE '%*%' OR location LIKE '%*%')
            AND NOT excluded
            ORDER BY scraped_at DESC
        """)

        print(f"Found {len(jobs_with_asterisks)} jobs with asterisks")

        if len(jobs_with_asterisks) == 0:
            print("No jobs to fix!")
            return

        fixed_count = 0
        excluded_count = 0
        failed_count = 0

        for job in jobs_with_asterisks:
            job_id = job['id']
            current_title = job['title']
            current_company = job['company']
            current_location = job['location']
            job_url = job['job_url']

            # Extract from URL
            new_title, new_company, new_location = extract_from_url(job_url)

            # Determine what to update
            update_title = new_title if new_title and is_asterisk_text(current_title) else None
            update_company = new_company if new_company and is_asterisk_text(current_company) else None
            update_location = new_location if new_location and is_asterisk_text(current_location) else None

            # If we couldn't fix the essential fields (title or company), exclude the job
            if (is_asterisk_text(current_title) and not update_title) or (is_asterisk_text(current_company) and not update_company):
                await conn.execute("UPDATE jobs SET excluded = TRUE WHERE id = $1", job_id)
                print(f"❌ Excluded job {job_id}: Could not extract from URL")
                excluded_count += 1
                continue

            # Update the job
            if update_title or update_company or update_location:
                final_title = update_title or current_title
                final_company = update_company or current_company
                final_location = update_location or current_location

                await conn.execute("""
                    UPDATE jobs
                    SET title = $2, company = $3, location = $4, updated_at = $5
                    WHERE id = $1
                """, job_id, final_title, final_company, final_location, datetime.now())

                print(f"✅ Fixed job {job_id}:")
                if update_title:
                    print(f"   Title: {current_title} -> {final_title}")
                if update_company:
                    print(f"   Company: {current_company} -> {final_company}")
                if update_location:
                    print(f"   Location: {current_location} -> {final_location}")

                fixed_count += 1
            else:
                failed_count += 1

        print(f"\n✅ Summary:")
        print(f"   Fixed: {fixed_count} jobs")
        print(f"   Excluded: {excluded_count} jobs (could not fix)")
        print(f"   Failed: {failed_count} jobs (no changes needed)")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(fix_asterisk_jobs())
