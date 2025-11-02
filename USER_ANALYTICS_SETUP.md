# User Analytics & Multi-User Setup

Track user engagement and activity with automatic Slack reports!

---

## 📊 What You Get

**Daily analytics report sent to Slack at 8 AM Dublin time:**

```
📊 Daily User Analytics Report
Date: 2025-01-15

👥 User Stats

💻 admin (Software)
    • Applied: 45 | Rejected: 12 | Saved: 8
    • Last login: 2 hours ago

💻 john_doe (Software)
    • Applied: 23 | Rejected: 5 | Saved: 3
    • Last login: 1 day ago

💼 hr_user (HR)
    • Applied: 67 | Rejected: 20 | Saved: 15
    • Last login: 30 minutes ago

━━━━━━━━━━━━━━━━━━━━━━━━

🔥 Recent Activity (Last 24h)

• admin: 3 applied, 1 rejected
• john_doe: 5 applied, 2 rejected

━━━━━━━━━━━━━━━━━━━━━━━━

📊 Job Database Stats

💼 Total Jobs: 2,100
💻 Software: 1,250
🤝 HR: 850

🇮🇪 Ireland: 300
🇪🇸 Spain: 300
...
```

---

## 🚀 Setup (Already Done!)

The analytics system is already configured and will:
- ✅ Run automatically every day at 8 AM
- ✅ Track user logins, jobs applied, rejected, saved
- ✅ Send beautiful reports to your Slack channel
- ✅ Show 24-hour activity highlights

---

## 👤 Creating New Users

### Quick Method: Interactive Script

```bash
./create_software_user.sh
```

**Prompts you for:**
- Username
- Full Name
- Email
- Password

**Automatically sets up:**
- Software engineering job preferences
- Junior/Mid level filtering
- All 7 countries enabled
- Excludes senior positions

### Manual Method: API

```bash
# 1. Register
curl -X POST https://web-production-110bb.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_user",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "New User"
  }'

# 2. Set preferences (use token from registration)
curl -X PUT https://web-production-110bb.up.railway.app/api/auth/preferences \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "job_types": ["software"],
    "keywords": ["Python", "React", "JavaScript"],
    "experience_levels": ["junior", "mid"]
  }'
```

---

## 🎯 Per-User Job Interactions

**IMPORTANT:** Job applied/rejected status is tracked **per user**.

### How It Works

- ✅ Each user has their own applied/rejected/saved lists
- ✅ User A applies to a job → User B still sees it
- ✅ User B rejects a job → User A's view is unaffected
- ✅ Complete isolation between users

### Database Schema

```sql
user_job_interactions
├── user_id (unique per user)
├── job_id
├── applied (true/false)
├── rejected (true/false)
├── saved (true/false)
└── UNIQUE(user_id, job_id)
```

---

## 📈 Analytics Tracked

### Per User
- Total jobs applied
- Total jobs rejected
- Total jobs saved
- Last login time
- Last interaction time

### System-Wide
- Total jobs in database
- Jobs by country (7 countries)
- Jobs by type (software vs HR)
- Recent activity (last 24 hours)

---

## 🔧 Triggering Analytics Manually

### Via GitHub Actions
1. Go to: https://github.com/YOUR_USERNAME/job-scrapper/actions
2. Click "Daily User Analytics"
3. Click "Run workflow"
4. Check Slack in ~30 seconds

### Via Command Line
```bash
# Set environment variables
export DATABASE_URL="your_database_url"
export SLACK_WEBHOOK_URL="your_webhook_url"

# Run script
python send_analytics_to_slack.py
```

---

## 📅 Schedule

**Daily Analytics:** 8 AM Dublin time
**Job Scraping:** 7 times/day (9 AM, 11 AM, 1 PM, 3 PM, 4 PM, 6 PM, 8 PM)

---

## 🔒 Privacy & Security

- ✅ Passwords are hashed (bcrypt)
- ✅ Analytics only visible in your private Slack
- ✅ Each user sees only their own interactions
- ✅ No user data shared between accounts
- ✅ Database URL stored securely in GitHub Secrets

---

## 📋 Current Users

Run this to see all users:

```bash
curl -s "https://web-production-110bb.up.railway.app/api/auth/users" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## ❓ Troubleshooting

### Analytics not sending

1. **Check GitHub Actions:**
   ```
   https://github.com/YOUR_USERNAME/job-scrapper/actions
   ```

2. **Check Secrets are set:**
   - `DATABASE_URL` ✅
   - `SLACK_WEBHOOK_URL` ✅

3. **Test Slack webhook:**
   ```bash
   curl -X POST "YOUR_WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -d '{"text":"Test message"}'
   ```

### User can't see jobs

**Issue:** Applied status is shared between users?
**Solution:** This is already fixed! Applied status is per-user in `user_job_interactions` table.

**Verify:**
```sql
SELECT * FROM user_job_interactions
WHERE job_id = 'some_job_id';
```

You should see separate rows for each user.

---

## 💡 Tips

1. **Create separate users for different team members**
   - Each gets their own applied/rejected/saved lists
   - No interference between users

2. **Use analytics to track engagement**
   - See who's actively job hunting
   - Monitor application rates
   - Identify inactive users

3. **Customize preferences per user**
   - Different experience levels
   - Different countries
   - Different keywords

---

## 🎉 Ready!

Your multi-user analytics system is ready to go. Tomorrow at 8 AM you'll get your first daily report!

**Want to test it now?**
```bash
# Trigger analytics manually
gh workflow run daily-analytics.yml
```
