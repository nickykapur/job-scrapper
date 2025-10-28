#!/usr/bin/env python3
"""
Test script to verify country scraping configuration
"""

from linkedin_job_scraper import LinkedInJobScraper

def test_country_filtering():
    """Test that company filtering works correctly for all countries"""

    scraper = LinkedInJobScraper(headless=True)

    print("Testing Country & Company Filtering")
    print("=" * 60)

    # Test cases: (company, country, should_pass)
    test_cases = [
        # Netherlands - should filter
        ("Google", "Netherlands", True),
        ("Booking.com", "Netherlands", True),
        ("Random Small Company", "Netherlands", False),

        # Germany - should filter
        ("SAP", "Germany", True),
        ("Zalando", "Germany", True),
        ("Unknown Startup", "Germany", False),

        # Sweden - should filter
        ("Spotify", "Sweden", True),
        ("Klarna", "Sweden", True),
        ("Local Company AB", "Sweden", False),

        # Ireland - no filtering (all pass)
        ("Google", "Ireland", True),
        ("Random Irish Company", "Ireland", True),

        # Spain - no filtering (all pass)
        ("Microsoft", "Spain", True),
        ("Small Spanish Company", "Spain", True),

        # Panama - no filtering (all pass)
        ("Any Company", "Panama", True),

        # Chile - no filtering (all pass)
        ("Any Company", "Chile", True),
    ]

    passed = 0
    failed = 0

    for company, country, expected in test_cases:
        result = scraper.is_top_tech_company(company, country)
        status = "PASS" if result == expected else "FAIL"

        if result == expected:
            passed += 1
        else:
            failed += 1

        symbol = "[OK]" if result == expected else "[ERROR]"
        print(f"{symbol} {country:15} | {company:30} | Expected: {expected:5} | Got: {result:5} | {status}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0

def test_countries_config():
    """Test that all 7 countries are configured"""

    print("\nTesting Countries Configuration")
    print("=" * 60)

    scraper = LinkedInJobScraper(headless=True)

    expected_countries = [
        'Ireland',
        'Spain',
        'Panama',
        'Chile',
        'Netherlands',
        'Germany',
        'Sweden'
    ]

    for country in expected_countries:
        if country in scraper.top_tech_companies:
            companies_count = len(scraper.top_tech_companies[country])
            filter_status = "NO FILTER" if companies_count == 0 else f"{companies_count} companies"
            print(f"[OK] {country:15} - {filter_status}")
        else:
            print(f"[ERROR] {country:15} - NOT CONFIGURED")

    print("=" * 60)

def test_daily_script_config():
    """Test that daily_multi_country_update.py has all countries"""

    print("\nTesting Daily Script Configuration")
    print("=" * 60)

    try:
        with open('daily_multi_country_update.py', 'r') as f:
            content = f.read()

        expected_locations = [
            'Dublin, County Dublin, Ireland',
            'Madrid, Community of Madrid, Spain',
            'Panama City, Panama',
            'Santiago, Chile',
            'Amsterdam, North Holland, Netherlands',
            'Berlin, Germany',
            'Stockholm, Sweden'
        ]

        for location in expected_locations:
            if location in content:
                print(f"[OK] Found: {location}")
            else:
                print(f"[ERROR] Missing: {location}")

        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] Could not read daily script: {e}")

if __name__ == "__main__":
    print("\nCountry Scraping Configuration Test")
    print("=" * 60)
    print()

    # Run tests
    test_countries_config()
    test_daily_script_config()
    all_passed = test_country_filtering()

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All tests passed! Scraper is configured correctly.")
    else:
        print("[ERROR] Some tests failed. Please review configuration.")
    print("=" * 60)
