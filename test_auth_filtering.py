#!/usr/bin/env python3
"""
Test script to verify authentication and job filtering
"""
import requests
import json
from collections import Counter

API_URL = "https://web-production-110bb.up.railway.app"

def test_without_auth():
    """Test /api/jobs without authentication"""
    print("=" * 80)
    print("TEST 1: API call WITHOUT authentication")
    print("=" * 80)

    response = requests.get(f"{API_URL}/api/jobs")
    jobs = response.json()

    # Filter out metadata
    actual_jobs = {k: v for k, v in jobs.items() if not k.startswith('_')}

    # Count by job type
    job_types = Counter(job.get('job_type', 'unknown') for job in actual_jobs.values())

    print(f"Total jobs returned: {len(actual_jobs)}")
    print(f"Job types distribution:")
    for job_type, count in job_types.most_common():
        print(f"  - {job_type}: {count}")
    print()

    return len(actual_jobs), job_types

def test_with_auth(username, password):
    """Test /api/jobs with authentication"""
    print("=" * 80)
    print(f"TEST 2: API call WITH authentication (user: {username})")
    print("=" * 80)

    # Login
    print("Logging in...")
    login_response = requests.post(
        f"{API_URL}/api/auth/login",
        data={
            "username": username,
            "password": password
        }
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return None, None

    token = login_response.json()['access_token']
    print(f"✅ Login successful! Token: {token[:20]}...")

    # Get user preferences
    prefs_response = requests.get(
        f"{API_URL}/api/auth/preferences",
        headers={"Authorization": f"Bearer {token}"}
    )

    if prefs_response.status_code == 200:
        prefs = prefs_response.json()
        print(f"\n📋 User preferences:")
        print(f"  - Job types: {prefs.get('job_types', [])}")
        print(f"  - Experience levels: {prefs.get('experience_levels', [])}")
        print(f"  - Preferred countries: {prefs.get('preferred_countries', [])}")

    # Get jobs with authentication
    print(f"\nFetching jobs with auth token...")
    jobs_response = requests.get(
        f"{API_URL}/api/jobs",
        headers={"Authorization": f"Bearer {token}"}
    )

    if jobs_response.status_code != 200:
        print(f"❌ Failed to get jobs: {jobs_response.status_code}")
        print(f"Response: {jobs_response.text}")
        return None, None

    jobs = jobs_response.json()

    # Filter out metadata
    actual_jobs = {k: v for k, v in jobs.items() if not k.startswith('_')}

    # Count by job type
    job_types = Counter(job.get('job_type', 'unknown') for job in actual_jobs.values())

    print(f"\n✅ Jobs returned: {len(actual_jobs)}")
    print(f"Job types distribution:")
    for job_type, count in job_types.most_common():
        print(f"  - {job_type}: {count}")

    # Check for non-software jobs
    non_software = [job for job in actual_jobs.values() if job.get('job_type') != 'software']
    if non_software:
        print(f"\n⚠️  WARNING: Found {len(non_software)} non-software jobs!")
        print("Sample non-software jobs:")
        for job in non_software[:5]:
            print(f"  - {job.get('title')} ({job.get('company')}) - Type: {job.get('job_type')}")
    else:
        print(f"\n✅ All jobs are software jobs as expected!")

    print()
    return len(actual_jobs), job_types

if __name__ == "__main__":
    # Test without auth
    total_unauth, types_unauth = test_without_auth()

    # Test with auth
    print("\nEnter credentials for software_admin:")
    username = input("Username (default: software_admin): ").strip() or "software_admin"
    password = input("Password: ").strip()

    if password:
        total_auth, types_auth = test_with_auth(username, password)

        if total_auth is not None:
            print("=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Without auth: {total_unauth} jobs returned (all types mixed)")
            print(f"With auth:    {total_auth} jobs returned (should be filtered)")

            if total_auth < total_unauth:
                print(f"\n✅ Filtering is working! Reduced from {total_unauth} to {total_auth} jobs")
            else:
                print(f"\n❌ Filtering NOT working! Still showing all {total_auth} jobs")
    else:
        print("No password provided, skipping authenticated test")
