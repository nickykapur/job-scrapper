# Slack Notifications Setup (2 minutes)

Get instant push notifications on your iPhone when job scraping completes!

---

## 📱 What You'll Get

**Per-country notifications (as they complete):**
```
:flag-ie: Ireland: 23 jobs ✅
:flag-es: Spain: 15 jobs ✅
:flag-pa: Panama: 8 jobs ✅
... (7 total)
```

**Final summary:**
```
╔═══════════════════════════════════╗
║ 🎉 Job Scraper Complete          ║
║ ✅ All countries completed        ║
║                                   ║
║ 📊 Total Jobs: 5,234             ║
║ 🧹 Jobs Cleaned: 142             ║
║ ⏱️ Run: #47                       ║
║ 🌍 Countries: 7                   ║
║                                   ║
║ 🔗 View Jobs on Railway           ║
╚═══════════════════════════════════╝
```

---

## 🚀 Setup Instructions

### Step 1: Create Slack Workspace (if you don't have one)

1. Go to: https://slack.com/get-started
2. Click "Create a new workspace"
3. Follow the prompts (free forever)
4. Or use existing workspace

### Step 2: Create Channel

1. In Slack, click "+" next to "Channels"
2. Name it: `job-alerts` (or anything you want)
3. Create channel

### Step 3: Create Incoming Webhook (1 minute)

1. Go to: https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. App Name: `Job Scraper`
5. Select your workspace → "Create App"
6. On the left sidebar, click "Incoming Webhooks"
7. Toggle "Activate Incoming Webhooks" to **ON**
8. Scroll down, click "Add New Webhook to Workspace"
9. Select your `#job-alerts` channel → "Allow"
10. **Copy the Webhook URL** (looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`)

### Step 4: Add to GitHub (30 seconds)

1. Go to: https://github.com/nickykapur/job-scrapper/settings/secrets/actions
2. Click "New repository secret"
3. Name: `SLACK_WEBHOOK_URL`
4. Value: Paste your webhook URL
5. Click "Add secret"

### Step 5: Enable iPhone Notifications

1. **iOS Settings** → **Notifications** → **Slack**
2. Enable: ✅ **Allow Notifications**
3. Enable: ✅ **Sounds**
4. Enable: ✅ **Badges**
5. Enable: ✅ **Show on Lock Screen**

---

## ✅ Done!

That's it! After the next deployment, you'll get notifications like:

```
🤖 Job Scraper
12:35 PM

:flag-ie: Ireland: 23 jobs ✅

12:36 PM

:flag-es: Spain: 15 jobs ✅

... (7 countries)

12:40 PM

╔═══════════════════════════════════╗
║ 🎉 Job Scraper Complete          ║
║ ✅ All countries completed!       ║
║                                   ║
║ 📊 Total Jobs: 5,234             ║
║ 🧹 Jobs Cleaned: 142             ║
║ ⏱️ Run: #47                       ║
║ 🌍 Countries: 7                   ║
║                                   ║
║ 🔗 View Jobs on Railway           ║
╚═══════════════════════════════════╝
```

---

## 📊 Notification Schedule

**7 automatic runs per day:**
- 9 AM Dublin time
- 11 AM Dublin time
- 1 PM Dublin time
- 3 PM Dublin time
- 4 PM Dublin time
- 6 PM Dublin time
- 8 PM Dublin time

**Per run:** 8 notifications (7 countries + 1 summary)
**Daily total:** 56 notifications

---

## 🔕 Too Many Notifications?

### Option 1: Mute channel but keep alerts
1. Right-click `#job-alerts` channel
2. "Mute channel" → "Until I turn it back on"
3. Still get notifications, but less intrusive

### Option 2: Only receive summary (not per-country)
Tell me and I'll remove the per-country notifications, keep only the final summary (7 notifications/day instead of 56)

### Option 3: Quiet hours
1. Slack → Settings → Notifications
2. Set "Do Not Disturb" schedule
3. Example: 10 PM - 8 AM

---

## 🧪 Test It

After setup, test your webhook:

```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"text":"🎉 Test notification from Job Scraper!"}'
```

You should see the message appear in your `#job-alerts` channel and get a push notification on your iPhone!

---

## 🔒 Security

- ✅ Webhook URL is secret (stored in GitHub Secrets)
- ✅ Only your GitHub workflow can send messages
- ✅ Can revoke webhook anytime
- ❌ Don't share webhook URL publicly

---

## ❓ Troubleshooting

### "Webhook invalid"
- Check you copied the full webhook URL
- No extra spaces or characters
- Starts with: `https://hooks.slack.com/services/...`

### "Not receiving notifications on iPhone"
- Check iOS Settings → Notifications → Slack → Enabled
- Check Slack app → Preferences → Notifications → Enabled
- Make sure channel isn't muted

### "401 Unauthorized"
- Webhook was revoked
- Create new webhook (Step 3)
- Update GitHub Secret with new URL

---

## 💡 Why Slack?

| Feature | Slack | Telegram | Discord |
|---------|-------|----------|---------|
| **iPhone push** | ✅✅✅ | ✅✅✅ | ⚠️ Hit or miss |
| **Setup time** | 2 min | 3 min | 5 min |
| **Free** | ✅ | ✅ | ✅ |
| **Rich formatting** | ✅✅✅ | ✅ | ✅✅ |
| **Professional** | ✅✅✅ | ⚠️ | ⚠️ |
| **Already using?** | Maybe! | Unlikely | Maybe |

**Slack wins if:**
- You already use Slack for work
- You want professional-looking notifications
- You need reliable iPhone push notifications

---

## 📱 Example iPhone Notification

What you'll see on lock screen:

```
┌─────────────────────────────────────┐
│ 🤖 Job Scraper                      │
│ #job-alerts                         │
│                                     │
│ :flag-ie: Ireland: 23 jobs ✅        │
└─────────────────────────────────────┘

Swipe to open Slack →
```

---

## ✅ Ready to Deploy

Once you've added `SLACK_WEBHOOK_URL` to GitHub Secrets, tell me:

**"I added the Slack webhook"**

Then I'll:
1. Commit all the fixes (database sync, frontend, notifications)
2. Push to GitHub
3. Run backfill script
4. You'll start getting notifications!

---

## 🎯 Summary

**Setup:**
1. Create Slack workspace (or use existing)
2. Create #job-alerts channel
3. Create Incoming Webhook
4. Add webhook URL to GitHub Secrets

**What you get:**
- 8 notifications per run (7 countries + summary)
- 7 runs per day = 56 daily notifications
- Rich formatted messages
- Reliable iPhone push notifications
- Free forever

**Ready? Follow the 5 steps above!** 🚀
