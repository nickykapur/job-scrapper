#!/usr/bin/env python3
"""
Single Country Job Scraper - For parallel GitHub Actions execution
Scrapes one country at a time for faster execution
"""

import argparse
import os
import sys
from daily_multi_country_update import (
    LinkedInJobScraper,
    load_existing_jobs_from_railway,
    upload_jobs_to_railway,
    enforce_country_job_limit
)

def scrape_single_country(location, country_name, railway_url):
    """Scrape jobs for a single country"""

    print(f"\n{'='*80}")
    print(f"🌍 Scraping {country_name} - {location}")
    print(f"{'='*80}\n")

    # Load existing jobs from Railway
    existing_jobs = load_existing_jobs_from_railway(railway_url)

    # Search terms - Multi-user configuration
    software_search_terms = [
        "Software Engineer",
        "Python Developer",
        "React Developer",
        "Full Stack Developer",
        "Backend Developer",
        "Frontend Developer",
        "JavaScript Developer",
        "Node.js Developer",
        "Junior Software Engineer"
    ]

    hr_search_terms = [
        "HR Officer",
        "Talent Acquisition Coordinator",
        "Talent Acquisition Specialist",
        "HR Coordinator",
        "HR Generalist",
        "HR Specialist",
        "Junior Recruiter",
        "Recruiter",
        "Recruitment Coordinator",
        "People Operations",
        "People Partner",
        "HR Assistant",
        "HR Manager",
        "Talent Manager",
        "HR Business Partner",
        "Talent Sourcer"
    ]

    search_terms = software_search_terms + hr_search_terms

    # Initialize scraper
    scraper = LinkedInJobScraper(headless=True)
    scraper.existing_jobs = existing_jobs

    all_new_jobs = {}
    successful_searches = 0

    try:
        print(f"\n[LOCATION] Searching in {location}")

        for term in search_terms:
            print(f"   [SEARCH] {term}")

            try:
                results = scraper.search_jobs(
                    keywords=term,
                    location=location,
                    date_filter="24h"
                )

                if results:
                    for job_id, job_data in results.items():
                        # Add country info
                        job_data["country"] = country_name
                        job_data["search_location"] = location

                        if job_id not in all_new_jobs:
                            all_new_jobs[job_id] = job_data

                    print(f"      ✓ Found {len(results)} jobs")
                    successful_searches += 1
                else:
                    print(f"      ⊗ No new jobs found")

            except Exception as e:
                print(f"      ✗ Search failed: {e}")
                continue

    finally:
        scraper.close()

    print(f"\n[SUMMARY] {country_name}:")
    print(f"   • Searches: {successful_searches}/{len(search_terms)}")
    print(f"   • New jobs found: {len(all_new_jobs)}")

    # Upload to Railway
    if all_new_jobs:
        print(f"\n[UPLOAD] Uploading {len(all_new_jobs)} jobs to Railway...")
        success = upload_jobs_to_railway(railway_url, all_new_jobs)

        if success:
            print(f"   ✅ Upload successful!")
        else:
            print(f"   ❌ Upload failed!")
            return False
    else:
        print(f"\n[SKIP] No new jobs to upload")

    print(f"\n✅ {country_name} scraping complete!")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape jobs for a single country')
    parser.add_argument('--location', required=True, help='Location string (e.g., "Dublin, County Dublin, Ireland")')
    parser.add_argument('--country', required=True, help='Country name (e.g., "Ireland")')
    parser.add_argument('--railway-url', help='Railway URL (default from env)')

    args = parser.parse_args()

    railway_url = args.railway_url or os.environ.get('RAILWAY_URL')

    if not railway_url:
        print("❌ Error: RAILWAY_URL not provided")
        sys.exit(1)

    success = scrape_single_country(args.location, args.country, railway_url)
    sys.exit(0 if success else 1)
