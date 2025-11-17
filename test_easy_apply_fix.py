#!/usr/bin/env python3
"""
Test script to verify Easy Apply detection fix
Tests the updated scraper with Easy Apply filtering
"""
from linkedin_job_scraper import LinkedInJobScraper
import json

def test_easy_apply_fix():
    """Test that Easy Apply filtering works correctly"""

    print("="*80)
    print("Testing Easy Apply Detection Fix")
    print("="*80)

    scraper = LinkedInJobScraper(headless=True)

    try:
        # Test search parameters
        test_keyword = "Software Engineer"
        test_location = "Dublin, Ireland"

        print(f"\n1️⃣ Testing regular search (no Easy Apply filter)...")
        print(f"   Keywords: {test_keyword}")
        print(f"   Location: {test_location}\n")

        # First: Regular search
        regular_results = scraper.search_jobs(
            keywords=test_keyword,
            location=test_location,
            date_filter="24h",
            easy_apply_filter=False
        )

        regular_count = len(regular_results)
        regular_easy_apply_count = sum(1 for job in regular_results.values() if job.get('easy_apply', False))

        print(f"\n   Results:")
        print(f"   • Total jobs found: {regular_count}")
        print(f"   • Jobs with Easy Apply: {regular_easy_apply_count}")
        print(f"   • Jobs without Easy Apply: {regular_count - regular_easy_apply_count}")

        if regular_count > 0:
            print(f"\n   Sample jobs:")
            for idx, (job_id, job) in enumerate(list(regular_results.items())[:3], 1):
                easy_label = "⚡" if job.get('easy_apply') else "❌"
                print(f"   {idx}. {easy_label} {job['title']} at {job['company']}")

        print(f"\n2️⃣ Testing Easy Apply filtered search...")
        print(f"   Keywords: {test_keyword}")
        print(f"   Location: {test_location}")
        print(f"   Filter: Easy Apply ONLY\n")

        # Second: Easy Apply filtered search
        easy_apply_results = scraper.search_jobs(
            keywords=test_keyword,
            location=test_location,
            date_filter="24h",
            easy_apply_filter=True
        )

        easy_apply_count = len(easy_apply_results)
        all_marked_easy_apply = all(job.get('easy_apply', False) for job in easy_apply_results.values())

        print(f"\n   Results:")
        print(f"   • Total jobs found: {easy_apply_count}")
        print(f"   • All marked as Easy Apply: {all_marked_easy_apply}")

        if easy_apply_count > 0:
            print(f"\n   Sample Easy Apply jobs:")
            for idx, (job_id, job) in enumerate(list(easy_apply_results.items())[:3], 1):
                easy_label = "⚡" if job.get('easy_apply') else "❌"
                print(f"   {idx}. {easy_label} {job['title']} at {job['company']}")

        print(f"\n{'='*80}")
        print("Test Results Summary")
        print(f"{'='*80}")
        print(f"✅ Regular search: {regular_count} jobs")
        print(f"✅ Easy Apply search: {easy_apply_count} jobs")

        if easy_apply_count > 0 and all_marked_easy_apply:
            print(f"✅ All Easy Apply jobs correctly marked!")
        elif easy_apply_count > 0:
            print(f"❌ Some Easy Apply jobs NOT marked correctly")
        else:
            print(f"⚠️  No Easy Apply jobs found (this might be expected for some searches)")

        if regular_count > 0 and easy_apply_count > 0:
            percentage = (easy_apply_count / regular_count) * 100
            print(f"📊 Easy Apply jobs: {percentage:.1f}% of total jobs")

        print(f"\n{'='*80}")
        print("Test complete!")
        print(f"{'='*80}\n")

        # Save results to file for inspection
        test_results = {
            "regular_search": {
                "total": regular_count,
                "easy_apply": regular_easy_apply_count,
                "jobs": list(regular_results.values())[:5]  # Save first 5 for inspection
            },
            "easy_apply_search": {
                "total": easy_apply_count,
                "all_marked": all_marked_easy_apply,
                "jobs": list(easy_apply_results.values())[:5]  # Save first 5 for inspection
            }
        }

        with open('easy_apply_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)

        print("📄 Detailed results saved to: easy_apply_test_results.json\n")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()

if __name__ == "__main__":
    test_easy_apply_fix()
