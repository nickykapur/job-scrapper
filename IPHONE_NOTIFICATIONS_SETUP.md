# Get Push Notifications on Your iPhone

Get instant notifications when job scraping completes!

---

## Option 1: GitHub Mobile App (Recommended - FREE) 📱

**Best choice:** Already have GitHub, works perfectly, completely free!

### Setup Steps:

**1. Install GitHub Mobile App:**
   - Download from App Store: https://apps.apple.com/app/github/id1477376905
   - Sign in with your GitHub account

**2. Enable Notifications:**
   - Open GitHub app
   - Tap your profile (bottom right)
   - Tap "Settings" (gear icon)
   - Tap "Notifications"
   - Enable "Push notifications"
   - Enable "Actions"

**3. Watch Your Repository:**
   - Go to: https://github.com/nickykapur/job-scrapper
   - Tap "Watch" → "Custom"
   - Check ✅ "Actions" (workflow runs)
   - Tap "Apply"

**4. Done!** You'll now receive notifications like:

```
✅ Scraping Complete
Ireland Complete: 23 new jobs found
Spain Complete: 15 new jobs found
Panama Complete: 8 new jobs found
...
All 7 countries processed successfully
Total jobs: 5,234
```

**Notification Triggers:**
- ✅ Each country completes (7 notifications per run)
- ✅ Final summary when all complete
- ⚠️ If any country fails
- ❌ If workflow fails

---

## Option 2: Discord (Also FREE) 💬

Great for custom messages and rich notifications.

### Setup Steps:

**1. Install Discord:**
   - Download from App Store
   - Create account (free)
   - Create a server (tap + icon → "Create My Own")

**2. Create Webhook:**
   - Open Discord
   - Go to your server
   - Tap on a channel → Settings → Integrations
   - Create Webhook
   - Copy webhook URL

**3. Add to GitHub:**
   - Go to: https://github.com/nickykapur/job-scrapper/settings/secrets/actions
   - Click "New repository secret"
   - Name: `NOTIFICATION_WEBHOOK_URL`
   - Value: Paste Discord webhook URL
   - Save

**4. Done!** You'll get rich notifications with:
- Total jobs count
- Jobs cleaned
- Status (success/failure)
- Timestamp
- Direct link to view jobs

---

## Comparison

| Method | iPhone Notifications | Setup Time | Cost | Features |
|--------|---------------------|------------|------|----------|
| **GitHub Mobile** | ✅ Yes | 2 minutes | Free | Per-country + summary |
| **Discord** | ✅ Yes | 5 minutes | Free | Rich formatting, custom messages |
| **Email** | ⚠️ Not instant | 0 minutes | Free | Built-in, delayed |

---

## What You'll Receive

### Per-Country Notifications (7 per run):
```
Ireland ✅
Completed - 23 jobs found and uploaded
```

### Final Summary Notification:
```
✅ Scraping Complete
All 7 countries processed successfully
Total jobs: 5,234

View jobs at your Railway app
```

### If Something Fails:
```
⚠️ Scraping Complete with Issues
Some countries failed. Check logs.
Total jobs: 4,821
```

---

## Testing Notifications

After setup:

1. Go to: https://github.com/nickykapur/job-scrapper/actions
2. Click "Parallel Job Scraper (Fast)"
3. Click "Run workflow" → "Run workflow"
4. Wait 5-7 minutes
5. Check your iPhone notifications!

---

## Customizing Notification Sound

**GitHub App:**
- iOS Settings → Notifications → GitHub
- Choose notification sound
- Enable "Banners" or "Alerts"
- Enable on Lock Screen

**Discord App:**
- Discord Settings → Notifications
- Choose notification sound
- Enable push notifications
- Customize per-server

---

## Troubleshooting

### "Not receiving notifications"

**GitHub App:**
- Check iOS Settings → Notifications → GitHub is enabled
- Check GitHub app settings → Notifications → Actions is enabled
- Make sure you're "Watching" the repository with "Actions" checked

**Discord:**
- Check webhook URL is correct in GitHub Secrets
- Check Discord app has notifications enabled in iOS Settings
- Test webhook: `curl -X POST "<webhook_url>" -H "Content-Type: application/json" -d '{"content":"test"}'`

### "Too many notifications"

If 7 notifications per run (one per country) is too many:
- Use Discord instead (only 1 final notification)
- Or modify the workflow to only send final summary

---

## Recommended Setup

**For best experience:**
1. Install GitHub mobile app
2. Enable Actions notifications
3. Watch repository with "Actions" checked
4. Done!

You'll get:
- Instant push notifications
- Per-country progress
- Final summary
- Failure alerts
- All 100% free
- No extra services needed

**Runs 7 times per day:**
- 9 AM, 11 AM, 1 PM, 3 PM, 4 PM, 6 PM, 8 PM (Dublin time)
- ~5-7 minutes each
- 7 notifications per run (+ 1 summary)
- Total: ~56 notifications per day
