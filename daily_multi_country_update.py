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

def sync_to_railway(railway_url):
    """Sync to Railway using the sync script"""
    try:
        print(f"🚀 Syncing to Railway: {railway_url}")
        result = subprocess.run([
            sys.executable, 'sync_to_railway.py', railway_url
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        if result.returncode == 0:
            print(f"✅ Railway sync successful!")
            # Print any success output
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip() and ('✅' in line or '📊' in line or '🚀' in line):
                        print(f"   {line.strip()}")
            return True
        else:
            print(f"❌ Railway sync failed!")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ Railway sync timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Railway sync error: {e}")
        return False

def load_existing_jobs():
    """Load existing jobs from database"""
    jobs_file = "jobs_database.json"
    if os.path.exists(jobs_file):
        try:
            with open(jobs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading existing jobs: {e}")
            return {}
    return {}

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
        print(f"❌ Error saving jobs: {e}")
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

    # Keep existing jobs that weren't found in the 24h search
    for job_id, job_data in existing_jobs.items():
        if job_id.startswith("_"):  # Skip metadata
            continue

        if job_id not in categorized_jobs:
            job_copy = job_data.copy()
            # Reset category if it was temporary
            if job_copy.get("category") in ["new", "last_24h"]:
                job_copy["category"] = "existing"
            categorized_jobs[job_id] = job_copy

    return categorized_jobs, new_count, last_24h_count

def get_country_from_location(location):
    """Extract country name from location string"""
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

def run_multi_country_job_search():
    """Run multi-country job search for last 24 hours"""

    print("🌍 Starting Multi-Country Job Search (Last 24 Hours)")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Target: 13 European Countries - Software Jobs - Last 24 Hours")

    # Load existing jobs
    existing_jobs = load_existing_jobs()
    old_count = len([j for k, j in existing_jobs.items() if not k.startswith("_")])

    print(f"📊 Current database: {old_count} total jobs")

    # Multi-country search configuration
    # Limited to 4 main locations for faster scraping
    countries_config = [
        {"location": "Dublin, County Dublin, Ireland", "country": "Ireland"},
        {"location": "Barcelona, Catalonia, Spain", "country": "Spain"},
        {"location": "Berlin, Germany", "country": "Germany"},
        {"location": "London, England, United Kingdom", "country": "United Kingdom"},
    ]

    # Search terms
    search_terms = [
        "Software Engineer",
        "Python Developer",
        "React Developer",
        "Full Stack Developer",
        "Backend Developer",
        "Frontend Developer",
        "JavaScript Developer",
        "Node.js Developer",
        "Senior Software Engineer",
        "Junior Software Engineer"
    ]

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

            print(f"\n🏙️ Searching in {location}")
            country_jobs = 0

            if country not in country_results:
                country_results[country] = {"jobs": 0, "searches": 0}

            for term in search_terms:
                print(f"   🔍 {term}")

                try:
                    # Search with location and 24-hour filter
                    results = scraper.search_jobs(
                        keywords=term,
                        location=location,
                        date_filter="24h"  # Last 24 hours only
                    )

                    if results:
                        found_jobs = len(results)
                        print(f"      ✅ Found {found_jobs} jobs")

                        # Add country info to each job and merge results
                        for job_id, job_data in results.items():
                            if job_id not in all_new_jobs:
                                job_data["country"] = country
                                job_data["search_location"] = location
                                all_new_jobs[job_id] = job_data
                                country_jobs += 1

                        country_results[country]["jobs"] += found_jobs
                        successful_searches += 1
                    else:
                        print(f"      ⚠️ No jobs found")

                    country_results[country]["searches"] += 1

                except Exception as e:
                    print(f"      ❌ Search failed: {e}")
                    continue

            print(f"   📊 {country}: {country_jobs} unique jobs found")

        # Categorize jobs
        print(f"\n📋 Categorizing jobs...")
        categorized_jobs, new_count, last_24h_count = categorize_jobs(existing_jobs, all_new_jobs)

        # Save updated database
        if save_jobs_with_categories(categorized_jobs):
            total_count = len([j for k, j in categorized_jobs.items() if not k.startswith("_")])

            print(f"\n📈 Results Summary:")
            print(f"   🆕 New jobs: {new_count}")
            print(f"   🕐 Last 24h jobs: {last_24h_count}")
            print(f"   📊 Total jobs in database: {total_count}")
            print(f"   ✅ Successful searches: {successful_searches}/{total_searches}")

            print(f"\n🌍 Country Breakdown:")
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

            print(f"\n🏆 Top Performing Countries Today:")
            for i, (country, job_count) in enumerate(top_countries, 1):
                if job_count > 0:
                    print(f"   {i}. {country}: {job_count} jobs")

            if new_count > 0 or last_24h_count > 0:
                print(f"\n🎉 Multi-country update completed successfully!")
                print(f"📊 Daily Summary:")
                print(f"   • Best market: {top_countries[0][0]} ({top_countries[0][1]} jobs)" if top_countries[0][1] > 0 else "   • No standout markets today")
                print(f"   • Countries active: {len([c for c, s in categorized_jobs['_metadata']['country_daily_stats'].items() if s['new_jobs'] + s['last_24h_jobs'] > 0])}/8")
                print(f"   • Total job opportunities: {new_count + last_24h_count}")

                print(f"\n📝 Next steps:")
                print(f"   1. git add jobs_database.json")
                print(f"   2. git commit -m 'Multi-country 24h job update - {datetime.now().strftime('%Y-%m-%d')}'")
                print(f"   3. git push")
                print(f"   4. Check country stats in your dashboard!")

                # Auto-sync to Railway
                print(f"\n🚀 Auto-syncing to Railway...")
                try:
                    sync_success = sync_to_railway("web-production-110bb.up.railway.app")
                    if sync_success:
                        print(f"🎉 Successfully synced to Railway! Your jobs are now live.")
                    else:
                        print(f"⚠️ Railway sync failed, but data is saved locally.")
                        print(f"📝 You can manually sync later with:")
                        print(f"   python3 sync_to_railway.py web-production-110bb.up.railway.app")
                except Exception as sync_error:
                    print(f"⚠️ Railway sync error: {sync_error}")
                    print(f"📁 Data is saved locally in jobs_database.json")
                    print(f"📝 You can manually sync later with:")
                    print(f"   python3 sync_to_railway.py web-production-110bb.up.railway.app")
            else:
                print(f"\n🔄 No new jobs found across all countries, database unchanged")

        else:
            print(f"❌ Failed to save jobs database")
            return False

    except Exception as e:
        print(f"❌ Multi-country search process failed: {e}")
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