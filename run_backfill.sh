#!/bin/bash
# Run backfill to populate country, job_type, experience_level for existing jobs
# Run this ONCE after deploying database_models.py and railway_server.py fixes

RAILWAY_URL="https://web-production-110bb.up.railway.app"

echo "🔧 Running backfill for existing jobs..."
echo "📡 Target: $RAILWAY_URL"
echo ""

curl -X POST "$RAILWAY_URL/api/backfill-job-fields" \
  -H "Content-Type: application/json" \
  | python3 -m json.tool

echo ""
echo "✅ Backfill complete!"
echo ""
echo "Now check your frontend - you should see jobs from all 7 countries:"
echo "- Ireland"
echo "- Spain"
echo "- Panama"
echo "- Chile"
echo "- Netherlands"
echo "- Germany"
echo "- Sweden"
