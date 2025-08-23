#!/usr/bin/env python3
"""
Sync jobs from local scraper to Railway database
Run this after your local daily_dublin_update.py completes
"""

import json
import requests
import os
import sys
from datetime import datetime

def load_local_jobs():
    """Load jobs from local JSON file"""
    jobs_file = "jobs_database.json"
    if not os.path.exists(jobs_file):
        print("❌ No local jobs database found. Run daily_dublin_update.py first.")
        return None
    
    try:
        with open(jobs_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading local jobs: {e}")
        return None

def sync_to_railway(jobs_data, railway_url=None):
    """Sync jobs to Railway database"""
    if not railway_url:
        # Try to get Railway URL from environment or use default
        railway_url = os.environ.get('RAILWAY_URL', 'https://your-app.railway.app')
        
    if railway_url == 'https://your-app.railway.app':
        print("⚠️ Please set your Railway URL:")
        print("   Option 1: Set environment variable: export RAILWAY_URL=https://your-app.railway.app")
        print("   Option 2: Pass it as argument: python sync_to_railway.py https://your-app.railway.app")
        return False
    
    sync_url = f"{railway_url}/sync_jobs"
    
    try:
        print(f"🚀 Syncing {len([k for k in jobs_data.keys() if not k.startswith('_')])} jobs to Railway...")
        print(f"📡 URL: {sync_url}")
        
        response = requests.post(
            sync_url,
            json={"jobs_data": jobs_data},
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sync successful!")
            print(f"   📊 New jobs: {result.get('new_jobs', 0)}")
            print(f"   🔄 Updated jobs: {result.get('updated_jobs', 0)}")
            print(f"   💬 Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Sync failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Sync error: {e}")
        return False

def main():
    """Main function"""
    print("🔄 LinkedIn Job Manager - Railway Sync")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Get Railway URL from command line argument if provided
    railway_url = None
    if len(sys.argv) > 1:
        railway_url = sys.argv[1]
        if not railway_url.startswith('http'):
            railway_url = f"https://{railway_url}"
    
    # Load local jobs
    jobs_data = load_local_jobs()
    if not jobs_data:
        sys.exit(1)
    
    total_jobs = len([k for k in jobs_data.keys() if not k.startswith("_")])
    applied_jobs = len([j for k, j in jobs_data.items() if not k.startswith("_") and j.get("applied", False)])
    
    print(f"📊 Local database stats:")
    print(f"   📋 Total jobs: {total_jobs}")
    print(f"   ✅ Applied jobs: {applied_jobs}")
    print(f"   📝 New jobs: {len([j for k, j in jobs_data.items() if not k.startswith('_') and j.get('is_new', False)])}")
    
    # Sync to Railway
    success = sync_to_railway(jobs_data, railway_url)
    
    if success:
        print("\n🎉 Sync completed successfully!")
        print("📱 Check your Railway app to see the updated jobs")
        print("💡 Your applied job statuses are now preserved in the cloud!")
    else:
        print("\n❌ Sync failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()