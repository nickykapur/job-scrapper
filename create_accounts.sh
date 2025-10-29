#!/bin/bash

echo "Creating Admin account for Software Engineering jobs..."
ADMIN_RESPONSE=$(curl -s -X POST https://web-production-110bb.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@jobmanager.local",
    "password": "Admin123!",
    "full_name": "Admin User"
  }')

echo "Admin account response:"
echo $ADMIN_RESPONSE | python3 -m json.tool

# Get admin token
ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ ! -z "$ADMIN_TOKEN" ]; then
  echo -e "\n✅ Admin account created!"
  echo "Setting admin preferences for Software Engineering..."
  
  curl -s -X PUT https://web-production-110bb.up.railway.app/api/auth/preferences \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -d '{
      "job_types": ["software"],
      "keywords": ["Python", "React", "JavaScript", "Full Stack", "Backend", "Frontend"],
      "experience_levels": ["junior", "mid"],
      "preferred_countries": ["Ireland", "Spain", "Netherlands", "Germany", "Remote"],
      "exclude_senior": true,
      "excluded_keywords": ["Senior", "Lead", "Manager", "Principal"],
      "easy_apply_only": false,
      "remote_only": false
    }' | python3 -m json.tool
  echo -e "\n✅ Admin preferences set!"
fi

echo -e "\n---\n"

echo "Creating HR account for Recruitment jobs..."
HR_RESPONSE=$(curl -s -X POST https://web-production-110bb.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "hr_user",
    "email": "hr@jobmanager.local",
    "password": "HR123!",
    "full_name": "HR User"
  }')

echo "HR account response:"
echo $HR_RESPONSE | python3 -m json.tool

# Get HR token
HR_TOKEN=$(echo $HR_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ ! -z "$HR_TOKEN" ]; then
  echo -e "\n✅ HR account created!"
  echo "Setting HR preferences for Recruitment jobs..."
  
  curl -s -X PUT https://web-production-110bb.up.railway.app/api/auth/preferences \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $HR_TOKEN" \
    -d '{
      "job_types": ["hr"],
      "keywords": ["HR Officer", "Talent Acquisition", "Recruiter", "HR Coordinator", "HR Generalist"],
      "experience_levels": ["entry", "junior"],
      "preferred_countries": ["Ireland", "Remote"],
      "exclude_senior": false,
      "excluded_keywords": ["Senior", "Director", "Head of"],
      "easy_apply_only": false,
      "remote_only": false
    }' | python3 -m json.tool
  echo -e "\n✅ HR preferences set!"
fi

echo -e "\n=== ACCOUNTS CREATED ===\n"
echo "Admin Account:"
echo "  Username: admin"
echo "  Password: Admin123!"
echo "  Email: admin@jobmanager.local"
echo "  Type: Software Engineering jobs"
echo ""
echo "HR Account:"
echo "  Username: hr_user"
echo "  Password: HR123!"
echo "  Email: hr@jobmanager.local"
echo "  Type: HR/Recruitment jobs"
