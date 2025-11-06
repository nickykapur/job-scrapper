#!/bin/bash
# Script to trigger the deduplication migration on Railway

RAILWAY_URL="${RAILWAY_URL:-https://web-production-110bb.up.railway.app}"

echo "🚀 Triggering deduplication migration on Railway..."
echo "📍 Server: $RAILWAY_URL"
echo ""

response=$(curl -s -X POST "$RAILWAY_URL/api/admin/run-deduplication-migration" \
  -H "Content-Type: application/json")

echo "📨 Response:"
echo "$response" | python3 -m json.tool

# Check if successful
if echo "$response" | grep -q '"success": true'; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    echo "🎯 What's next:"
    echo "   - Your scraper will now automatically skip reposted jobs"
    echo "   - Jobs are tracked for 30 days after you apply"
    echo "   - Check logs during next scraping run for '⏭️ Skipped X reposted jobs'"
else
    echo ""
    echo "❌ Migration failed. Check the response above for details."
    exit 1
fi
