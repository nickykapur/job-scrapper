#!/usr/bin/env python3
"""
Daily Multi-Country Job Database Update Script
Searches for jobs across multiple European countries in the last 24 hours and categorizes them as:
- New Jobs: Jobs that weren't in the database before
- Last 24 Hours Jobs: Jobs that were already in the database but match 24h criteria
- Organizes by country for better filtering
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from linkedin_job_scraper import LinkedInJobScraper
import re
import requests

def delete_country_jobs_from_railway(railway_url, country):
    """Delete ALL jobs for a specific country from Railway database

    WARNING: This deletes ALL jobs from the country, not just excess ones.
    Consider using enforce_country_job_limit() instead to keep newest jobs.

    This function is kept for manual cleanup operations only.
    """
    try:
        # Normalize Railway URL
        if not railway_url.startswith('http'):
            railway_url = f'https://{railway_url}'

        api_url = f"{railway_url}/api/jobs/by-country/{country}"
        print(f"[DELETE] Deleting {country} jobs from Railway: {api_url}")

        response = requests.delete(api_url, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"   [OK] Deleted {result.get('jobs_deleted', 0)} jobs from {country}")
            print(f"   [STATS] Total jobs remaining in database: {result.get('total_jobs_in_database', 0)}")
            return True
        else:
            print(f"   [ERROR] Delete failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"   [TIMEOUT] Delete request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"   [ERROR] Delete error: {e}")
        return False

def sync_to_railway(railway_url):
    """Sync to Railway using the sync script"""
    try:
        print(f"[SYNC] Syncing to Railway: {railway_url}")
        result = subprocess.run([
            sys.executable, 'sync_to_railway.py', railway_url
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        if result.returncode == 0:
            print(f"[OK] Railway sync successful!")
            # Print any success output
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip() and ('[OK]' in line or '[STATS]' in line or '[SYNC]' in line):
                        print(f"   {line.strip()}")
            return True
        else:
            print(f"[ERROR] Railway sync failed!")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Railway sync timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"[ERROR] Railway sync error: {e}")
        return False

def load_existing_jobs_from_railway(railway_url):
    """Load existing jobs from Railway database via API"""
    try:
        # Normalize Railway URL
        if not railway_url.startswith('http'):
            railway_url = f'https://{railway_url}'

        api_url = f"{railway_url}/api/jobs"
        print(f"📡 Fetching jobs from Railway: {api_url}")

        response = requests.get(api_url, timeout=30)

        if response.status_code == 200:
            jobs_data = response.json()

            # Fix missing country fields by deriving from location
            fixed_count = 0
            for job_id, job_data in jobs_data.items():
                if job_id.startswith('_'):  # Skip metadata
                    continue

                # If country is missing or "Unknown", try to derive it from location
                if not job_data.get('country') or job_data.get('country') == 'Unknown':
                    location = job_data.get('location', '')
                    if location:
                        derived_country = get_country_from_location(location)
                        if derived_country != 'Unknown':
                            job_data['country'] = derived_country
                            fixed_count += 1

            actual_jobs = {k: v for k, v in jobs_data.items() if not k.startswith('_')}
            print(f"   [OK] Loaded {len(actual_jobs)} jobs from Railway database")
            if fixed_count > 0:
                print(f"   [FIX] Mapped {fixed_count} jobs from location to country")
            return jobs_data
        else:
            print(f"   [ERROR] Failed to load jobs: {response.status_code}")
            return {}

    except requests.exceptions.Timeout:
        print(f"   [TIMEOUT] Request timed out after 30 seconds")
        return {}
    except Exception as e:
        print(f"   [ERROR] Error loading jobs from Railway: {e}")
        return {}

def check_country_job_counts(existing_jobs):
    """Check job counts per country and identify countries that need cleanup"""
    country_counts = {}

    for job_id, job_data in existing_jobs.items():
        if job_id.startswith("_"):
            continue

        country = job_data.get("country", "Unknown")
        if country not in country_counts:
            country_counts[country] = 0
        country_counts[country] += 1

    return country_counts

def enforce_country_job_limit(railway_url, max_jobs=300):
    """Enforce max jobs per country by removing only the oldest jobs

    This is MUCH more efficient than deleting all jobs and re-adding them.
    It keeps the newest N jobs per country and only deletes excess old jobs.

    Args:
        railway_url: Railway URL to call the enforce endpoint
        max_jobs: Maximum number of jobs to keep per country (default: 300)

    Returns:
        True if successful, False otherwise
    """
    if not railway_url:
        print(f"\n[WARN] No Railway URL provided - skipping cleanup")
        return False

    try:
        api_url = f"{railway_url}/api/jobs/enforce-country-limit"
        print(f"\n🌐 Enforcing {max_jobs} jobs per country limit...")
        print(f"[API] Calling: {api_url}")

        response = requests.post(api_url, json={"max_jobs": max_jobs}, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: Deleted {result.get('jobs_deleted', 0)} old jobs")
            print(f"   📊 Total jobs remaining: {result.get('total_jobs_remaining', 0)}")
            print(f"   🌍 Countries processed: {result.get('countries_processed', 0)}")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"   ⏱️ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def save_jobs_with_categories(jobs_data):
    """Save jobs with categorization metadata"""
    try:
        # Add timestamp for this update
        current_time = datetime.now().isoformat()

        # Calculate statistics
        total_jobs = len([j for k, j in jobs_data.items() if not k.startswith("_")])
        new_jobs_count = len([j for k, j in jobs_data.items() if not k.startswith("_") and j.get("is_new", False)])
        last_24h_jobs_count = len([j for k, j in jobs_data.items() if not k.startswith("_") and j.get("category") == "last_24h"])

        # Count by country
        country_stats = {}
        for job_id, job_data in jobs_data.items():
            if job_id.startswith("_"):
                continue
            country = job_data.get("country", "Unknown")
            if country not in country_stats:
                country_stats[country] = {"total": 0, "new": 0, "last_24h": 0}

            country_stats[country]["total"] += 1
            if job_data.get("is_new", False):
                country_stats[country]["new"] += 1
            if job_data.get("category") == "last_24h":
                country_stats[country]["last_24h"] += 1

        # Create metadata section
        metadata = {
            "_metadata": {
                "last_updated": current_time,
                "last_multi_country_search": current_time,
                "total_jobs": total_jobs,
                "new_jobs_count": new_jobs_count,
                "last_24h_jobs_count": last_24h_jobs_count,
                "countries_searched": list(country_stats.keys()),
                "country_statistics": country_stats
            }
        }

        # Combine metadata with jobs
        final_data = {**metadata, **jobs_data}

        with open("jobs_database.json", 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Error saving jobs: {e}")
        return False

def categorize_jobs(existing_jobs, new_scraped_jobs):
    """Categorize jobs into 'new' and 'last_24h' based on whether they existed before"""
    categorized_jobs = {}
    new_count = 0
    last_24h_count = 0

    for job_id, job_data in new_scraped_jobs.items():
        if job_id.startswith("_"):  # Skip metadata
            continue

        job_copy = job_data.copy()

        if job_id in existing_jobs:
            # Job already existed - mark as last_24h
            job_copy["category"] = "last_24h"
            job_copy["is_new"] = False
            job_copy["last_seen_24h"] = datetime.now().isoformat()
            last_24h_count += 1
        else:
            # Brand new job - mark as new
            job_copy["category"] = "new"
            job_copy["is_new"] = True
            job_copy["first_seen"] = datetime.now().isoformat()
            new_count += 1

        categorized_jobs[job_id] = job_copy

    # DON'T keep old jobs - we only want 24h results
    # This ensures the database only contains recent jobs

    return categorized_jobs, new_count, last_24h_count

def limit_jobs_per_country(jobs_data, max_jobs_per_country=20, unlimited_countries=None):
    """Keep only the most recent max_jobs_per_country jobs per country

    Args:
        jobs_data: Dictionary of job data
        max_jobs_per_country: Default limit for countries (default: 20)
        unlimited_countries: List of countries with no limit (e.g., ['Ireland'])
    """
    if unlimited_countries is None:
        unlimited_countries = []

    jobs_by_country = {}

    # Group jobs by country
    for job_id, job_data in jobs_data.items():
        if job_id.startswith("_"):  # Skip metadata
            continue

        country = job_data.get("country", "Unknown")
        if country not in jobs_by_country:
            jobs_by_country[country] = []

        jobs_by_country[country].append((job_id, job_data))

    # Limit each country to max_jobs_per_country most recent jobs
    limited_jobs = {}
    removed_count = 0

    for country, country_jobs in jobs_by_country.items():
        # Sort by scraped_at timestamp (most recent first)
        country_jobs.sort(key=lambda x: x[1].get('scraped_at', ''), reverse=True)

        # Check if this country has unlimited jobs
        if country in unlimited_countries:
            print(f"   [UNLIMITED] {country}: No limit - keeping all {len(country_jobs)} jobs")
        elif len(country_jobs) > max_jobs_per_country:
            removed = len(country_jobs) - max_jobs_per_country
            removed_count += removed
            country_jobs = country_jobs[:max_jobs_per_country]
            print(f"   [TRIM] {country}: Trimmed to {max_jobs_per_country} most recent jobs (removed {removed} old jobs)")

        # Add limited jobs back to the result
        for job_id, job_data in country_jobs:
            limited_jobs[job_id] = job_data

    if removed_count > 0:
        print(f"\n[DELETE] Removed {removed_count} old jobs total (limited countries: {max_jobs_per_country} jobs each)")

    return limited_jobs

def get_country_from_location(location):
    """Extract country name from location string"""
    location_lower = location.lower()
    if "ireland" in location_lower:
        return "Ireland"
    elif "spain" in location_lower:
        return "Spain"
    elif "panama" in location_lower:
        return "Panama"
    elif "chile" in location_lower:
        return "Chile"
    elif "switzerland" in location_lower:
        return "Switzerland"
    elif "netherlands" in location_lower or "amsterdam" in location_lower:
        return "Netherlands"
    elif "germany" in location_lower or "berlin" in location_lower or "munich" in location_lower:
        return "Germany"
    elif "sweden" in location_lower or "stockholm" in location_lower:
        return "Sweden"
    elif "france" in location_lower:
        return "France"
    elif "italy" in location_lower:
        return "Italy"
    else:
        return "Unknown"

def filter_german_language_requirement(job_data):
    """Filter out jobs requiring proficient German language skills"""

    # Fields to check for German language requirements
    text_fields = [
        job_data.get('title', ''),
        job_data.get('company', ''),
        job_data.get('location', ''),
        job_data.get('description', ''),
        job_data.get('requirements', '')
    ]

    # Join all text fields
    combined_text = ' '.join(str(field) for field in text_fields).lower()

    # German language requirement patterns
    german_language_patterns = [
        r'\bfluent\s+(?:in\s+)?german\b',
        r'\bgerman\s+(?:language\s+)?(?:fluency|proficiency|proficient)\b',
        r'\bproficient\s+(?:in\s+)?german\b',
        r'\bnative\s+german\b',
        r'\bgerman\s+native\b',
        r'\bflie[sß]end(?:e[sn]?)?\s+deutsch\b',  # Fließend Deutsch
        r'\bdeutsch\s+(?:als\s+)?muttersprache\b',  # Deutsch als Muttersprache
        r'\bverhandlungssicher(?:e[sn]?)?\s+deutsch\b',  # Verhandlungssicher Deutsch
        r'\bsehr\s+gute\s+deutschkenntnisse\b',  # Sehr gute Deutschkenntnisse
        r'\bdeutsch\s+(?:c1|c2)\b',  # German C1/C2 level
        r'\bc[12]\s+(?:level\s+)?german\b',  # C1/C2 level German
        r'\bmust\s+(?:speak|know)\s+german\b',
        r'\bgerman\s+(?:is\s+)?(?:required|mandatory|essential)\b',
        r'\brequires?\s+german\b',
        r'\badvanced\s+german\b',
        r'\bexcellent\s+german\b',
    ]

    # Check if any German language pattern matches
    for pattern in german_language_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return False  # Filter out this job

    return True  # Keep this job (no German requirement)

def cleanup_old_jobs_by_country(existing_jobs, max_age_days=2, exclude_countries=None):
    """
    Remove jobs older than max_age_days to maintain database performance

    Args:
        existing_jobs: Dictionary of existing jobs
        max_age_days: Maximum age in days for jobs to keep (default: 2 days)
        exclude_countries: List of countries to exclude from cleanup (e.g., ['Ireland'])

    Returns:
        Tuple of (cleaned_jobs, removed_count)
    """
    if exclude_countries is None:
        exclude_countries = []

    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    print(f"[CLEANUP] Removing jobs older than {max_age_days} days (before {cutoff_date.strftime('%Y-%m-%d')})")

    cleaned_jobs = {}
    removed_count = 0
    removed_by_country = {}
    kept_by_country = {}

    for job_id, job_data in existing_jobs.items():
        # Keep metadata entries
        if job_id.startswith('_'):
            cleaned_jobs[job_id] = job_data
            continue

        # Keep applied jobs regardless of age
        if job_data.get('applied', False):
            cleaned_jobs[job_id] = job_data
            continue

        # Get country
        country = job_data.get('country', 'Unknown')

        # Keep jobs from excluded countries
        if country in exclude_countries:
            cleaned_jobs[job_id] = job_data
            if country not in kept_by_country:
                kept_by_country[country] = 0
            kept_by_country[country] += 1
            continue

        # Check job age
        scraped_at_str = job_data.get('scraped_at', '')

        try:
            if scraped_at_str:
                scraped_at = datetime.fromisoformat(scraped_at_str.replace('Z', '+00:00'))

                # Remove timezone info for comparison
                if scraped_at.tzinfo is not None:
                    scraped_at = scraped_at.replace(tzinfo=None)

                if scraped_at < cutoff_date:
                    # Job is too old, remove it
                    removed_count += 1
                    if country not in removed_by_country:
                        removed_by_country[country] = 0
                    removed_by_country[country] += 1
                    continue
        except Exception as e:
            # Keep job if we can't parse the date
            pass

        # Keep the job
        cleaned_jobs[job_id] = job_data
        if country not in kept_by_country:
            kept_by_country[country] = 0
        kept_by_country[country] += 1

    # Print summary
    if removed_count > 0:
        print(f"[CLEANUP] Removed {removed_count} old jobs")
        if removed_by_country:
            print(f"[CLEANUP] Breakdown by country:")
            for country, count in sorted(removed_by_country.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {country}: {count} jobs")
    else:
        print(f"[CLEANUP] No old jobs to remove")

    return cleaned_jobs, removed_count

def filter_high_experience_jobs(job_data):
    """Filter out jobs requiring 5+ years of experience"""

    # Fields to check for experience requirements
    text_fields = [
        job_data.get('title', ''),
        job_data.get('company', ''),
        job_data.get('location', ''),
        job_data.get('description', ''),
        job_data.get('requirements', '')
    ]

    # Join all text fields
    combined_text = ' '.join(str(field) for field in text_fields).lower()

    # Experience patterns that indicate 5+ years requirement
    high_experience_patterns = [
        r'\b(?:5|five|6|six|7|seven|8|eight|9|nine|10|ten)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)\b',
        r'\b(?:5|five|6|six|7|seven|8|eight|9|nine|10|ten)\+?\s*(?:years?|yrs?)\s*(?:in|with|of)\b',
        r'\bminimum\s*(?:of\s*)?(?:5|five|6|six|7|seven|8|eight|9|nine|10|ten)\+?\s*(?:years?|yrs?)\b',
        r'\bat\s*least\s*(?:5|five|6|six|7|seven|8|eight|9|nine|10|ten)\+?\s*(?:years?|yrs?)\b',
        r'\b(?:5|five|6|six|7|seven|8|eight|9|nine|10|ten)\+\s*(?:years?|yrs?)\b',
        r'\bsenior\s*(?:software\s*)?(?:engineer|developer|programmer)\b',
        r'\blead\s*(?:software\s*)?(?:engineer|developer|programmer)\b',
        r'\bprincipal\s*(?:software\s*)?(?:engineer|developer|programmer)\b',
        r'\bstaff\s*(?:software\s*)?(?:engineer|developer|programmer)\b',
        r'\barchitect\b'
    ]

    # Check if any high experience pattern matches
    for pattern in high_experience_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return False  # Filter out this job

    return True  # Keep this job

def run_multi_country_job_search():
    """Run multi-country job search for last 24 hours"""

    print("[MULTI] Starting Multi-Country Job Search (Last 24 Hours)")
    print(f"[DATE] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("[TARGET] Target: Ireland, Spain, Panama, Chile, Netherlands, Germany, Sweden - Software & HR Jobs - Last 24 Hours")

    # Railway configuration
    railway_url = "web-production-110bb.up.railway.app"

    # Load existing jobs from Railway database
    print(f"\n[REFRESH] Checking Railway database for existing jobs...")
    existing_jobs = load_existing_jobs_from_railway(railway_url)
    old_count = len([j for k, j in existing_jobs.items() if not k.startswith("_")])

    print(f"[STATS] Current database: {old_count} total jobs")

    # AUTOMATIC CLEANUP: Remove old jobs if database is too large
    max_total_jobs = 300  # Maximum total jobs threshold
    max_age_days = 2      # Keep jobs from last 2 days only

    if old_count > max_total_jobs:
        print(f"\n[WARN] Database has {old_count} jobs (threshold: {max_total_jobs})")
        print(f"[CLEANUP] Initiating automatic cleanup of jobs older than {max_age_days} days...")

        # Clean up old jobs (keeping Ireland unlimited, keeping all applied jobs)
        cleaned_jobs, removed_count = cleanup_old_jobs_by_country(
            existing_jobs,
            max_age_days=max_age_days,
            exclude_countries=['Ireland']  # Ireland has no limit
        )

        if removed_count > 0:
            print(f"\n[SAVE] Saving cleaned database...")
            # Save cleaned jobs locally first
            if save_jobs_with_categories(cleaned_jobs):
                print(f"   [OK] Saved locally")

                # Sync cleaned database to Railway
                print(f"\n[SYNC] Syncing cleaned database to Railway...")
                if sync_to_railway(railway_url):
                    print(f"   [OK] Railway updated successfully")
                    # Reload after cleanup
                    existing_jobs = load_existing_jobs_from_railway(railway_url)
                    new_count = len([j for k, j in existing_jobs.items() if not k.startswith("_")])
                    print(f"   [STATS] Database now has {new_count} jobs (freed {removed_count} slots)")
                else:
                    print(f"   [WARN] Railway sync failed, but local database is cleaned")
                    existing_jobs = cleaned_jobs
        else:
            print(f"\n[OK] All jobs are recent, no cleanup needed")
    else:
        print(f"[OK] Database size is healthy ({old_count}/{max_total_jobs} jobs)")

    # Check for countries with excess jobs and clean them up
    if len([j for k, j in existing_jobs.items() if not k.startswith("_")]) > 0:
        print(f"\n[SEARCH] Checking for countries with excessive job accumulation...")
        country_counts = check_country_job_counts(existing_jobs)
        print(f"[STATS] Current jobs per country:")
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {country}: {count} jobs")

        # Enforce 300 jobs per country limit (keeps newest, deletes oldest)
        # This is much more efficient than deleting all jobs and re-adding
        enforce_country_job_limit(railway_url, max_jobs=300)

        # Reload jobs to get updated state after cleanup
        existing_jobs = load_existing_jobs_from_railway(railway_url)

    # Multi-country search configuration
    # Limited to main locations for faster scraping
    countries_config = [
        {"location": "Dublin, County Dublin, Ireland", "country": "Ireland"},
        {"location": "Madrid, Community of Madrid, Spain", "country": "Spain"},
        {"location": "Panama City, Panama", "country": "Panama"},
        {"location": "Santiago, Chile", "country": "Chile"},
        {"location": "Amsterdam, North Holland, Netherlands", "country": "Netherlands"},
        {"location": "Berlin, Germany", "country": "Germany"},
        {"location": "Stockholm, Sweden", "country": "Sweden"},
    ]

    # Search terms - Multi-user configuration
    # Software Engineering (User 1)
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

    # HR/Recruitment (User 2) - Expanded for better coverage
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

    # Combine all search terms for comprehensive scraping
    search_terms = software_search_terms + hr_search_terms

    # Initialize scraper
    scraper = LinkedInJobScraper(headless=True)

    all_new_jobs = {}
    successful_searches = 0
    total_searches = len(countries_config) * len(search_terms)
    country_results = {}

    try:
        for country_config in countries_config:
            location = country_config["location"]
            country = country_config["country"]

            print(f"\n[LOCATION] Searching in {location}")
            country_jobs = 0

            if country not in country_results:
                country_results[country] = {"jobs": 0, "searches": 0}

            for term in search_terms:
                print(f"   [SEARCH] {term}")

                try:
                    # Search with location and 24-hour filter
                    results = scraper.search_jobs(
                        keywords=term,
                        location=location,
                        date_filter="24h"  # Last 24 hours only
                    )

                    if results:
                        found_jobs = len(results)
                        print(f"      [OK] Found {found_jobs} jobs")

                        # Filter jobs based on experience and company
                        filtered_jobs = 0
                        high_exp_filtered = 0
                        company_filtered = 0

                        for job_id, job_data in results.items():
                            if job_id not in all_new_jobs:
                                # Apply experience filter
                                if not filter_high_experience_jobs(job_data):
                                    high_exp_filtered += 1
                                    continue

                                # REMOVED: Company filter - now accepting all companies
                                # This ensures we get 20 jobs per country regardless of company

                                # Job passed all filters
                                job_data["country"] = country
                                job_data["search_location"] = location
                                all_new_jobs[job_id] = job_data
                                country_jobs += 1
                                filtered_jobs += 1

                        if high_exp_filtered > 0:
                            print(f"      [REJECT] Filtered out {high_exp_filtered} high-experience jobs")
                        print(f"      [OK] Added {filtered_jobs} suitable jobs")

                        country_results[country]["jobs"] += filtered_jobs
                        successful_searches += 1
                    else:
                        print(f"      [WARN] No jobs found")

                    country_results[country]["searches"] += 1

                except Exception as e:
                    print(f"      [ERROR] Search failed: {e}")
                    continue

            print(f"   [STATS] {country}: {country_jobs} unique jobs found")

        # Categorize jobs
        print(f"\n📋 Categorizing jobs...")
        categorized_jobs, new_count, last_24h_count = categorize_jobs(existing_jobs, all_new_jobs)

        # Limit jobs to 20 per country (except Ireland - no limit)
        print(f"\n[TRIM] Applying job limits per country...")
        print(f"   • Ireland: Unlimited (all jobs kept)")
        print(f"   • Spain, Panama, Chile, Netherlands, Germany, Sweden: 20 jobs each (most recent)")
        categorized_jobs = limit_jobs_per_country(
            categorized_jobs,
            max_jobs_per_country=20,
            unlimited_countries=['Ireland']
        )

        # Save updated database
        if save_jobs_with_categories(categorized_jobs):
            total_count = len([j for k, j in categorized_jobs.items() if not k.startswith("_")])

            print(f"\n[RESULTS] Results Summary:")
            print(f"   [NEW] New jobs: {new_count}")
            print(f"   🕐 Last 24h jobs: {last_24h_count}")
            print(f"   [STATS] Total jobs in database: {total_count}")
            print(f"   [OK] Successful searches: {successful_searches}/{total_searches}")

            print(f"\n[MULTI] Country Breakdown:")
            print(f"{'Country':<20} {'New Jobs':<10} {'24h Jobs':<10} {'Total':<10} {'Success Rate'}")
            print("-" * 65)

            for country, stats in country_results.items():
                country_new = len([j for j in categorized_jobs.values() if j.get('country') == country and j.get('is_new', False)])
                country_24h = len([j for j in categorized_jobs.values() if j.get('country') == country and j.get('category') == 'last_24h'])
                country_total = country_new + country_24h
                success_rate = f"{stats['searches']}/{len(search_terms)}"

                print(f"{country:<20} {country_new:<10} {country_24h:<10} {country_total:<10} {success_rate}")

                # Store detailed stats in metadata
                if 'country_daily_stats' not in categorized_jobs.get('_metadata', {}):
                    if '_metadata' not in categorized_jobs:
                        categorized_jobs['_metadata'] = {}
                    categorized_jobs['_metadata']['country_daily_stats'] = {}

                categorized_jobs['_metadata']['country_daily_stats'][country] = {
                    'new_jobs': country_new,
                    'last_24h_jobs': country_24h,
                    'total_jobs_found': country_total,
                    'searches_completed': stats['searches'],
                    'searches_total': len(search_terms),
                    'success_rate': round((stats['searches'] / len(search_terms)) * 100, 1),
                    'date': datetime.now().strftime('%Y-%m-%d')
                }

            # Show top performing countries
            top_countries = sorted(
                [(country, stats['new_jobs'] + stats['last_24h_jobs']) for country, stats in categorized_jobs['_metadata']['country_daily_stats'].items()],
                key=lambda x: x[1],
                reverse=True
            )[:3]

            print(f"\n[TOP] Top Performing Countries Today:")
            for i, (country, job_count) in enumerate(top_countries, 1):
                if job_count > 0:
                    print(f"   {i}. {country}: {job_count} jobs")

            if new_count > 0 or last_24h_count > 0:
                print(f"\n[SUCCESS] Multi-country update completed successfully!")
                print(f"[STATS] Daily Summary:")
                print(f"   • Best market: {top_countries[0][0]} ({top_countries[0][1]} jobs)" if top_countries[0][1] > 0 else "   • No standout markets today")
                print(f"   • Countries active: {len([c for c, s in categorized_jobs['_metadata']['country_daily_stats'].items() if s['new_jobs'] + s['last_24h_jobs'] > 0])}/7")
                print(f"   • Total job opportunities: {new_count + last_24h_count}")
                print(f"   • Experience filtering: Jobs requiring 5+ years filtered out automatically")
                print(f"   • Company filtering: Netherlands, Germany, Sweden limited to top 20+ tech companies")

                print(f"\n[NOTE] Next steps:")
                print(f"   1. git add jobs_database.json")
                print(f"   2. git commit -m 'Multi-country 24h job update - {datetime.now().strftime('%Y-%m-%d')}'")
                print(f"   3. git push")
                print(f"   4. Check country stats in your dashboard!")

                # Auto-sync to Railway
                print(f"\n[SYNC] Auto-syncing to Railway...")
                try:
                    sync_success = sync_to_railway("web-production-110bb.up.railway.app")
                    if sync_success:
                        print(f"[SUCCESS] Successfully synced to Railway! Your jobs are now live.")
                    else:
                        print(f"[WARN] Railway sync failed, but data is saved locally.")
                        print(f"[NOTE] You can manually sync later with:")
                        print(f"   python3 sync_to_railway.py web-production-110bb.up.railway.app")
                except Exception as sync_error:
                    print(f"[WARN] Railway sync error: {sync_error}")
                    print(f"📁 Data is saved locally in jobs_database.json")
                    print(f"[NOTE] You can manually sync later with:")
                    print(f"   python3 sync_to_railway.py web-production-110bb.up.railway.app")
            else:
                print(f"\n[REFRESH] No new jobs found across all countries, database unchanged")

        else:
            print(f"[ERROR] Failed to save jobs database")
            return False

    except Exception as e:
        print(f"[ERROR] Multi-country search process failed: {e}")
        return False

    finally:
        # Close scraper
        try:
            scraper.close()
        except:
            pass

    return successful_searches > 0

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Run the multi-country job search
    success = run_multi_country_job_search()

    # Exit with appropriate code
    sys.exit(0 if success else 1)