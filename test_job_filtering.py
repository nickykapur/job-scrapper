#!/usr/bin/env python3
"""
Test job filtering against your CV to ensure you're getting relevant jobs
"""

from linkedin_job_scraper import LinkedInJobScraper

def test_job_filtering():
    """Test job filtering with jobs that were previously rejected"""
    scraper = LinkedInJobScraper()
    
    # Jobs that were being skipped but should match your CV
    test_jobs = [
        "Software Engineer, Java - Marketing Tools",
        "Full Stack Engineer, Revenue and Finance Automation", 
        "Senior Software Engineer - Java, Marketing Tools",
        "Scientist – Compiler Infrastructure",
        "Integration Reliability Engineer, Technical Operations",
        "Data Operations Engineer",
        "Salesforce Developer – nCino",
        "Lead Developer - Salesforce /nCino",
        "Principal Research Scientist",
        
        # Should definitely be included
        "Software Engineer",
        "Python Developer", 
        "React Developer",
        "Full Stack Developer",
        "Backend Engineer",
        "Frontend Developer",
        
        # Should be excluded
        "Account Manager",
        "Sales Representative", 
        "HR Manager",
        "Construction Worker",
        "Receptionist"
    ]
    
    print("🧪 Testing Job Filtering Against Your CV")
    print("=" * 60)
    print("Your skills: Python, React, Angular, Java, AWS, Data Science, Full Stack")
    print("-" * 60)
    
    included_count = 0
    excluded_count = 0
    
    for job_title in test_jobs:
        is_match = scraper.is_software_related_job(job_title)
        status = "✅ INCLUDED" if is_match else "❌ EXCLUDED"
        
        print(f"{status}: {job_title}")
        
        if is_match:
            included_count += 1
        else:
            excluded_count += 1
    
    print("-" * 60)
    print(f"📊 Results: {included_count} included, {excluded_count} excluded")
    
    # Test specific problematic cases
    print("\n🔍 Detailed Analysis of Previously Rejected Jobs:")
    print("-" * 60)
    
    problematic_jobs = [
        "Software Engineer, Java - Marketing Tools",
        "Full Stack Engineer, Revenue and Finance Automation",
        "Integration Reliability Engineer, Technical Operations"
    ]
    
    for job in problematic_jobs:
        is_match = scraper.is_software_related_job(job)
        print(f"\n📝 Job: '{job}'")
        print(f"   Match: {'YES' if is_match else 'NO'}")
        
        if is_match:
            print(f"   ✅ This job WILL be included in your searches")
        else:
            print(f"   ❌ This job is being filtered out")
            print(f"   💡 Why: Check if it contains excluded keywords or missing software keywords")

if __name__ == "__main__":
    test_job_filtering()