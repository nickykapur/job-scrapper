#!/usr/bin/env python3
"""
Cleanup Old Jobs Script
Removes jobs older than specified days from the database to maintain database performance
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any

def load_jobs_from_file(filepath: str = "jobs_database.json") -> Dict[str, Any]:
    """Load jobs from local JSON file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"[ERROR] Error loading jobs from file: {e}")
        return {}

def save_jobs_to_file(jobs: Dict[str, Any], filepath: str = "jobs_database.json"):
    """Save jobs to local JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved cleaned jobs to {filepath}")
        return True
    except Exception as e:
        print(f"[ERROR] Error saving jobs to file: {e}")
        return False

def cleanup_old_jobs(
    jobs: Dict[str, Any],
    max_days: int = 2,
    exclude_applied: bool = True,
    exclude_countries: list = None
) -> tuple[Dict[str, Any], int]:
    """
    Clean up jobs older than max_days

    Args:
        jobs: Dictionary of jobs
        max_days: Maximum age in days for jobs to keep (default: 2 days)
        exclude_applied: If True, keep applied jobs regardless of age
        exclude_countries: List of countries to not clean (keep all jobs)

    Returns:
        Tuple of (cleaned_jobs_dict, removed_count)
    """
    if exclude_countries is None:
        exclude_countries = []

    cutoff_date = datetime.now() - timedelta(days=max_days)
    print(f"🗓️  Removing jobs older than {max_days} days (before {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')})")

    cleaned_jobs = {}
    removed_count = 0
    removed_by_country = {}
    kept_by_country = {}

    for job_id, job_data in jobs.items():
        # Keep metadata entries
        if job_id.startswith('_'):
            cleaned_jobs[job_id] = job_data
            continue

        # Keep applied jobs if exclude_applied is True
        if exclude_applied and job_data.get('applied', False):
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
            print(f"[WARN] Warning: Could not parse date for job {job_id}: {e}")
            # Keep job if we can't parse the date

        # Keep the job
        cleaned_jobs[job_id] = job_data
        if country not in kept_by_country:
            kept_by_country[country] = 0
        kept_by_country[country] += 1

    # Print summary
    print(f"\n[STATS] Cleanup Summary:")
    print(f"   [DELETE] Total jobs removed: {removed_count}")

    if removed_by_country:
        print(f"\n   Removed by country:")
        for country, count in sorted(removed_by_country.items(), key=lambda x: x[1], reverse=True):
            print(f"      • {country}: {count} jobs")

    if kept_by_country:
        print(f"\n   [OK] Kept by country:")
        for country, count in sorted(kept_by_country.items(), key=lambda x: x[1], reverse=True):
            print(f"      • {country}: {count} jobs")

    return cleaned_jobs, removed_count

def sync_to_railway(railway_url: str, jobs: Dict[str, Any]) -> bool:
    """Sync cleaned jobs to Railway"""
    try:
        if not railway_url.startswith('http'):
            railway_url = f'https://{railway_url}'

        api_url = f"{railway_url}/api/jobs/sync"
        print(f"\n[SYNC] Syncing to Railway: {api_url}")

        response = requests.post(api_url, json=jobs, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print(f"   [OK] Successfully synced to Railway")
            print(f"   [STATS] Jobs in database: {result.get('total_jobs', 0)}")
            return True
        else:
            print(f"   [ERROR] Sync failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"   [TIMEOUT] Sync request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"   [ERROR] Sync error: {e}")
        return False

def main():
    print("[CLEANUP] Job Database Cleanup Tool")
    print("=" * 60)

    # Configuration
    max_age_days = 2
    exclude_applied_jobs = True
    exclude_countries = ['Ireland']  # Ireland has unlimited job limit
    railway_url = "web-production-110bb.up.railway.app"

    print(f"\n[CONFIG] Configuration:")
    print(f"   • Max job age: {max_age_days} days")
    print(f"   • Keep applied jobs: {exclude_applied_jobs}")
    print(f"   • Countries without limit: {', '.join(exclude_countries)}")

    # Load jobs
    print(f"\n[FILE] Loading jobs from local database...")
    jobs = load_jobs_from_file()

    if not jobs:
        print("[ERROR] No jobs found in database")
        return 1

    initial_count = len([k for k in jobs.keys() if not k.startswith('_')])
    print(f"   [STATS] Found {initial_count} jobs")

    # Clean up old jobs
    print(f"\n[CLEANUP] Cleaning up jobs older than {max_age_days} days...")
    cleaned_jobs, removed_count = cleanup_old_jobs(
        jobs,
        max_days=max_age_days,
        exclude_applied=exclude_applied_jobs,
        exclude_countries=exclude_countries
    )

    final_count = len([k for k in cleaned_jobs.keys() if not k.startswith('_')])

    print(f"\n[OK] Cleanup complete!")
    print(f"   Before: {initial_count} jobs")
    print(f"   After: {final_count} jobs")
    print(f"   Removed: {removed_count} jobs")

    if removed_count == 0:
        print("\n[INFO] No jobs needed to be removed!")
        return 0

    # Ask for confirmation before saving
    if initial_count > 0:
        response = input("\n[SAVE] Save changes to local database? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            if save_jobs_to_file(cleaned_jobs):
                print("[OK] Local database updated")

                # Ask about Railway sync
                response = input("\n[CLOUD] Sync to Railway? (yes/no): ")
                if response.lower() in ['yes', 'y']:
                    if sync_to_railway(railway_url, cleaned_jobs):
                        print("[OK] Railway database updated")
                    else:
                        print("[WARN] Railway sync failed, but local changes are saved")
            else:
                print("[ERROR] Failed to save local changes")
        else:
            print("[ERROR] Changes not saved")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[WARN] Cleanup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
