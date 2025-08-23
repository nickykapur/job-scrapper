#!/usr/bin/env python3
"""
Test script to verify company exclusions and applied job tracking
"""

from linkedin_job_scraper import LinkedInJobScraper

def test_exclusions():
    """Test company exclusion functionality"""
    scraper = LinkedInJobScraper()
    
    # Test cases
    test_companies = [
        "Bending Spoons",
        "BENDING SPOONS", 
        "bending spoons",
        "Google",
        "Microsoft",
        "Stripe"
    ]
    
    print("🧪 Testing Company Exclusions:")
    print("=" * 40)
    
    for company in test_companies:
        is_excluded = scraper.is_excluded_company(company)
        status = "❌ EXCLUDED" if is_excluded else "✅ ALLOWED"
        print(f"{status}: {company}")
    
    print("\n🧪 Testing Applied Job Preservation:")
    print("=" * 40)
    
    # Create sample job data
    test_job = {
        "id": "test123",
        "title": "Software Engineer",
        "company": "Test Company",
        "applied": False,
        "is_new": True
    }
    
    # Simulate existing job with applied=True
    scraper.existing_jobs["test123"] = {
        "id": "test123", 
        "title": "Software Engineer",
        "company": "Test Company",
        "applied": True,
        "notes": "Applied via email"
    }
    
    # Test preservation
    preserved_job = scraper.preserve_applied_status("test123", test_job)
    
    print(f"Original applied status: {test_job['applied']}")
    print(f"Preserved applied status: {preserved_job['applied']}")
    print(f"Notes preserved: {'notes' in preserved_job}")
    
    if preserved_job['applied'] and 'notes' in preserved_job:
        print("✅ Applied status preservation WORKS!")
    else:
        print("❌ Applied status preservation FAILED!")

if __name__ == "__main__":
    test_exclusions()