#!/usr/bin/env python3
"""
Cleanup script to remove trailing numbers from company names in the database.
This fixes entries like "Stripe 4342327281" to "Stripe"
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import re

def clean_company_name(company):
    """
    Clean company name by removing trailing numbers and extra metadata.
    LinkedIn sometimes appends tracking numbers like "Stripe 4342327281"
    """
    if not company:
        return company

    # Remove leading/trailing whitespace
    company = company.strip()

    # Pattern: Remove trailing space followed by numbers (e.g., " 4342327281")
    # This regex matches a space followed by 4 or more consecutive digits at the end
    cleaned = re.sub(r'\s+\d{4,}$', '', company)

    return cleaned.strip()

def cleanup_company_names(database_url):
    """Clean up all company names in the database"""

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("🔍 Fetching all unique company names...")

        # Get all unique company names
        cursor.execute("SELECT DISTINCT company FROM jobs WHERE company IS NOT NULL")
        companies = cursor.fetchall()

        print(f"📊 Found {len(companies)} unique company names")

        # Track changes
        cleaned_count = 0
        changes = []

        for row in companies:
            original = row['company']
            cleaned = clean_company_name(original)

            if original != cleaned:
                changes.append({
                    'original': original,
                    'cleaned': cleaned
                })
                cleaned_count += 1

        if cleaned_count == 0:
            print("✅ All company names are already clean!")
            return

        print(f"\n🧹 Found {cleaned_count} company names to clean:")
        for change in changes[:10]:  # Show first 10
            print(f"   '{change['original']}' → '{change['cleaned']}'")

        if len(changes) > 10:
            print(f"   ... and {len(changes) - 10} more")

        # Ask for confirmation
        print(f"\n⚠️  This will update all jobs with these company names.")
        response = input("Continue? (yes/no): ")

        if response.lower() != 'yes':
            print("❌ Cleanup cancelled")
            return

        # Perform cleanup
        print("\n🔄 Cleaning company names...")
        updated_jobs = 0

        for change in changes:
            cursor.execute(
                "UPDATE jobs SET company = %s WHERE company = %s",
                (change['cleaned'], change['original'])
            )
            updated_jobs += cursor.rowcount

        # Commit changes
        conn.commit()

        print(f"\n✅ Cleanup complete!")
        print(f"   📊 Updated {updated_jobs} job entries")
        print(f"   🏢 Cleaned {cleaned_count} company names")

        # Show final stats
        cursor.execute("SELECT DISTINCT company FROM jobs WHERE company LIKE '% %' AND company ~ '\\d{4,}$'")
        remaining = cursor.fetchall()

        if len(remaining) > 0:
            print(f"\n⚠️  Warning: {len(remaining)} company names still have trailing numbers:")
            for row in remaining[:5]:
                print(f"   {row['company']}")
        else:
            print("\n✅ No company names with trailing numbers found!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        # Try constructing from individual components
        database_url = "postgresql://postgres:JcWFAlWypXvRisiQPVlOlGVFEIRgsgxl@switchback.proxy.rlwy.net:22276/railway"

    if not database_url:
        print("❌ Error: DATABASE_URL not set")
        exit(1)

    cleanup_company_names(database_url)
