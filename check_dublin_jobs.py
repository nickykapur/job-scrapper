#!/usr/bin/env python3
"""
Check current Dublin jobs in the database and show categorization status
"""

import json
import os
from datetime import datetime, timedelta

def check_dublin_jobs():
    """Check and categorize existing Dublin jobs"""
    
    print("🔍 Analyzing Current Dublin Jobs Database")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Load existing jobs
    jobs_file = "jobs_database.json"
    if not os.path.exists(jobs_file):
        print("❌ No jobs_database.json found!")
        return
    
    try:
        with open(jobs_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
    except Exception as e:
        print(f"❌ Error loading jobs: {e}")
        return
    
    # Filter and analyze jobs
    all_jobs = {k: v for k, v in jobs.items() if not k.startswith("_")}
    dublin_jobs = {k: v for k, v in all_jobs.items() if "dublin" in v.get("location", "").lower()}
    
    # Categorize existing jobs
    categorized = {
        "new": [],
        "last_24h": [],
        "existing": [],
        "no_category": []
    }
    
    for job_id, job in dublin_jobs.items():
        category = job.get("category", "none")
        if category == "new":
            categorized["new"].append(job)
        elif category == "last_24h":
            categorized["last_24h"].append(job)
        elif category == "existing":
            categorized["existing"].append(job)
        else:
            categorized["no_category"].append(job)
    
    # Show summary
    print(f"📊 Database Summary:")
    print(f"   Total jobs: {len(all_jobs)}")
    print(f"   Dublin jobs: {len(dublin_jobs)}")
    print(f"   Applied Dublin jobs: {len([j for j in dublin_jobs.values() if j.get('applied', False)])}")
    
    print(f"\n🏙️ Dublin Job Categories:")
    print(f"   🆕 New: {len(categorized['new'])}")
    print(f"   🕐 Last 24h: {len(categorized['last_24h'])}")
    print(f"   📋 Existing: {len(categorized['existing'])}")
    print(f"   ❓ No category: {len(categorized['no_category'])}")
    
    # Show sample jobs
    if dublin_jobs:
        print(f"\n📝 Dublin Jobs Sample:")
        for i, (job_id, job) in enumerate(list(dublin_jobs.items())[:10]):
            category = job.get("category", "none")
            applied = "✅" if job.get("applied", False) else "⏳"
            print(f"   {i+1:2d}. {applied} {job['title'][:40]:<40} | {job['company'][:25]:<25} | {category}")
    
    # Check if categorization is needed
    if len(categorized['no_category']) > 0:
        print(f"\n💡 Recommendation:")
        print(f"   {len(categorized['no_category'])} jobs have no category assigned")
        print(f"   Run 'python daily_dublin_update.py' to:")
        print(f"   - Search for new Dublin jobs (last 24h)")
        print(f"   - Categorize existing jobs properly")
        print(f"   - Update the database with categories")
    else:
        print(f"\n✅ All Dublin jobs are properly categorized!")
    
    # Show recent job dates
    if dublin_jobs:
        print(f"\n📅 Job Posting Dates:")
        dates = {}
        for job in dublin_jobs.values():
            posted = job.get("posted_date", "unknown")
            dates[posted] = dates.get(posted, 0) + 1
        
        for date, count in sorted(dates.items()):
            print(f"   {date}: {count} jobs")

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check Dublin jobs
    check_dublin_jobs()