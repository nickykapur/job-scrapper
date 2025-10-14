#!/usr/bin/env python3
"""
Export Scraping Statistics to CSV
Exports job scraping data to CSV files for analysis in Excel/Google Sheets
"""

import os
import asyncio
import csv
from datetime import datetime
import asyncpg


class StatsExporter:
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")

    async def get_connection(self):
        """Get database connection"""
        return await asyncpg.connect(self.db_url)

    async def export_daily_country_stats(self, output_file: str = "scraping_stats_by_country_date.csv"):
        """Export daily stats per country to CSV"""
        conn = await self.get_connection()

        try:
            query = """
                SELECT
                    DATE(scraped_at) as scrape_date,
                    COALESCE(country, 'Unknown') as country,
                    COUNT(*) as total_jobs,
                    COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                    COUNT(*) FILTER (WHERE category = 'last_24h') as recurring_jobs,
                    COUNT(*) FILTER (WHERE applied = TRUE) as applied_jobs,
                    COUNT(*) FILTER (WHERE easy_apply = TRUE) as easy_apply_jobs
                FROM jobs
                WHERE scraped_at >= CURRENT_DATE - INTERVAL '90 days'
                GROUP BY DATE(scraped_at), country
                ORDER BY scrape_date DESC, country
            """

            rows = await conn.fetch(query)

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Country', 'Total Jobs', 'New Jobs',
                    'Recurring Jobs', 'Applied', 'Easy Apply Available'
                ])

                for row in rows:
                    writer.writerow([
                        row['scrape_date'].strftime('%Y-%m-%d'),
                        row['country'],
                        row['total_jobs'],
                        row['new_jobs'],
                        row['recurring_jobs'],
                        row['applied_jobs'],
                        row['easy_apply_jobs']
                    ])

            print(f"✅ Exported daily country stats to: {output_file}")
            print(f"   📊 {len(rows)} rows exported")

        finally:
            await conn.close()

    async def export_day_of_week_stats(self, output_file: str = "scraping_stats_by_weekday.csv"):
        """Export day-of-week patterns to CSV"""
        conn = await self.get_connection()

        try:
            query = """
                SELECT
                    TO_CHAR(scraped_at, 'Day') as day_name,
                    EXTRACT(DOW FROM scraped_at) as day_number,
                    COALESCE(country, 'Unknown') as country,
                    COUNT(*) as total_jobs,
                    COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                    ROUND(AVG(CASE
                        WHEN is_new THEN 1
                        ELSE 0
                    END) * 100, 2) as new_job_percentage
                FROM jobs
                WHERE scraped_at >= CURRENT_DATE - INTERVAL '90 days'
                GROUP BY day_name, day_number, country
                ORDER BY day_number, country
            """

            rows = await conn.fetch(query)

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Day of Week', 'Day Number', 'Country',
                    'Total Jobs', 'New Jobs', 'New Job %'
                ])

                for row in rows:
                    writer.writerow([
                        row['day_name'].strip(),
                        row['day_number'],
                        row['country'],
                        row['total_jobs'],
                        row['new_jobs'],
                        row['new_job_percentage']
                    ])

            print(f"✅ Exported day-of-week stats to: {output_file}")
            print(f"   📊 {len(rows)} rows exported")

        finally:
            await conn.close()

    async def export_country_summary(self, output_file: str = "scraping_stats_country_summary.csv"):
        """Export country-level summary statistics"""
        conn = await self.get_connection()

        try:
            query = """
                SELECT
                    COALESCE(country, 'Unknown') as country,
                    COUNT(*) as total_jobs,
                    COUNT(DISTINCT DATE(scraped_at)) as active_days,
                    MIN(DATE(scraped_at)) as first_scrape,
                    MAX(DATE(scraped_at)) as last_scrape,
                    ROUND(COUNT(*)::NUMERIC / COUNT(DISTINCT DATE(scraped_at)), 2) as avg_jobs_per_day,
                    COUNT(*) FILTER (WHERE is_new = TRUE) as total_new_jobs,
                    COUNT(*) FILTER (WHERE applied = TRUE) as total_applied,
                    COUNT(*) FILTER (WHERE easy_apply = TRUE) as total_easy_apply,
                    ROUND(COUNT(*) FILTER (WHERE applied = TRUE)::NUMERIC / COUNT(*) * 100, 2) as application_rate
                FROM jobs
                WHERE scraped_at >= CURRENT_DATE - INTERVAL '90 days'
                GROUP BY country
                ORDER BY total_jobs DESC
            """

            rows = await conn.fetch(query)

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Country', 'Total Jobs', 'Active Days', 'First Scrape',
                    'Last Scrape', 'Avg Jobs/Day', 'New Jobs',
                    'Applied', 'Easy Apply Available', 'Application Rate %'
                ])

                for row in rows:
                    writer.writerow([
                        row['country'],
                        row['total_jobs'],
                        row['active_days'],
                        row['first_scrape'].strftime('%Y-%m-%d'),
                        row['last_scrape'].strftime('%Y-%m-%d'),
                        row['avg_jobs_per_day'],
                        row['total_new_jobs'],
                        row['total_applied'],
                        row['total_easy_apply'],
                        row['application_rate']
                    ])

            print(f"✅ Exported country summary to: {output_file}")
            print(f"   📊 {len(rows)} countries included")

        finally:
            await conn.close()

    async def export_time_series(self, output_file: str = "scraping_stats_time_series.csv"):
        """Export time series data for trend analysis"""
        conn = await self.get_connection()

        try:
            query = """
                SELECT
                    DATE(scraped_at) as scrape_date,
                    COUNT(*) as total_jobs,
                    COUNT(DISTINCT country) as countries_active,
                    COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                    COUNT(*) FILTER (WHERE applied = TRUE) as applied_jobs,
                    ROUND(COUNT(*) FILTER (WHERE applied = TRUE)::NUMERIC / COUNT(*) * 100, 2) as application_rate,
                    TO_CHAR(scraped_at, 'Day') as day_of_week
                FROM jobs
                WHERE scraped_at >= CURRENT_DATE - INTERVAL '90 days'
                GROUP BY DATE(scraped_at), TO_CHAR(scraped_at, 'Day')
                ORDER BY scrape_date
            """

            rows = await conn.fetch(query)

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Total Jobs', 'Countries Active', 'New Jobs',
                    'Applied', 'Application Rate %', 'Day of Week'
                ])

                for row in rows:
                    writer.writerow([
                        row['scrape_date'].strftime('%Y-%m-%d'),
                        row['total_jobs'],
                        row['countries_active'],
                        row['new_jobs'],
                        row['applied_jobs'],
                        row['application_rate'],
                        row['day_of_week'].strip()
                    ])

            print(f"✅ Exported time series to: {output_file}")
            print(f"   📊 {len(rows)} days of data")

        finally:
            await conn.close()


async def main():
    """Export all statistics"""
    print("\n" + "="*60)
    print("📊 EXPORTING SCRAPING STATISTICS TO CSV")
    print("="*60)
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        exporter = StatsExporter()

        # Export all stats
        await exporter.export_daily_country_stats()
        await exporter.export_day_of_week_stats()
        await exporter.export_country_summary()
        await exporter.export_time_series()

        print("\n" + "="*60)
        print("✅ ALL EXPORTS COMPLETED!")
        print("="*60)
        print("\n📁 Generated files:")
        print("   1. scraping_stats_by_country_date.csv - Daily stats per country")
        print("   2. scraping_stats_by_weekday.csv - Day-of-week patterns")
        print("   3. scraping_stats_country_summary.csv - Country-level overview")
        print("   4. scraping_stats_time_series.csv - Daily trends over time")
        print("\n💡 Import these into Excel/Google Sheets for visualization!")
        print("   Recommended charts:")
        print("   - Line chart: Time series data to see trends")
        print("   - Bar chart: Day-of-week to find best posting days")
        print("   - Pie chart: Country distribution")
        print()

        return 0

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print(f"💡 Make sure DATABASE_URL environment variable is set")
        return 1
    except Exception as e:
        print(f"\n❌ Export Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
