#!/usr/bin/env python3
"""
Historical Job Scraper for Divya Rajani in Panama (Past 2 weeks)
Scrapes both Spanish and English job postings
Based on: Industrial Engineer + MBA, Commercial Strategy & Analytics, 8+ years
"""

import os
import requests
from linkedin_job_scraper import LinkedInJobScraper

# Configuration
LOCATION = "Panama City, Panama"
COUNTRY_NAME = "Panama"
RAILWAY_URL = "https://web-production-110bb.up.railway.app"
DATE_FILTER = "30d"  # Get past month to ensure we cover 2 weeks

# Job search terms based on Divya's CV (Both Spanish and English)
SEARCH_TERMS = [
    # Product Management (English)
    "product owner",
    "product manager",
    "product coordinator",
    "corporate product coordinator",

    # Product Management (Spanish)
    "product owner",
    "gerente de producto",
    "coordinador de producto",

    # Commercial Strategy (English)
    "commercial strategy",
    "commercial planning",
    "strategic planning",
    "business strategy",

    # Commercial Strategy (Spanish)
    "estrategia comercial",
    "planning comercial",
    "planeación comercial",
    "planificación comercial",

    # Revenue & Network Planning (English)
    "revenue management",
    "network planning",
    "regional planning",
    "revenue analyst",
    "network analyst",

    # Revenue & Network Planning (Spanish)
    "gestión de ingresos",
    "planificación de red",
    "planificación regional",
    "analista de ingresos",

    # Analytics & BI (English)
    "business intelligence analyst",
    "commercial analyst",
    "data analyst",
    "performance analyst",
    "KPI analyst",

    # Analytics & BI (Spanish)
    "analista de inteligencia de negocios",
    "analista comercial",
    "analista de datos",
    "analista de desempeño",

    # Sales Force Effectiveness (English)
    "sales force effectiveness",
    "sales effectiveness",
    "sales operations",
    "commercial operations",

    # Sales Force Effectiveness (Spanish)
    "efectividad de ventas",
    "operaciones de ventas",
    "operaciones comerciales",

    # Process & Operations (English)
    "process manager",
    "process coordinator",
    "business process",
    "operations analyst",

    # Process & Operations (Spanish)
    "gerente de procesos",
    "coordinador de procesos",
    "analista de operaciones",

    # Budget & Financial Planning (English)
    "budget planning",
    "financial planning analyst",
    "commercial controller",

    # Budget & Financial Planning (Spanish)
    "planificación presupuestaria",
    "analista de planificación financiera",
    "controller comercial",
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
Historical Job Scraper for Divya Rajani - Panama
{'='*70}
Location: {LOCATION}
Time Range: Past 30 days (covering last 2 weeks)
Languages: Spanish & English
Job Types: Product, Commercial Strategy, Analytics, Revenue Mgmt
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
            print(f"\n[SUCCESS] Historical scrape completed for Divya!")
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
