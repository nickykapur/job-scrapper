#!/usr/bin/env python3
"""
Test script to verify job limit logic works correctly
"""

from datetime import datetime, timedelta

def limit_jobs_per_country(jobs_data, max_jobs_per_country=20, unlimited_countries=None):
    """Keep only the most recent max_jobs_per_country jobs per country"""
    if unlimited_countries is None:
        unlimited_countries = []

    jobs_by_country = {}

    # Group jobs by country
    for job_id, job_data in jobs_data.items():
        if job_id.startswith("_"):  # Skip metadata
            continue

        country = job_data.get("country", "Unknown")
        if country not in jobs_by_country:
            jobs_by_country[country] = []

        jobs_by_country[country].append((job_id, job_data))

    # Limit each country to max_jobs_per_country most recent jobs
    limited_jobs = {}
    removed_count = 0

    for country, country_jobs in jobs_by_country.items():
        # Sort by scraped_at timestamp (most recent first)
        country_jobs.sort(key=lambda x: x[1].get('scraped_at', ''), reverse=True)

        # Check if this country has unlimited jobs
        if country in unlimited_countries:
            print(f"   ♾️  {country}: No limit - keeping all {len(country_jobs)} jobs")
        elif len(country_jobs) > max_jobs_per_country:
            removed = len(country_jobs) - max_jobs_per_country
            removed_count += removed
            country_jobs = country_jobs[:max_jobs_per_country]
            print(f"   ✂️ {country}: Trimmed to {max_jobs_per_country} most recent jobs (removed {removed} old jobs)")

        # Add limited jobs back to the result
        for job_id, job_data in country_jobs:
            limited_jobs[job_id] = job_data

    if removed_count > 0:
        print(f"\n🗑️ Removed {removed_count} old jobs total (limited countries: {max_jobs_per_country} jobs each)")

    return limited_jobs


def test_job_limits():
    """Test the job limit logic with mock data"""

    print("🧪 Testing Job Limit Logic")
    print("=" * 70)

    # Create test data with different amounts of jobs per country
    test_jobs = {}
    base_time = datetime.now()

    # Ireland: 50 jobs (should keep all)
    for i in range(50):
        job_id = f"ireland_job_{i}"
        test_jobs[job_id] = {
            "title": f"Software Engineer {i}",
            "country": "Ireland",
            "scraped_at": (base_time - timedelta(hours=i)).isoformat()
        }

    # Spain: 30 jobs (should keep only 20)
    for i in range(30):
        job_id = f"spain_job_{i}"
        test_jobs[job_id] = {
            "title": f"Developer {i}",
            "country": "Spain",
            "scraped_at": (base_time - timedelta(hours=i)).isoformat()
        }

    # UK: 25 jobs (should keep only 20)
    for i in range(25):
        job_id = f"uk_job_{i}"
        test_jobs[job_id] = {
            "title": f"Engineer {i}",
            "country": "United Kingdom",
            "scraped_at": (base_time - timedelta(hours=i)).isoformat()
        }

    # Germany: 15 jobs (should keep all - under limit)
    for i in range(15):
        job_id = f"germany_job_{i}"
        test_jobs[job_id] = {
            "title": f"Entwickler {i}",
            "country": "Germany",
            "scraped_at": (base_time - timedelta(hours=i)).isoformat()
        }

    print(f"\n📊 Test Data Created:")
    print(f"   Ireland: 50 jobs")
    print(f"   Spain: 30 jobs")
    print(f"   UK: 25 jobs")
    print(f"   Germany: 15 jobs")
    print(f"   Total: {len(test_jobs)} jobs\n")

    print("=" * 70)
    print("🔧 Applying limits (20 per country, except Ireland unlimited)...")
    print("=" * 70)

    # Apply limits
    limited_jobs = limit_jobs_per_country(
        test_jobs,
        max_jobs_per_country=20,
        unlimited_countries=['Ireland']
    )

    # Count results by country
    results = {}
    for job_id, job_data in limited_jobs.items():
        country = job_data.get("country", "Unknown")
        if country not in results:
            results[country] = 0
        results[country] += 1

    print("\n" + "=" * 70)
    print("📊 Results After Limiting:")
    print("=" * 70)

    test_passed = True

    # Ireland: should have all 50
    ireland_count = results.get("Ireland", 0)
    ireland_expected = 50
    ireland_status = "✅ PASS" if ireland_count == ireland_expected else "❌ FAIL"
    if ireland_count != ireland_expected:
        test_passed = False
    print(f"   Ireland: {ireland_count} jobs (expected {ireland_expected}) {ireland_status}")

    # Spain: should have 20
    spain_count = results.get("Spain", 0)
    spain_expected = 20
    spain_status = "✅ PASS" if spain_count == spain_expected else "❌ FAIL"
    if spain_count != spain_expected:
        test_passed = False
    print(f"   Spain: {spain_count} jobs (expected {spain_expected}) {spain_status}")

    # UK: should have 20
    uk_count = results.get("United Kingdom", 0)
    uk_expected = 20
    uk_status = "✅ PASS" if uk_count == uk_expected else "❌ FAIL"
    if uk_count != uk_expected:
        test_passed = False
    print(f"   UK: {uk_count} jobs (expected {uk_expected}) {uk_status}")

    # Germany: should have all 15 (under limit)
    germany_count = results.get("Germany", 0)
    germany_expected = 15
    germany_status = "✅ PASS" if germany_count == germany_expected else "❌ FAIL"
    if germany_count != germany_expected:
        test_passed = False
    print(f"   Germany: {germany_count} jobs (expected {germany_expected}) {germany_status}")

    total_expected = 50 + 20 + 20 + 15  # 105
    total_actual = len(limited_jobs)
    print(f"\n   Total: {total_actual} jobs (expected {total_expected})")

    print("\n" + "=" * 70)

    if test_passed:
        print("🎉 All tests passed! Job limit logic is working correctly.")
        print("\n✅ Configuration Summary:")
        print("   • Ireland: Unlimited jobs ✓")
        print("   • Spain: Limited to 20 jobs ✓")
        print("   • UK: Limited to 20 jobs ✓")
        print("   • Germany: Limited to 20 jobs (under limit in this test) ✓")
    else:
        print("❌ Some tests failed. Please review the limit logic.")

    print("=" * 70)

    return test_passed


if __name__ == "__main__":
    success = test_job_limits()
    exit(0 if success else 1)
