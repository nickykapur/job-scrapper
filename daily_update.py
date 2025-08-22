#!/usr/bin/env python3
"""
Daily Job Database Update Script
Run this locally every day to refresh your job database
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def update_jobs_database():
    """Update the jobs database with fresh LinkedIn data"""
    
    print("🚀 Starting daily job database update...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load current job count
    jobs_file = "jobs_database.json"
    old_count = 0
    if os.path.exists(jobs_file):
        try:
            with open(jobs_file, 'r') as f:
                old_jobs = json.load(f)
                old_count = len(old_jobs)
        except:
            old_count = 0
    
    print(f"📊 Current jobs in database: {old_count}")
    
    # Search terms to scrape
    search_terms = [
        "Software Engineer",
        "Python Developer", 
        "React Developer",
        "Full Stack Developer",
        "Backend Developer",
        "Frontend Developer"
    ]
    
    success_count = 0
    
    # Run scraping for each search term
    for term in search_terms:
        print(f"\n🔍 Searching for: {term}")
        if run_command(f'python main.py search "{term}" --headless', f"Scraping {term} jobs"):
            success_count += 1
    
    # Check new job count
    new_count = 0
    if os.path.exists(jobs_file):
        try:
            with open(jobs_file, 'r') as f:
                new_jobs = json.load(f)
                new_count = len(new_jobs)
        except:
            new_count = old_count
    
    added_jobs = new_count - old_count
    
    print(f"\n📈 Results:")
    print(f"   Previous jobs: {old_count}")
    print(f"   Current jobs:  {new_count}")
    print(f"   New jobs added: {added_jobs}")
    print(f"   Successful searches: {success_count}/{len(search_terms)}")
    
    if success_count > 0:
        print(f"\n✅ Daily update completed successfully!")
        print(f"🔄 Next: Push changes to git to deploy to Railway")
        print(f"   git add jobs_database.json")
        print(f"   git commit -m 'Daily job update - {datetime.now().strftime('%Y-%m-%d')}'")
        print(f"   git push")
    else:
        print(f"\n❌ No successful searches completed")
    
    return success_count > 0

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the update
    success = update_jobs_database()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)