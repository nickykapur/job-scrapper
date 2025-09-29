#!/usr/bin/env python3
"""
Fix missing country fields in existing jobs database
Adds country field based on location string
"""

import json
import os
from datetime import datetime

def get_country_from_location(location):
    """Extract country name from location string"""
    if not location:
        return "Unknown"

    location_lower = location.lower()
    if "ireland" in location_lower:
        return "Ireland"
    elif "spain" in location_lower:
        return "Spain"
    elif "germany" in location_lower:
        return "Germany"
    elif "switzerland" in location_lower:
        return "Switzerland"
    elif "united kingdom" in location_lower or "england" in location_lower or "scotland" in location_lower:
        return "United Kingdom"
    elif "netherlands" in location_lower:
        return "Netherlands"
    elif "france" in location_lower:
        return "France"
    elif "italy" in location_lower:
        return "Italy"
    else:
        return "Unknown"

def fix_job_countries():
    """Add missing country fields to existing jobs"""
    jobs_file = "jobs_database.json"

    if not os.path.exists(jobs_file):
        print("❌ jobs_database.json not found")
        return False

    print("🔧 Fixing missing country fields in jobs database...")

    # Load existing jobs
    with open(jobs_file, 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)

    jobs_updated = 0
    jobs_total = 0

    for job_id, job_data in jobs_data.items():
        if job_id.startswith('_'):  # Skip metadata
            continue

        jobs_total += 1

        # Check if country field is missing
        if 'country' not in job_data or not job_data.get('country'):
            # Extract country from location
            country = get_country_from_location(job_data.get('location', ''))
            job_data['country'] = country
            jobs_updated += 1

            if jobs_updated <= 5:  # Show first 5 examples
                print(f"   ✅ {job_id}: {job_data.get('location', 'No location')} → {country}")

    if jobs_updated > 0:
        # Update metadata timestamp
        if '_metadata' in jobs_data:
            jobs_data['_metadata']['last_updated'] = datetime.now().isoformat()
            jobs_data['_metadata']['country_fix_applied'] = datetime.now().isoformat()

        # Save updated jobs
        with open(jobs_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)

        print(f"\n📊 Results:")
        print(f"   📋 Total jobs processed: {jobs_total}")
        print(f"   🔧 Jobs updated with country: {jobs_updated}")
        print(f"   ✅ Database saved successfully")

        return True
    else:
        print(f"\n✅ All {jobs_total} jobs already have country fields")
        return True

if __name__ == "__main__":
    success = fix_job_countries()
    if success:
        print("\n🎉 Country fix completed! Your jobs now have proper country fields.")
        print("🚀 Restart your frontend to see the countries properly organized.")
    else:
        print("\n❌ Country fix failed.")