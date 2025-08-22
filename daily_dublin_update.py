#!/usr/bin/env python3
"""
Daily Dublin Job Database Update Script
Searches for Dublin jobs in the last 24 hours and categorizes them as:
- New Jobs: Jobs that weren't in the database before
- Last 24 Hours Jobs: Jobs that were already in the database but match 24h criteria
"""

import os
import sys
import json
from datetime import datetime, timedelta
from linkedin_job_scraper import LinkedInJobScraper

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
        
        # Create metadata section
        metadata = {
            "_metadata": {
                "last_updated": current_time,
                "last_dublin_search": current_time,
                "total_jobs": len([j for k, j in jobs_data.items() if not k.startswith("_")]),
                "dublin_jobs": len([j for k, j in jobs_data.items() if not k.startswith("_") and "dublin" in j.get("location", "").lower()]),
                "new_jobs_count": len([j for k, j in jobs_data.items() if not k.startswith("_") and j.get("is_new", False)]),
                "last_24h_jobs_count": len([j for k, j in jobs_data.items() if not k.startswith("_") and j.get("category") == "last_24h"])
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

def run_dublin_job_search():
    """Run Dublin-specific job search for last 24 hours"""
    
    print("🚀 Starting Daily Dublin Job Search (Last 24 Hours)")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Target: Dublin, Ireland - Software Jobs - Last 24 Hours")
    
    # Load existing jobs
    existing_jobs = load_existing_jobs()
    old_count = len([j for k, j in existing_jobs.items() if not k.startswith("_")])
    dublin_old_count = len([j for k, j in existing_jobs.items() if not k.startswith("_") and "dublin" in j.get("location", "").lower()])
    
    print(f"📊 Current database: {old_count} total jobs ({dublin_old_count} Dublin jobs)")
    
    # Dublin-specific search terms
    search_terms = [
        "Software Engineer Dublin",
        "Python Developer Dublin", 
        "React Developer Dublin",
        "Full Stack Developer Dublin",
        "Backend Developer Dublin",
        "Frontend Developer Dublin",
        "JavaScript Developer Dublin",
        "Node.js Developer Dublin",
        "Senior Software Engineer Dublin",
        "Junior Software Engineer Dublin"
    ]
    
    # Initialize scraper
    scraper = LinkedInJobScraper(headless=True)
    
    all_new_jobs = {}
    successful_searches = 0
    
    try:
        for term in search_terms:
            print(f"\n🔍 Searching: {term}")
            
            try:
                # Search with Dublin location and 24-hour filter
                results = scraper.search_jobs(
                    keywords=term,
                    location="Dublin, Ireland",
                    date_filter="24h"  # Last 24 hours only
                )
                
                if results:
                    print(f"   ✅ Found {len(results)} jobs")
                    # Merge results (avoiding duplicates)
                    for job_id, job_data in results.items():
                        if job_id not in all_new_jobs:
                            all_new_jobs[job_id] = job_data
                    successful_searches += 1
                else:
                    print(f"   ⚠️ No jobs found")
                    
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
                continue
        
        # Categorize jobs
        print(f"\n📋 Categorizing jobs...")
        categorized_jobs, new_count, last_24h_count = categorize_jobs(existing_jobs, all_new_jobs)
        
        # Save updated database
        if save_jobs_with_categories(categorized_jobs):
            total_count = len([j for k, j in categorized_jobs.items() if not k.startswith("_")])
            dublin_count = len([j for k, j in categorized_jobs.items() if not k.startswith("_") and "dublin" in j.get("location", "").lower()])
            
            print(f"\n📈 Results Summary:")
            print(f"   🆕 New jobs: {new_count}")
            print(f"   🕐 Last 24h jobs: {last_24h_count}")
            print(f"   📊 Total jobs in database: {total_count}")
            print(f"   🏙️ Dublin jobs: {dublin_count}")
            print(f"   ✅ Successful searches: {successful_searches}/{len(search_terms)}")
            
            if new_count > 0 or last_24h_count > 0:
                print(f"\n🎉 Update completed successfully!")
                print(f"📝 Next steps:")
                print(f"   1. git add jobs_database.json")
                print(f"   2. git commit -m 'Dublin 24h job update - {datetime.now().strftime('%Y-%m-%d')}'")
                print(f"   3. git push")
                print(f"   4. Check your Railway app for updated job categories!")
            else:
                print(f"\n🔄 No new jobs found, database unchanged")
                
        else:
            print(f"❌ Failed to save jobs database")
            return False
            
    except Exception as e:
        print(f"❌ Search process failed: {e}")
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
    
    # Run the Dublin job search
    success = run_dublin_job_search()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)