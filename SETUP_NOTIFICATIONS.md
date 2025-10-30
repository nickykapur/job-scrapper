# Setup Push Notifications for Job Scraper

Get notified on your phone/desktop when scraping completes!

---

## Built-in Notifications (Already Enabled) ✅

GitHub automatically sends email notifications for workflow runs if you have:
- Workflow failures
- Watch notifications enabled

**To enable:**
1. Go to https://github.com/nickykapur/job-scrapper
2. Click "Watch" → "Custom" → Check "Actions"
3. You'll get email notifications

**GitHub Summary (Already added):**
- After each run, check: https://github.com/nickykapur/job-scrapper/actions
- Click on the run
- See summary with total jobs, cleaned jobs, status

---

## Option 1: Discord Notifications (Recommended) 🔔

Get instant push notifications on your phone via Discord!

### Setup Steps:

**1. Create Discord Webhook:**
   - Open Discord (web/mobile/desktop)
   - Go to any server you own (or create one)
   - Click on a channel → Edit Channel → Integrations
   - Click "Create Webhook"
   - Copy the webhook URL (looks like: `https://discord.com/api/webhooks/...`)

**2. Add to GitHub Secrets:**
   - Go to https://github.com/nickykapur/job-scrapper/settings/secrets/actions
   - Click "New repository secret"
   - Name: `NOTIFICATION_WEBHOOK_URL`
   - Value: Paste your Discord webhook URL
   - Click "Add secret"

**3. Done!** You'll now get notifications like:

```
🎉 Job Scraper Complete
✅ All countries completed

Total Jobs: 5,234
Jobs Cleaned: 142
Duration: Run #47

View jobs: https://web-production-110bb.up.railway.app
```

---

## Option 2: Slack Notifications

### Setup Steps:

**1. Create Slack Webhook:**
   - Go to https://api.slack.com/apps
   - Create New App → From scratch
   - App Name: "Job Scraper Bot"
   - Select your workspace
   - Click "Incoming Webhooks" → Activate
   - Click "Add New Webhook to Workspace"
   - Select channel → Allow
   - Copy the webhook URL

**2. Add to GitHub Secrets:**
   - Go to https://github.com/nickykapur/job-scrapper/settings/secrets/actions
   - Click "New repository secret"
   - Name: `NOTIFICATION_WEBHOOK_URL`
   - Value: Paste your Slack webhook URL
   - Click "Add secret"

**3. Done!** You'll get Slack notifications

---

## Option 3: Telegram Notifications

### Setup Steps:

**1. Create Telegram Bot:**
   - Open Telegram
   - Search for @BotFather
   - Send `/newbot`
   - Follow instructions to create bot
   - Copy the bot token

**2. Get your Chat ID:**
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Look for `"chat":{"id":...}` - that's your chat ID

**3. Modify workflow (add this step):**
```yaml
- name: Send Telegram notification
  if: env.TELEGRAM_TOKEN != ''
  env:
    TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
  run: |
    MESSAGE="🎉 Job Scraper Complete!%0A%0ATotal Jobs: ${{ steps.cleanup.outputs.total_jobs }}%0AJobs Cleaned: ${{ steps.cleanup.outputs.jobs_deleted }}"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "text=${MESSAGE}"
```

**4. Add GitHub Secrets:**
   - `TELEGRAM_BOT_TOKEN`: Your bot token
   - `TELEGRAM_CHAT_ID`: Your chat ID

---

## Testing Notifications

After setting up:

1. Go to https://github.com/nickykapur/job-scrapper/actions
2. Click "Parallel Job Scraper (Fast)"
3. Click "Run workflow"
4. Wait 5-7 minutes
5. You should receive a notification!

---

## Notification Content

You'll receive:
- ✅/⚠️ Status (success or failures)
- Total jobs in database
- Number of old jobs cleaned up
- Link to view jobs
- Timestamp

Example Discord/Slack message:
```
🎉 Job Scraper Complete
✅ All countries completed

📊 Total Jobs: 5,234
🧹 Jobs Cleaned: 142
⏱️ Duration: Run #47
🕐 2024-10-30 14:25:30 UTC

👉 View jobs: https://web-production-110bb.up.railway.app
```

---

## Troubleshooting

### "Notification not received"
- Check webhook URL is correct in GitHub Secrets
- Test webhook manually: `curl -X POST <webhook_url> -H "Content-Type: application/json" -d '{"content":"test"}'`
- Check Discord/Slack channel permissions

### "Notification says 'failed'"
- Check GitHub Actions logs for actual error
- Some countries may have failed but others succeeded
- Notification will show which countries failed

---

## Disable Notifications

To disable:
1. Go to https://github.com/nickykapur/job-scrapper/settings/secrets/actions
2. Delete the `NOTIFICATION_WEBHOOK_URL` secret
3. Notifications will stop (but workflow still runs)

---

## Recommended: Discord

- ✅ Free
- ✅ Easy setup (2 minutes)
- ✅ Mobile app with push notifications
- ✅ Desktop app
- ✅ Web access
- ✅ No rate limits for webhooks
- ✅ Rich formatting (embeds)

Create a Discord account → Create server → Add webhook → Done!
