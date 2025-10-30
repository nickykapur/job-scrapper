#!/bin/bash
# Run database migration to add missing columns

RAILWAY_URL="https://web-production-110bb.up.railway.app"

echo "🔧 Running database migration..."
echo "📡 Target: $RAILWAY_URL"

curl -X POST "$RAILWAY_URL/api/migrate-schema" \
  -H "Content-Type: application/json" \
  | python3 -m json.tool

echo ""
echo "✅ Migration complete!"
echo ""
echo "Now you can run the scraper: python daily_multi_country_update.py"
