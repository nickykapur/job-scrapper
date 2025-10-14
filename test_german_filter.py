#!/usr/bin/env python3
"""
Test script to verify German language filter works correctly
"""

import re

def filter_german_language_requirement(job_data):
    """Filter out jobs requiring proficient German language skills"""

    # Fields to check for German language requirements
    text_fields = [
        job_data.get('title', ''),
        job_data.get('company', ''),
        job_data.get('location', ''),
        job_data.get('description', ''),
        job_data.get('requirements', '')
    ]

    # Join all text fields
    combined_text = ' '.join(str(field) for field in text_fields).lower()

    # German language requirement patterns
    german_language_patterns = [
        r'\bfluent\s+(?:in\s+)?german\b',
        r'\bgerman\s+(?:language\s+)?(?:fluency|proficiency|proficient)\b',
        r'\bproficient\s+(?:in\s+)?german\b',
        r'\bnative\s+german\b',
        r'\bgerman\s+native\b',
        r'\bflie[sß]end(?:e[sn]?)?\s+deutsch\b',  # Fließend Deutsch
        r'\bdeutsch\s+(?:als\s+)?muttersprache\b',  # Deutsch als Muttersprache
        r'\bverhandlungssicher(?:e[sn]?)?\s+deutsch\b',  # Verhandlungssicher Deutsch
        r'\bsehr\s+gute\s+deutschkenntnisse\b',  # Sehr gute Deutschkenntnisse
        r'\bdeutsch\s+(?:c1|c2)\b',  # German C1/C2 level
        r'\bc[12]\s+(?:level\s+)?german\b',  # C1/C2 level German
        r'\bmust\s+(?:speak|know)\s+german\b',
        r'\bgerman\s+(?:is\s+)?(?:required|mandatory|essential)\b',
        r'\brequires?\s+german\b',
        r'\badvanced\s+german\b',
        r'\bexcellent\s+german\b',
    ]

    # Check if any German language pattern matches
    for pattern in german_language_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return False  # Filter out this job

    return True  # Keep this job (no German requirement)


def test_german_filter():
    """Test the German language filter with various job descriptions"""

    print("🧪 Testing German Language Filter")
    print("=" * 70)

    test_cases = [
        {
            "name": "Job requiring fluent German",
            "job": {
                "title": "Software Engineer",
                "description": "We are looking for a developer with fluent German skills",
                "requirements": ""
            },
            "should_pass": False
        },
        {
            "name": "Job requiring German proficiency",
            "job": {
                "title": "Backend Developer",
                "description": "German proficiency is required for this role",
                "requirements": ""
            },
            "should_pass": False
        },
        {
            "name": "Job with C1 German requirement",
            "job": {
                "title": "Full Stack Developer",
                "description": "Must have C1 level German",
                "requirements": ""
            },
            "should_pass": False
        },
        {
            "name": "Job with Fließend Deutsch requirement",
            "job": {
                "title": "Frontend Developer",
                "description": "Fließend Deutsch erforderlich",
                "requirements": ""
            },
            "should_pass": False
        },
        {
            "name": "Job with native German requirement",
            "job": {
                "title": "Python Developer",
                "description": "Native German speaker preferred",
                "requirements": ""
            },
            "should_pass": False
        },
        {
            "name": "Job mentioning Germany location only",
            "job": {
                "title": "Software Engineer",
                "description": "Work in our Berlin office in Germany",
                "location": "Berlin, Germany",
                "requirements": ""
            },
            "should_pass": True
        },
        {
            "name": "Job with English language requirement",
            "job": {
                "title": "React Developer",
                "description": "Fluent English required, German is a plus but not required",
                "requirements": ""
            },
            "should_pass": True
        },
        {
            "name": "Job with no language requirements",
            "job": {
                "title": "Node.js Developer",
                "description": "Looking for experienced backend developer",
                "requirements": "3+ years Node.js experience"
            },
            "should_pass": True
        },
        {
            "name": "Job requiring German as mandatory",
            "job": {
                "title": "Software Developer",
                "description": "German is mandatory for this position",
                "requirements": ""
            },
            "should_pass": False
        },
        {
            "name": "Job requiring excellent German",
            "job": {
                "title": "JavaScript Developer",
                "description": "Excellent German language skills needed",
                "requirements": ""
            },
            "should_pass": False
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        result = filter_german_language_requirement(test_case["job"])
        expected = test_case["should_pass"]

        status = "✅ PASS" if result == expected else "❌ FAIL"
        passed += 1 if result == expected else 0
        failed += 1 if result != expected else 0

        print(f"\n{i}. {test_case['name']}")
        print(f"   Description: {test_case['job'].get('description', 'N/A')[:60]}...")
        print(f"   Expected: {'KEEP' if expected else 'FILTER OUT'}")
        print(f"   Got: {'KEEP' if result else 'FILTER OUT'}")
        print(f"   {status}")

    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    if failed == 0:
        print("🎉 All tests passed! German language filter is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the filter patterns.")

    return failed == 0


if __name__ == "__main__":
    success = test_german_filter()
    exit(0 if success else 1)
