#!/usr/bin/env python3

import argparse
import sys
import json
from linkedin_job_scraper import LinkedInJobScraper


def search_jobs(args):
    """Search for jobs"""
    # Determine headless mode
    headless = args.headless and not args.show_browser
    
    print(f"🔍 Searching for '{args.keywords}' jobs in '{args.location or 'All locations'}'")
    print(f"⏰ Looking for jobs posted in the last 7 days")
    print(f"🌐 Browser mode: {'Headless' if headless else 'Visible'}")
    print("-" * 50)
    
    # Initialize scraper
    scraper = LinkedInJobScraper(headless=headless)
    
    try:
        # Search for jobs
        jobs = scraper.search_jobs(
            keywords=args.keywords,
            location=args.location,
            date_filter="7d"
        )
        
        # Display results
        scraper.print_jobs_summary()
        
        # Save to file
        if jobs:
            scraper.save_jobs_to_file(args.output)
            print(f"\n✅ Results saved to {args.output}")
        else:
            print("\n❌ No jobs found matching your criteria")
            
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        sys.exit(1)
        
    finally:
        # Clean up
        scraper.close()


def apply_to_job(job_id):
    """Mark a job as applied"""
    scraper = LinkedInJobScraper()
    if scraper.mark_job_as_applied(job_id):
        print(f"✅ Marked job {job_id} as applied")
    else:
        print(f"❌ Job {job_id} not found")


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Job Bot - Search and track job applications")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for jobs')
    search_parser.add_argument("keywords", help="Job search keywords (e.g., 'Python Developer', 'Data Scientist')")
    search_parser.add_argument("-l", "--location", default="Dublin, County Dublin, Ireland", help="Job location (e.g., 'New York', 'Remote')")
    search_parser.add_argument("-o", "--output", default="linkedin_jobs.json", help="Output file name (default: linkedin_jobs.json)")
    search_parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode (default: True)")
    search_parser.add_argument("--show-browser", action="store_true", help="Show browser window (opposite of headless)")
    
    # Apply command
    apply_parser = subparsers.add_parser('apply', help='Mark a job as applied')
    apply_parser.add_argument("job_id", help="Job ID to mark as applied")
    
    # For backward compatibility, if no subcommand is used, treat as search
    args, unknown = parser.parse_known_args()
    
    if args.command is None:
        # Backward compatibility: treat first argument as keywords
        if unknown:
            search_parser = argparse.ArgumentParser()
            search_parser.add_argument("keywords", help="Job search keywords")
            search_parser.add_argument("-l", "--location", default="Dublin, County Dublin, Ireland")
            search_parser.add_argument("-o", "--output", default="linkedin_jobs.json")
            search_parser.add_argument("--headless", action="store_true", default=True)
            search_parser.add_argument("--show-browser", action="store_true")
            
            search_args = search_parser.parse_args(unknown)
            search_jobs(search_args)
        else:
            parser.print_help()
    elif args.command == 'search':
        search_jobs(args)
    elif args.command == 'apply':
        apply_to_job(args.job_id)
    
    print("\n🔚 Bot finished")


if __name__ == "__main__":
    main()