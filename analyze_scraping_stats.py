#!/usr/bin/env python3
"""
Scraping Statistics Analyzer
Analyzes job scraping patterns by country and date to identify:
- Daily scrape counts per country
- Peak posting days
- Country-specific trends
"""

import os
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
import asyncpg
from typing import Dict, List, Tuple


class ScrapingAnalyzer:
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")

    async def get_connection(self):
        """Get database connection"""
        return await asyncpg.connect(self.db_url)

    async def get_scrapes_per_country_per_day(self, days_back: int = 30) -> Dict:
        """Get number of jobs scraped per country per day"""
        conn = await self.get_connection()

        try:
            query = """
                SELECT
                    DATE(scraped_at) as scrape_date,
                    COALESCE(country, 'Unknown') as country,
                    COUNT(*) as job_count,
                    COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                    COUNT(*) FILTER (WHERE category = 'last_24h') as recurring_jobs
                FROM jobs
                WHERE scraped_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(scraped_at), country
                ORDER BY scrape_date DESC, country
            """ % days_back

            rows = await conn.fetch(query)

            # Organize data by date and country
            stats = defaultdict(lambda: defaultdict(dict))

            for row in rows:
                date_str = row['scrape_date'].strftime('%Y-%m-%d')
                country = row['country']
                stats[date_str][country] = {
                    'total': row['job_count'],
                    'new': row['new_jobs'],
                    'recurring': row['recurring_jobs']
                }

            return dict(stats)

        finally:
            await conn.close()

    async def get_daily_totals(self, days_back: int = 30) -> List[Tuple]:
        """Get total scrapes per day across all countries"""
        conn = await self.get_connection()

        try:
            query = """
                SELECT
                    DATE(scraped_at) as scrape_date,
                    COUNT(*) as total_jobs,
                    COUNT(DISTINCT country) as countries_count,
                    COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs_count
                FROM jobs
                WHERE scraped_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(scraped_at)
                ORDER BY scrape_date DESC
            """ % days_back

            rows = await conn.fetch(query)
            return [(
                row['scrape_date'].strftime('%Y-%m-%d'),
                row['total_jobs'],
                row['countries_count'],
                row['new_jobs_count']
            ) for row in rows]

        finally:
            await conn.close()

    async def get_country_trends(self) -> Dict:
        """Get overall trends per country"""
        conn = await self.get_connection()

        try:
            query = """
                SELECT
                    COALESCE(country, 'Unknown') as country,
                    COUNT(*) as total_jobs,
                    COUNT(DISTINCT DATE(scraped_at)) as active_days,
                    ROUND(AVG(daily_count)) as avg_per_day,
                    MAX(daily_count) as peak_day_count,
                    MIN(daily_count) as min_day_count
                FROM (
                    SELECT
                        country,
                        DATE(scraped_at) as scrape_date,
                        COUNT(*) as daily_count
                    FROM jobs
                    WHERE scraped_at >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY country, DATE(scraped_at)
                ) daily_stats
                GROUP BY country
                ORDER BY total_jobs DESC
            """

            rows = await conn.fetch(query)

            trends = {}
            for row in rows:
                trends[row['country']] = {
                    'total_jobs': row['total_jobs'],
                    'active_days': row['active_days'],
                    'avg_per_day': float(row['avg_per_day']) if row['avg_per_day'] else 0,
                    'peak_day': row['peak_day_count'],
                    'min_day': row['min_day_count']
                }

            return trends

        finally:
            await conn.close()

    async def get_day_of_week_patterns(self) -> Dict:
        """Identify which days of the week have most job postings"""
        conn = await self.get_connection()

        try:
            query = """
                SELECT
                    TO_CHAR(scraped_at, 'Day') as day_name,
                    EXTRACT(DOW FROM scraped_at) as day_number,
                    COUNT(*) as job_count,
                    COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                    COALESCE(country, 'Unknown') as country
                FROM jobs
                WHERE scraped_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY day_name, day_number, country
                ORDER BY day_number, country
            """

            rows = await conn.fetch(query)

            # Organize by day and country
            day_patterns = defaultdict(lambda: defaultdict(dict))

            for row in rows:
                day_name = row['day_name'].strip()
                country = row['country']
                day_patterns[day_name][country] = {
                    'total': row['job_count'],
                    'new': row['new_jobs'],
                    'day_number': row['day_number']
                }

            return dict(day_patterns)

        finally:
            await conn.close()

    async def print_analysis_report(self, days_back: int = 30):
        """Print comprehensive analysis report"""
        print(f"\n{'='*80}")
        print(f"📊 JOB SCRAPING ANALYTICS REPORT")
        print(f"{'='*80}")
        print(f"📅 Period: Last {days_back} days")
        print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 1. Daily totals
        print(f"\n{'─'*80}")
        print(f"📈 DAILY SCRAPING SUMMARY")
        print(f"{'─'*80}")
        daily_totals = await self.get_daily_totals(days_back)

        if daily_totals:
            print(f"\n{'Date':<15} {'Total Jobs':<15} {'Countries':<15} {'New Jobs':<15}")
            print("─" * 60)
            for date, total, countries, new_jobs in daily_totals[:10]:  # Show last 10 days
                print(f"{date:<15} {total:<15} {countries:<15} {new_jobs:<15}")
        else:
            print("❌ No data available for this period")

        # 2. Per-country trends
        print(f"\n{'─'*80}")
        print(f"🌍 COUNTRY-LEVEL TRENDS")
        print(f"{'─'*80}")
        trends = await self.get_country_trends()

        if trends:
            print(f"\n{'Country':<20} {'Total Jobs':<15} {'Avg/Day':<15} {'Peak Day':<15} {'Min Day':<15}")
            print("─" * 80)
            for country, stats in sorted(trends.items(), key=lambda x: x[1]['total_jobs'], reverse=True):
                print(f"{country:<20} {stats['total_jobs']:<15} "
                      f"{stats['avg_per_day']:<15.1f} {stats['peak_day']:<15} {stats['min_day']:<15}")
        else:
            print("❌ No country trends available")

        # 3. Day of week patterns
        print(f"\n{'─'*80}")
        print(f"📅 DAY OF WEEK PATTERNS (When are most jobs posted?)")
        print(f"{'─'*80}")
        day_patterns = await self.get_day_of_week_patterns()

        if day_patterns:
            # Calculate totals per day
            day_totals = {}
            for day_name, countries in day_patterns.items():
                total = sum(stats['total'] for stats in countries.values())
                new_total = sum(stats['new'] for stats in countries.values())
                day_num = list(countries.values())[0]['day_number']
                day_totals[day_name] = {'total': total, 'new': new_total, 'day_num': day_num}

            # Sort by day number
            sorted_days = sorted(day_totals.items(), key=lambda x: x[1]['day_num'])

            print(f"\n{'Day':<15} {'Total Jobs':<15} {'New Jobs':<15} {'% of Week':<15}")
            print("─" * 60)

            week_total = sum(d['total'] for d in day_totals.values())

            for day_name, stats in sorted_days:
                percentage = (stats['total'] / week_total * 100) if week_total > 0 else 0
                print(f"{day_name:<15} {stats['total']:<15} {stats['new']:<15} {percentage:<15.1f}%")

            # Find best days
            best_day = max(sorted_days, key=lambda x: x[1]['total'])
            print(f"\n🏆 Best day for job postings: {best_day[0].strip()} ({best_day[1]['total']} jobs)")
        else:
            print("❌ No day-of-week patterns available")

        # 4. Detailed per-country, per-day breakdown
        print(f"\n{'─'*80}")
        print(f"📋 DETAILED BREAKDOWN: Scrapes Per Country Per Day (Last 7 days)")
        print(f"{'─'*80}")

        country_day_stats = await self.get_scrapes_per_country_per_day(7)

        if country_day_stats:
            for date in sorted(country_day_stats.keys(), reverse=True):
                print(f"\n📅 {date}")
                print("─" * 60)

                countries = country_day_stats[date]
                if countries:
                    print(f"{'Country':<25} {'Total':<10} {'New':<10} {'Recurring':<10}")
                    print("─" * 55)
                    for country, stats in sorted(countries.items()):
                        print(f"{country:<25} {stats['total']:<10} {stats['new']:<10} {stats['recurring']:<10}")

                    daily_total = sum(c['total'] for c in countries.values())
                    print(f"{'TOTAL':<25} {daily_total:<10}")
                else:
                    print("   No data for this day")
        else:
            print("❌ No detailed breakdown available")

        # 5. Key insights
        print(f"\n{'─'*80}")
        print(f"💡 KEY INSIGHTS")
        print(f"{'─'*80}")

        if trends:
            top_country = max(trends.items(), key=lambda x: x[1]['total_jobs'])
            print(f"\n✅ Most active market: {top_country[0]} ({top_country[1]['total_jobs']} jobs)")
            print(f"✅ Highest daily average: {top_country[0]} ({top_country[1]['avg_per_day']:.1f} jobs/day)")

        if day_patterns and day_totals:
            best_day = max(day_totals.items(), key=lambda x: x[1]['total'])
            worst_day = min(day_totals.items(), key=lambda x: x[1]['total'])
            print(f"✅ Best posting day: {best_day[0].strip()} ({best_day[1]['total']} jobs)")
            print(f"✅ Slowest day: {worst_day[0].strip()} ({worst_day[1]['total']} jobs)")

        print(f"\n{'='*80}\n")


async def main():
    """Run the analysis"""
    try:
        analyzer = ScrapingAnalyzer()

        # Default to 30 days analysis
        days = 30

        # Check if custom days provided via command line
        import sys
        if len(sys.argv) > 1:
            try:
                days = int(sys.argv[1])
            except ValueError:
                print(f"⚠️  Invalid days parameter, using default: 30 days")

        await analyzer.print_analysis_report(days_back=days)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print(f"💡 Make sure DATABASE_URL environment variable is set")
        return 1
    except Exception as e:
        print(f"\n❌ Analysis Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
