#!/usr/bin/env python3
"""
Single Country Job Scraper - For parallel GitHub Actions execution
Scrapes one country at a time for faster execution
"""

import argparse
import os
import sys
import requests
from linkedin_job_scraper import LinkedInJobScraper

def load_existing_jobs_from_railway(railway_url):
    """Load existing jobs from Railway database via API"""
    try:
        if not railway_url.startswith('http'):
            railway_url = f'https://{railway_url}'

        api_url = f"{railway_url}/api/jobs"
        response = requests.get(api_url, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"[WARN] Could not load existing jobs: {response.status_code}")
            return {}
    except Exception as e:
        print(f"[WARN] Error loading existing jobs: {e}")
        return {}

def upload_jobs_to_railway(railway_url, jobs_data):
    """Upload jobs to Railway database and return actual new/updated counts"""
    try:
        if not railway_url.startswith('http'):
            railway_url = f'https://{railway_url}'

        sync_url = f"{railway_url}/sync_jobs"

        print(f"   [API] Uploading to: {sync_url}")
        response = requests.post(
            sync_url,
            json={"jobs_data": jobs_data},
            timeout=60,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            new_jobs = result.get('new_jobs', 0)
            new_software = result.get('new_software', 0)
            new_hr = result.get('new_hr', 0)
            new_cybersecurity = result.get('new_cybersecurity', 0)
            updated_jobs = result.get('updated_jobs', 0)
            print(f"   [OK] New: {new_jobs} ({new_software} software, {new_hr} HR, {new_cybersecurity} cybersecurity), Updated: {updated_jobs}")
            return {
                'success': True,
                'new_jobs': new_jobs,
                'new_software': new_software,
                'new_hr': new_hr,
                'new_cybersecurity': new_cybersecurity,
                'updated_jobs': updated_jobs
            }
        else:
            print(f"   [ERROR] Upload failed: {response.status_code}")
            return {'success': False, 'new_jobs': 0, 'new_software': 0, 'new_hr': 0, 'new_cybersecurity': 0, 'updated_jobs': 0}
    except Exception as e:
        print(f"   [ERROR] Upload error: {e}")
        return {'success': False, 'new_jobs': 0, 'new_software': 0, 'new_hr': 0, 'new_cybersecurity': 0, 'updated_jobs': 0}

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

    cybersecurity_search_terms = [
        # English terms
        "SOC Analyst",
        "Cybersecurity Analyst",
        "Security Analyst",
        "Information Security Analyst",
        "Junior SOC Analyst",
        "Security Operations",
        "Incident Response Analyst",
        # Spanish terms (for Panama and Spain)
        "Analista SOC",
        "Analista de Ciberseguridad",
        "Analista de Seguridad",
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

    search_terms = software_search_terms + hr_search_terms + cybersecurity_search_terms

    # Initialize scraper
    scraper = LinkedInJobScraper(headless=True)
    scraper.existing_jobs = existing_jobs

    all_new_jobs = {}
    software_jobs = {}
    hr_jobs = {}
    cybersecurity_jobs = {}
    successful_searches = 0

    try:
        print(f"\n[LOCATION] Searching in {location}")

        for term in search_terms:
            print(f"   [SEARCH] {term}")

            # Determine if this is a software, HR, or cybersecurity search
            is_software = term in software_search_terms
            is_cybersecurity = term in cybersecurity_search_terms

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

                            # Track software vs HR vs cybersecurity jobs
                            if is_software:
                                software_jobs[job_id] = job_data
                            elif is_cybersecurity:
                                cybersecurity_jobs[job_id] = job_data
                            else:
                                hr_jobs[job_id] = job_data

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
    print(f"   • New jobs found: {len(all_new_jobs)} (Software: {len(software_jobs)}, HR: {len(hr_jobs)}, Cybersecurity: {len(cybersecurity_jobs)})")

    # Upload to Railway and get actual new job counts
    actual_new_software = 0
    actual_new_hr = 0
    actual_new_cybersecurity = 0
    actual_new_total = 0

    if all_new_jobs:
        print(f"\n[UPLOAD] Uploading {len(all_new_jobs)} jobs to Railway...")
        upload_result = upload_jobs_to_railway(railway_url, all_new_jobs)

        if upload_result['success']:
            actual_new_total = upload_result['new_jobs']
            actual_new_software = upload_result['new_software']
            actual_new_hr = upload_result['new_hr']
            actual_new_cybersecurity = upload_result['new_cybersecurity']
            print(f"   ✅ Upload successful!")
            print(f"   📊 Actually added to DB: {actual_new_total} new ({actual_new_software} software, {actual_new_hr} HR, {actual_new_cybersecurity} cybersecurity)")
        else:
            print(f"   ❌ Upload failed!")
            return False
    else:
        print(f"\n[SKIP] No new jobs to upload")

    # Output for GitHub Actions summary
    print(f"\n::notice title={country_name} Complete::{actual_new_total} new jobs added ({actual_new_software} software, {actual_new_hr} HR, {actual_new_cybersecurity} cybersecurity)")

    # Set output for GitHub Actions - use ACTUAL new counts, not scraped counts
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
            f.write(f"jobs_found={actual_new_total}\n")
            f.write(f"software_jobs={actual_new_software}\n")
            f.write(f"hr_jobs={actual_new_hr}\n")
            f.write(f"cybersecurity_jobs={actual_new_cybersecurity}\n")
            f.write(f"country={country_name}\n")

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
