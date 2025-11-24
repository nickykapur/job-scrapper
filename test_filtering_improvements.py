#!/usr/bin/env python3
"""
Test script to verify improved job filtering works correctly
Tests: language detection, civil/infrastructure engineer exclusion, and data jobs inclusion
"""

from linkedin_job_scraper import LinkedInJobScraper

def test_job_filtering():
    """Test the improved job filtering with various test cases"""

    print("🧪 Testing Improved Job Filtering")
    print("=" * 80)

    scraper = LinkedInJobScraper(headless=True)

    test_cases = [
        # Language detection tests
        {
            "name": "German job title",
            "title": "Softwareentwickler für Backend-Systeme",
            "should_pass": False,
            "reason": "Non-English/Spanish language"
        },
        {
            "name": "French job title",
            "title": "Développeur Full Stack avec React et Node.js",
            "should_pass": False,
            "reason": "Non-English/Spanish language"
        },
        {
            "name": "Italian job title",
            "title": "Ingegnere Software per Applicazioni Cloud",
            "should_pass": False,
            "reason": "Non-English/Spanish language"
        },
        {
            "name": "English software job",
            "title": "Senior Software Engineer - Backend Systems",
            "should_pass": True,
            "reason": "Valid English software job"
        },
        {
            "name": "Spanish software job",
            "title": "Desarrollador Full Stack - React y Node.js",
            "should_pass": True,
            "reason": "Valid Spanish software job"
        },

        # Civil/Infrastructure engineer exclusion tests
        {
            "name": "Civil Engineer",
            "title": "Civil Engineer - Infrastructure Projects",
            "should_pass": False,
            "reason": "Civil engineering (construction)"
        },
        {
            "name": "Structural Engineer",
            "title": "Senior Structural Engineer",
            "should_pass": False,
            "reason": "Structural engineering (construction)"
        },
        {
            "name": "Mechanical Engineer",
            "title": "Mechanical Engineer - Manufacturing",
            "should_pass": False,
            "reason": "Mechanical engineering"
        },
        {
            "name": "Infrastructure Project Engineer",
            "title": "Infrastructure Project Engineer - Roads and Bridges",
            "should_pass": False,
            "reason": "Infrastructure construction"
        },
        {
            "name": "Software Engineer (Infrastructure)",
            "title": "Software Engineer - Cloud Infrastructure",
            "should_pass": True,
            "reason": "Valid software infrastructure role"
        },
        {
            "name": "Infrastructure Engineer (DevOps)",
            "title": "Infrastructure Engineer - Kubernetes & AWS",
            "should_pass": True,
            "reason": "Valid cloud infrastructure role"
        },

        # Data science & data engineering inclusion tests
        {
            "name": "Data Engineer",
            "title": "Data Engineer - Python & Spark",
            "should_pass": True,
            "reason": "Valid data engineering job"
        },
        {
            "name": "Data Scientist",
            "title": "Senior Data Scientist - Machine Learning",
            "should_pass": True,
            "reason": "Valid data science job"
        },
        {
            "name": "ML Engineer",
            "title": "ML Engineer - Deep Learning & NLP",
            "should_pass": True,
            "reason": "Valid machine learning job"
        },
        {
            "name": "Data Analyst",
            "title": "Data Analyst - Business Intelligence",
            "should_pass": True,
            "reason": "Valid data analytics job"
        },
        {
            "name": "Analytics Engineer",
            "title": "Analytics Engineer - Data Warehouse & DBT",
            "should_pass": True,
            "reason": "Valid analytics engineering job"
        },
        {
            "name": "Research Scientist",
            "title": "Research Scientist - AI & Machine Learning",
            "should_pass": True,
            "reason": "Valid research scientist job"
        },
        {
            "name": "BI Analyst",
            "title": "Business Intelligence Analyst - Tableau & Power BI",
            "should_pass": True,
            "reason": "Valid BI job"
        },
        {
            "name": "MLOps Engineer",
            "title": "MLOps Engineer - Model Deployment",
            "should_pass": True,
            "reason": "Valid MLOps job"
        },
        {
            "name": "Spanish Data Scientist",
            "title": "Científico de Datos - Machine Learning",
            "should_pass": True,
            "reason": "Valid Spanish data science job"
        },

        # Edge cases
        {
            "name": "Electrical Engineer (Hardware)",
            "title": "Electrical Engineer - Circuit Design",
            "should_pass": False,
            "reason": "Hardware engineering"
        },
        {
            "name": "Software Engineer with mixed language",
            "title": "Software Engineer und Backend Developer",
            "should_pass": False,
            "reason": "Mixed language (German 'und')"
        },
    ]

    passed = 0
    failed = 0

    print("\n" + "=" * 80)
    print("RUNNING TESTS")
    print("=" * 80)

    for i, test_case in enumerate(test_cases, 1):
        result = scraper.is_software_related_job(test_case["title"])
        expected = test_case["should_pass"]

        status = "✅ PASS" if result == expected else "❌ FAIL"
        passed += 1 if result == expected else 0
        failed += 1 if result != expected else 0

        print(f"\n{i}. {test_case['name']}")
        print(f"   Title: {test_case['title']}")
        print(f"   Reason: {test_case['reason']}")
        print(f"   Expected: {'KEEP' if expected else 'FILTER OUT'}")
        print(f"   Got: {'KEEP' if result else 'FILTER OUT'}")
        print(f"   {status}")

    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)

    if failed == 0:
        print("🎉 All tests passed! Job filtering is working correctly.")
        print("\n✨ Summary of improvements:")
        print("   ✅ Language detection filters out non-English/Spanish jobs")
        print("   ✅ Civil/infrastructure engineers are excluded")
        print("   ✅ Data science & data engineering jobs are included")
    else:
        print("⚠️  Some tests failed. Please review the filter logic.")

    return failed == 0


if __name__ == "__main__":
    success = test_job_filtering()
    exit(0 if success else 1)
