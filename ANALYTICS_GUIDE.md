# Job Scraping Analytics Guide

This guide explains how to analyze your job scraping data to understand patterns and optimize your job search strategy.

## 📊 Available Analytics Tools

### 1. **analyze_scraping_stats.py** - Console Report
Generates a comprehensive text report with insights about your scraping patterns.

**Usage:**
```bash
# Analyze last 30 days (default)
python3 analyze_scraping_stats.py

# Analyze custom time period (e.g., last 7 days)
python3 analyze_scraping_stats.py 7

# Analyze last 90 days
python3 analyze_scraping_stats.py 90
```

**What it shows:**
- Daily scraping summary (total jobs per day)
- Country-level trends (which markets are most active)
- Day-of-week patterns (when are most jobs posted?)
- Detailed breakdown of scrapes per country per day
- Key insights and recommendations

### 2. **export_scraping_stats.py** - CSV Export
Exports your data to CSV files for detailed analysis in Excel/Google Sheets.

**Usage:**
```bash
python3 export_scraping_stats.py
```

**Generated files:**
1. `scraping_stats_by_country_date.csv` - Daily stats per country
2. `scraping_stats_by_weekday.csv` - Day-of-week patterns
3. `scraping_stats_country_summary.csv` - Country-level overview
4. `scraping_stats_time_series.csv` - Daily trends over time

## 🎯 What You Can Learn

### 1. **Best Days to Check for Jobs**
The day-of-week analysis shows which days companies post the most jobs:
- Monday: Typically high (companies post for the week)
- Tuesday-Wednesday: Peak posting days
- Thursday-Friday: Lower activity
- Weekend: Usually quiet

### 2. **Most Active Markets**
Country trends show which markets have:
- Highest job volume
- Best application-to-posting ratio
- Most consistent posting patterns

### 3. **Optimal Scraping Frequency**
By analyzing daily patterns, you can:
- Identify when to run your scraper for maximum results
- Avoid wasting resources on low-activity days
- Focus on high-performing markets

### 4. **Application Success Patterns**
Track which countries/days have:
- Higher application rates
- More Easy Apply opportunities
- Better job quality (less recurring, more new postings)

## 📈 Example Insights

After running the analysis, you might discover:

```
🏆 Best day for job postings: Tuesday (324 jobs)
✅ Most active market: Ireland (1,250 jobs, 42 jobs/day avg)
✅ Peak posting time: Tuesday-Wednesday (60% of weekly jobs)
📊 Application sweet spot: Ireland on Tuesdays (18% application rate)
```

## 💡 Using the Data

### For Daily Scraping Strategy:
1. **Run the console report weekly** to understand current trends
2. **Schedule scrapers** for peak days (typically Tue-Wed)
3. **Focus efforts** on countries with highest new job rates

### For Long-term Planning:
1. **Export to CSV** monthly
2. **Create charts** in Excel/Sheets:
   - Line chart: Daily job volume over time
   - Bar chart: Jobs per country comparison
   - Pie chart: Market share by country
3. **Track trends** over months to see seasonal patterns

### For Job Search Optimization:
1. Check the **day-of-week report** to know when to look for fresh jobs
2. Monitor **country trends** to know where to focus applications
3. Track **new vs recurring** ratio to gauge market freshness

## 🔄 Recommended Schedule

```bash
# Daily (quick check)
python3 analyze_scraping_stats.py 7

# Weekly (detailed insights)
python3 analyze_scraping_stats.py 30

# Monthly (export for records)
python3 export_scraping_stats.py
```

## 📊 Sample SQL Queries

If you want to run custom queries directly:

### Jobs scraped today by country:
```sql
SELECT country, COUNT(*) as jobs
FROM jobs
WHERE DATE(scraped_at) = CURRENT_DATE
GROUP BY country;
```

### Best posting day in last month:
```sql
SELECT TO_CHAR(scraped_at, 'Day') as day, COUNT(*) as jobs
FROM jobs
WHERE scraped_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY day
ORDER BY jobs DESC;
```

### Country with most new jobs this week:
```sql
SELECT country, COUNT(*) as new_jobs
FROM jobs
WHERE is_new = TRUE
  AND scraped_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY country
ORDER BY new_jobs DESC;
```

## 🚀 Pro Tips

1. **Run analytics before major scraping sessions** to know which markets to prioritize
2. **Export data monthly** to track long-term trends
3. **Compare week-over-week** to spot emerging markets
4. **Monitor application rates** to measure job quality
5. **Use day-of-week data** to time your applications (apply early on peak days)

## 🛠️ Troubleshooting

### "DATABASE_URL environment variable not set"
Make sure your Railway database URL is set:
```bash
export DATABASE_URL="your-railway-postgres-url"
```

### No data showing
- Check that jobs have been scraped recently
- Verify the `country` field is populated in your jobs table
- Try increasing the days parameter (e.g., `analyze_scraping_stats.py 90`)

### CSV files not opening correctly
- Use UTF-8 encoding when opening in Excel
- Try opening in Google Sheets first, then download as Excel

---

**Questions or issues?** Check the main README or open an issue on GitHub.
