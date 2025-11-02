#!/bin/bash

# Create a new software engineering user

echo "================================================"
echo "   Create New Software Engineering User"
echo "================================================"
echo ""

# Get user input
read -p "Username: " USERNAME
read -p "Full Name: " FULL_NAME
read -p "Email: " EMAIL
read -sp "Password: " PASSWORD
echo ""

# Railway URL
RAILWAY_URL="https://web-production-110bb.up.railway.app"

echo ""
echo "Creating user '$USERNAME'..."

# Register user
RESPONSE=$(curl -s -X POST "$RAILWAY_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"full_name\": \"$FULL_NAME\"
  }")

echo "Registration response:"
echo "$RESPONSE" | python3 -m json.tool

# Get token
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo ""
  echo "❌ Failed to create user. Check error above."
  exit 1
fi

echo ""
echo "✅ User created successfully!"
echo ""
echo "Setting preferences for Software Engineering jobs..."

# Set preferences
PREF_RESPONSE=$(curl -s -X PUT "$RAILWAY_URL/api/auth/preferences" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "job_types": ["software"],
    "keywords": ["Python", "React", "JavaScript", "TypeScript", "Full Stack", "Backend", "Frontend", "Node.js"],
    "experience_levels": ["entry", "junior", "mid"],
    "preferred_countries": ["Ireland", "Spain", "Netherlands", "Germany", "Panama", "Chile", "Sweden"],
    "exclude_senior": true,
    "excluded_keywords": ["Senior", "Lead", "Manager", "Principal", "Staff", "Architect"],
    "easy_apply_only": false,
    "remote_only": false
  }')

echo "$PREF_RESPONSE" | python3 -m json.tool

echo ""
echo "================================================"
echo "   ✅ Software User Created!"
echo "================================================"
echo ""
echo "  Username: $USERNAME"
echo "  Email: $EMAIL"
echo "  Password: [hidden]"
echo "  Type: Software Engineering"
echo ""
echo "  Login at: $RAILWAY_URL"
echo ""
echo "================================================"
