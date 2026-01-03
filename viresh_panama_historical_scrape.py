#!/usr/bin/env python3
"""
Historical Job Scraper for Viresh Rajani in Panama (Past 2 weeks)
Scrapes both Spanish and English job postings
"""

import os
import requests
from linkedin_job_scraper import LinkedInJobScraper

# Configuration
LOCATION = "Panama City, Panama"
COUNTRY_NAME = "Panama"
RAILWAY_URL = "https://web-production-110bb.up.railway.app"
DATE_FILTER = "30d"  # Get past month to ensure we cover 2 weeks

# Job search terms based on Viresh's CV (Both Spanish and English)
SEARCH_TERMS = [
    # Sales & Key Account (English)
    "key account manager",
    "sales coordinator",
    "commercial coordinator",
    "account executive",
    "business development",

    # Sales & Key Account (Spanish)
    "gerente de cuentas clave",
    "coordinador de ventas",
    "coordinador comercial",
    "ejecutivo de cuentas",
    "desarrollo de negocios",

    # Customer Service (English)
    "customer service coordinator",
    "customer service manager",
    "client relations",

    # Customer Service (Spanish)
    "coordinador servicio al cliente",
    "gerente servicio al cliente",
    "relaciones con clientes",

    # HR (English)
    "human resources coordinator",
    "HR manager",
    "talent acquisition",
    "recruitment specialist",

    # HR (Spanish)
    "coordinador recursos humanos",
    "gerente RRHH",
    "adquisición de talento",
    "reclutamiento",

    # Business Intelligence & Analytics (English)
    "business intelligence analyst",
    "commercial analyst",
    "data analyst",
    "business analyst",

    # Business Intelligence & Analytics (Spanish)
    "analista de inteligencia de negocios",
    "analista comercial",
    "analista de datos",
    "analista de negocios",

    # Operations & Supply Chain (English)
    "operations coordinator",
    "supply chain coordinator",
    "logistics coordinator",
    "industrial engineer",

    # Operations & Supply Chain (Spanish)
    "coordinador de operaciones",
    "coordinador cadena de suministro",
    "coordinador logística",
    "ingeniero industrial",
]

def load_existing_jobs():
    """Load existing jobs from Railway"""
    try:
        api_url = f"{RAILWAY_URL}/api/jobs"
        response = requests.get(api_url, timeout=30)

        if response.status_code == 200:
            print(f"[OK] Loaded existing jobs from Railway")
            return response.json()
        else:
            print(f"[WARN] Could not load existing jobs: {response.status_code}")
            return {}
    except Exception as e:
        print(f"[WARN] Error loading existing jobs: {e}")
        return {}

def upload_jobs(jobs_data):
    """Upload jobs to Railway"""
    try:
        sync_url = f"{RAILWAY_URL}/sync_jobs"

        print(f"[API] Uploading {len(jobs_data)} jobs to Railway...")
        response = requests.post(
            sync_url,
            json={"jobs_data": jobs_data},
            timeout=120,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            new_jobs = result.get('new_jobs', 0)
            updated_jobs = result.get('updated_jobs', 0)
            print(f"[OK] Upload complete: {new_jobs} new, {updated_jobs} updated")
            return True
        else:
            print(f"[ERROR] Upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Upload error: {e}")
        return False

def main():
    print(f"""
{'='*70}
Historical Job Scraper for Viresh Rajani - Panama
{'='*70}
Location: {LOCATION}
Time Range: Past 30 days (covering last 2 weeks)
Languages: Spanish & English
Job Types: Sales, HR, Finance, Customer Service, BI, Operations
{'='*70}
    """)

    # Load existing jobs
    existing_jobs = load_existing_jobs()

    # Initialize scraper
    scraper = LinkedInJobScraper(headless=True)
    scraper.existing_jobs = existing_jobs

    all_jobs = {}
    total_found = 0

    # Search for each term
    for idx, term in enumerate(SEARCH_TERMS, 1):
        print(f"\n[{idx}/{len(SEARCH_TERMS)}] Searching: '{term}'")

        try:
            # Search for jobs
            results = scraper.search_jobs(
                keywords=term,
                location=LOCATION,
                date_filter=DATE_FILTER,  # Past 30 days
                easy_apply_filter=None    # Get all jobs, not just Easy Apply
            )

            if results:
                print(f"   Found: {len(results)} jobs")
                total_found += len(results)

                # Add country to each job
                for job_id, job_data in results.items():
                    job_data['country'] = COUNTRY_NAME
                    all_jobs[job_id] = job_data
            else:
                print(f"   Found: 0 jobs")

        except Exception as e:
            print(f"   [ERROR] Search failed: {e}")
            continue

    # Close scraper
    scraper.close()

    # Summary
    print(f"\n{'='*70}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*70}")
    print(f"Total searches: {len(SEARCH_TERMS)}")
    print(f"Jobs found: {total_found}")
    print(f"Unique jobs: {len(all_jobs)}")
    print(f"{'='*70}\n")

    if all_jobs:
        # Upload to Railway
        if upload_jobs(all_jobs):
            print(f"\n[SUCCESS] Historical scrape completed for Viresh!")
            print(f"[INFO] {len(all_jobs)} jobs are now available in Panama")
            print(f"[INFO] Daily scraper will continue to update automatically 7x/day")
        else:
            print(f"\n[ERROR] Failed to upload jobs to Railway")
    else:
        print(f"\n[WARN] No jobs found. This might indicate:")
        print(f"  - No matching jobs in Panama for the specified criteria")
        print(f"  - LinkedIn rate limiting (try again later)")
        print(f"  - Connection issues")

if __name__ == "__main__":
    main()
