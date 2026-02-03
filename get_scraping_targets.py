#!/usr/bin/env python3
"""
Get scraping targets based on active users' preferences
This script queries the API to determine which job types and countries need scraping
"""

import os
import sys
import json
import requests

def get_scraping_targets():
    """Get job types and countries to scrape from active users"""

    # API base URL (default to Railway production URL)
    api_base_url = os.environ.get('API_BASE_URL', 'https://web-production-110bb.up.railway.app')

    try:
        # Call the scraping targets endpoint
        response = requests.get(
            f'{api_base_url}/api/admin/scraping-targets',
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        if not data.get('success'):
            print("[ERROR] API returned unsuccessful response", file=sys.stderr)
            return None

        active_users_count = data.get('active_users_count', 0)
        job_types = data.get('job_types', [])
        countries = data.get('countries', [])
        scraping_needed = data.get('scraping_needed', False)

        print(f"[INFO] Active users: {active_users_count}", file=sys.stderr)
        print(f"[INFO] Job types needed: {', '.join(job_types)}", file=sys.stderr)
        print(f"[INFO] Countries needed: {', '.join(countries)}", file=sys.stderr)

        # If no active users or no scraping needed, return empty lists
        if active_users_count == 0 or not scraping_needed:
            print("[WARNING] No active users or no scraping needed - skipping scraping", file=sys.stderr)
            return {
                'skip_scraping': True,
                'reason': 'No active users',
                'countries': [],
                'job_types': []
            }

        # Map job types to search terms
        job_type_configs = {
            'software': {
                'search_terms': ['Python Developer', 'React Developer', 'Full Stack Developer', 'Backend Developer', 'Frontend Developer'],
                'enabled': 'software' in job_types
            },
            'hr': {
                'search_terms': ['HR Manager', 'Recruiter', 'Talent Acquisition', 'People Operations'],
                'enabled': 'hr' in job_types
            },
            'cybersecurity': {
                'search_terms': ['Security Analyst', 'SOC Analyst', 'Cybersecurity Engineer'],
                'enabled': 'cybersecurity' in job_types
            },
            'sales': {
                'search_terms': ['Sales Manager', 'Account Executive', 'Business Development'],
                'enabled': 'sales' in job_types
            },
            'finance': {
                'search_terms': ['Financial Analyst', 'Accountant', 'Finance Manager'],
                'enabled': 'finance' in job_types
            },
            'marketing': {
                'search_terms': ['Digital Marketing Manager', 'Marketing Executive', 'Social Media Manager', 'SEO Specialist', 'Content Marketing'],
                'enabled': 'marketing' in job_types or 'digital_marketing' in job_types
            },
            'biotech': {
                'search_terms': ['Research Scientist', 'Scientist', 'Research Associate', 'Cell Culture Scientist', 'Molecular Biologist', 'Gene Therapy', 'CRISPR', 'Biotechnology', 'Lab Scientist', 'R&D Scientist'],
                'enabled': 'biotech' in job_types or 'life_sciences' in job_types
            },
            'engineering': {
                'search_terms': ['Mechanical Engineer', 'Manufacturing Engineer', 'Industrial Engineer', 'Process Engineer', 'Aerospace Engineer', 'Design Engineer', 'Production Engineer', 'Quality Engineer'],
                'enabled': 'engineering' in job_types or 'manufacturing' in job_types or 'mechanical' in job_types
            },
            'events': {
                'search_terms': ['Event Manager', 'Event Coordinator', 'Event Executive', 'Conference Manager', 'Wedding Planner', 'Hospitality Manager', 'Meeting Planner', 'Event Planner'],
                'enabled': 'events' in job_types or 'hospitality' in job_types or 'event_management' in job_types
            }
        }

        # Map country names to scraping locations
        country_locations = {
            'Ireland': 'Dublin, County Dublin, Ireland',
            'Spain': 'Madrid, Community of Madrid, Spain',
            'Panama': 'Panama City, Panama',
            'Chile': 'Santiago, Santiago Metropolitan Region, Chile',
            'Netherlands': 'Amsterdam, North Holland, Netherlands',
            'Germany': 'Berlin, Germany',
            'Sweden': 'Stockholm, Stockholm County, Sweden',
            'Belgium': 'Brussels, Belgium',
            'Denmark': 'Copenhagen, Capital Region of Denmark, Denmark',
            'Luxembourg': 'Luxembourg City, Luxembourg',
            'Switzerland': 'Basel, Switzerland',
            'United States': 'United States'
        }

        # Build countries list to scrape
        countries_to_scrape = []
        for country in countries:
            if country in country_locations:
                countries_to_scrape.append({
                    'name': country,
                    'location': country_locations[country]
                })

        # Build job types list to scrape
        job_types_to_scrape = []
        for job_type, config in job_type_configs.items():
            if config['enabled']:
                job_types_to_scrape.append({
                    'type': job_type,
                    'search_terms': config['search_terms']
                })

        result = {
            'skip_scraping': False,
            'active_users_count': active_users_count,
            'countries': countries_to_scrape,
            'job_types': job_types_to_scrape,
            'total_combinations': len(countries_to_scrape) * len(job_types_to_scrape)
        }

        print(f"[INFO] Will scrape {result['total_combinations']} combinations (countries × job types)", file=sys.stderr)

        return result

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to get scraping targets from API: {e}", file=sys.stderr)
        print("[WARNING] Falling back to default configuration", file=sys.stderr)

        # Fallback to default configuration if API fails
        return {
            'skip_scraping': False,
            'active_users_count': 'unknown',
            'countries': [
                {'name': 'Ireland', 'location': 'Dublin, County Dublin, Ireland'}
            ],
            'job_types': [
                {'type': 'software', 'search_terms': ['Python Developer', 'React Developer']}
            ],
            'total_combinations': 1,
            'fallback': True
        }

def main():
    """Main entry point"""
    targets = get_scraping_targets()

    if targets is None:
        print("[ERROR] Failed to get scraping targets", file=sys.stderr)
        sys.exit(1)

    # Output JSON for GitHub Actions to consume
    print(json.dumps(targets, indent=2))

    # Exit with code 0 if scraping needed, code 2 if should skip
    if targets.get('skip_scraping'):
        print("[INFO] Exiting with code 2 to signal scraping should be skipped", file=sys.stderr)
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
