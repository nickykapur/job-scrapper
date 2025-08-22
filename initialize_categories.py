#!/usr/bin/env python3
"""
Initialize existing jobs with categories for the new Dublin tracking system
"""

import json
import os
from datetime import datetime

def initialize_job_categories():
    """Initialize existing jobs with 'existing' category"""
    
    print("🚀 Initializing Job Categories for Dublin Tracking System")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load existing jobs
    jobs_file = "jobs_database.json"
    if not os.path.exists(jobs_file):
        print("❌ No jobs_database.json found!")
        return False
    
    try:
        with open(jobs_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        print(f"📊 Loaded {len(jobs)} entries from database")
    except Exception as e:
        print(f"❌ Error loading jobs: {e}")
        return False
    
    # Count and categorize
    total_jobs = 0
    dublin_jobs = 0
    updated_jobs = 0
    
    for job_id, job_data in jobs.items():
        if job_id.startswith("_"):  # Skip metadata
            continue
            
        total_jobs += 1
        
        # Check if it's a Dublin job
        location = job_data.get("location", "").lower()
        is_dublin = "dublin" in location
        
        if is_dublin:
            dublin_jobs += 1
        
        # Add category if missing
        if "category" not in job_data:
            job_data["category"] = "existing"
            job_data["initialized_at"] = datetime.now().isoformat()
            updated_jobs += 1
    
    # Add metadata
    current_time = datetime.now().isoformat()
    jobs["_metadata"] = {
        "last_updated": current_time,
        "categories_initialized": current_time,
        "total_jobs": total_jobs,
        "dublin_jobs": dublin_jobs,
        "system_version": "dublin_tracking_v1"
    }
    
    # Save updated database
    try:
        with open(jobs_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print(f"✅ Database updated successfully!")
    except Exception as e:
        print(f"❌ Error saving jobs: {e}")
        return False
    
    # Show results
    print(f"\n📈 Initialization Results:")
    print(f"   📊 Total jobs: {total_jobs}")
    print(f"   🏙️ Dublin jobs: {dublin_jobs}")
    print(f"   🔄 Jobs updated with categories: {updated_jobs}")
    
    if dublin_jobs > 0:
        print(f"\n🎯 Your Dublin Jobs are Ready!")
        print(f"   All existing jobs are now categorized as 'existing'")
        print(f"   Next run of daily_dublin_update.py will:")
        print(f"   - Search for new Dublin jobs (last 24h)")
        print(f"   - Mark new jobs as 'new' category")
        print(f"   - Mark overlapping jobs as 'last_24h' category")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Run: python daily_dublin_update.py")
        print(f"   2. Check your Railway app for categorized jobs")
        print(f"   3. Set up daily automation if desired")
    else:
        print(f"\n⚠️ No Dublin jobs found in current database")
        print(f"   Run daily_dublin_update.py to search for Dublin jobs")
    
    return True

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Initialize categories
    success = initialize_job_categories()
    
    if success:
        print(f"\n✅ Job categories initialized successfully!")
        print(f"🎉 Your Dublin tracking system is ready to use!")
    else:
        print(f"\n❌ Failed to initialize job categories")