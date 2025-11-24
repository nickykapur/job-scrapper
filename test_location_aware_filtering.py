#!/usr/bin/env python3
"""
Test script to verify location-aware language filtering
Tests that Spanish jobs are only accepted in Spanish-speaking countries
"""

from linkedin_job_scraper import LinkedInJobScraper

def test_location_aware_filtering():
    """Test location-aware language filtering"""

    print("🧪 Testing Location-Aware Language Filtering")
    print("=" * 80)

    scraper = LinkedInJobScraper(headless=True)

    test_cases = [
        # Spanish jobs in Spanish-speaking countries (SHOULD PASS)
        {
            "name": "Spanish job in Spain",
            "title": "Desarrollador Full Stack - React y Node.js",
            "location": "Madrid, Spain",
            "should_pass": True,
            "reason": "Spanish is acceptable in Spain"
        },
        {
            "name": "Spanish job in Barcelona",
            "title": "Ingeniero de Software - Backend",
            "location": "Barcelona, España",
            "should_pass": True,
            "reason": "Spanish is acceptable in Spain"
        },
        {
            "name": "Spanish job in Chile",
            "title": "Desarrollador Python - Machine Learning",
            "location": "Santiago, Chile",
            "should_pass": True,
            "reason": "Spanish is acceptable in Chile"
        },
        {
            "name": "Spanish job in Panama",
            "title": "Programador Full Stack",
            "location": "Panama City, Panama",
            "should_pass": True,
            "reason": "Spanish is acceptable in Panama"
        },

        # Spanish jobs in NON-Spanish-speaking countries (SHOULD FAIL)
        {
            "name": "Spanish job in Ireland",
            "title": "Desarrollador Full Stack - React y Node.js",
            "location": "Dublin, Ireland",
            "should_pass": False,
            "reason": "Spanish not acceptable in Ireland"
        },
        {
            "name": "Spanish job in Netherlands",
            "title": "Ingeniero de Software Backend",
            "location": "Amsterdam, Netherlands",
            "should_pass": False,
            "reason": "Spanish not acceptable in Netherlands"
        },
        {
            "name": "Spanish job in Germany",
            "title": "Desarrollador Python Senior",
            "location": "Berlin, Germany",
            "should_pass": False,
            "reason": "Spanish not acceptable in Germany"
        },
        {
            "name": "Spanish data scientist in Sweden",
            "title": "Científico de Datos - Machine Learning",
            "location": "Stockholm, Sweden",
            "should_pass": False,
            "reason": "Spanish not acceptable in Sweden"
        },

        # English jobs (SHOULD PASS everywhere)
        {
            "name": "English job in Ireland",
            "title": "Senior Software Engineer - Backend",
            "location": "Dublin, Ireland",
            "should_pass": True,
            "reason": "English is acceptable everywhere"
        },
        {
            "name": "English job in Netherlands",
            "title": "Data Engineer - Python & Spark",
            "location": "Amsterdam, Netherlands",
            "should_pass": True,
            "reason": "English is acceptable everywhere"
        },
        {
            "name": "English job in Spain",
            "title": "Senior Data Scientist - Machine Learning",
            "location": "Madrid, Spain",
            "should_pass": True,
            "reason": "English is acceptable in Spain too"
        },
        {
            "name": "English job in Germany",
            "title": "ML Engineer - Deep Learning",
            "location": "Berlin, Germany",
            "should_pass": True,
            "reason": "English is acceptable everywhere"
        },

        # German jobs (SHOULD FAIL everywhere)
        {
            "name": "German job in Germany",
            "title": "Softwareentwickler Backend Systeme",
            "location": "Berlin, Germany",
            "should_pass": False,
            "reason": "German not acceptable"
        },

        # French jobs (SHOULD FAIL everywhere)
        {
            "name": "French job in France",
            "title": "Développeur Full Stack avec React",
            "location": "Paris, France",
            "should_pass": False,
            "reason": "French not acceptable"
        },
    ]

    passed = 0
    failed = 0

    print("\n" + "=" * 80)
    print("RUNNING TESTS")
    print("=" * 80)

    for i, test_case in enumerate(test_cases, 1):
        result = scraper.is_software_related_job(test_case["title"], test_case["location"])
        expected = test_case["should_pass"]

        status = "✅ PASS" if result == expected else "❌ FAIL"
        passed += 1 if result == expected else 0
        failed += 1 if result != expected else 0

        print(f"\n{i}. {test_case['name']}")
        print(f"   Title: {test_case['title']}")
        print(f"   Location: {test_case['location']}")
        print(f"   Reason: {test_case['reason']}")
        print(f"   Expected: {'KEEP' if expected else 'FILTER OUT'}")
        print(f"   Got: {'KEEP' if result else 'FILTER OUT'}")
        print(f"   {status}")

    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)

    if failed == 0:
        print("🎉 All tests passed! Location-aware filtering is working correctly.")
        print("\n✨ Summary:")
        print("   ✅ Spanish jobs accepted in Spain, Panama, and Chile")
        print("   ✅ Spanish jobs rejected in Ireland, Netherlands, Germany, Sweden")
        print("   ✅ English jobs accepted everywhere")
        print("   ✅ German and French jobs rejected everywhere")
    else:
        print("⚠️  Some tests failed. Please review the filter logic.")

    return failed == 0


if __name__ == "__main__":
    success = test_location_aware_filtering()
    exit(0 if success else 1)
