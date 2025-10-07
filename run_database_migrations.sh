#!/bin/bash
# Database Migration Script
# Adds easy_apply column and cleans up to 300 jobs per country

set -e  # Exit on error

echo "=========================================="
echo "🔧 Job Scraper Database Migrations"
echo "=========================================="
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable not set"
    echo ""
    echo "Set it with:"
    echo "  export DATABASE_URL='your_railway_postgres_url'"
    echo ""
    exit 1
fi

echo "✅ DATABASE_URL is set"
echo ""

# Step 1: Add easy_apply column
echo "📝 Step 1: Adding easy_apply column..."
echo "----------------------------------------"
if psql "$DATABASE_URL" -f add_easy_apply_column.sql; then
    echo "✅ easy_apply column added successfully"
else
    echo "⚠️  Column might already exist (this is OK)"
fi
echo ""

# Step 2: Clean up to 300 jobs per country
echo "🧹 Step 2: Cleaning up old jobs (300 limit per country)..."
echo "----------------------------------------"
echo "Current counts:"
echo "  - UK: 1000+ jobs → will keep 300 newest"
echo "  - Spain: 900 jobs → will keep 300 newest"
echo "  - Germany: 310 jobs → will keep 300 newest"
echo ""
read -p "⚠️  This will DELETE old jobs. Continue? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if psql "$DATABASE_URL" -f cleanup_database_300_limit.sql; then
        echo "✅ Database cleaned successfully"
    else
        echo "❌ Cleanup failed"
        exit 1
    fi
else
    echo "❌ Cleanup cancelled"
    exit 1
fi
echo ""

# Step 3: Verify
echo "🔍 Step 3: Verification..."
echo "----------------------------------------"
psql "$DATABASE_URL" -c "
    SELECT
        country,
        COUNT(*) as job_count,
        COUNT(*) FILTER (WHERE easy_apply = true) as easy_apply_jobs
    FROM jobs
    WHERE country IS NOT NULL
    GROUP BY country
    ORDER BY job_count DESC;
"
echo ""

echo "=========================================="
echo "🎉 Migration Complete!"
echo "=========================================="
echo ""
echo "✅ Next steps:"
echo "  1. Wait for next scraper run (or trigger manually)"
echo "  2. Check logs for: ⚡ Easy Apply: X"
echo "  3. Rebuild frontend: cd job-manager-ui && npm run build"
echo "  4. Verify in UI: Look for ⚡ Easy Apply badges"
echo ""
