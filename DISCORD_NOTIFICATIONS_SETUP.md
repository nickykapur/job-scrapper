# Discord Push Notifications Setup (5 minutes)

Get instant push notifications on your iPhone when job scraping completes!

---

## 📱 What You'll Get

**8 notifications per run (every few hours):**

```
✅ Ireland complete: 23 jobs found
✅ Spain complete: 15 jobs found
✅ Panama complete: 8 jobs found
✅ Chile complete: 12 jobs found
✅ Netherlands complete: 7 jobs found
✅ Germany complete: 10 jobs found
✅ Sweden complete: 5 jobs found

╔═══════════════════════════════════╗
║ 🎉 Job Scraper Complete          ║
║ ✅ All countries completed        ║
║                                   ║
║ 📊 Total Jobs: 5,234             ║
║ 🧹 Jobs Cleaned: 142             ║
║ ⏱️ Run: #47                       ║
╚═══════════════════════════════════╝
```

---

## 🚀 Setup Instructions

### Step 1: Install Discord App (2 minutes)

1. **Download Discord** from App Store
2. **Create account** (free)
3. **Create a server:**
   - Tap the "+" icon
   - Choose "Create My Own"
   - Name it "Job Alerts" (or anything)
   - Create

### Step 2: Create Webhook (2 minutes)

1. **Open your server**
2. **Tap on a text channel** (e.g., #general)
3. **Tap channel name** → "Settings"
4. **Scroll down** → "Integrations"
5. **Tap "Webhooks"** → "New Webhook"
6. **Copy webhook URL** (looks like: `https://discord.com/api/webhooks/...`)

### Step 3: Add to GitHub (1 minute)

1. **Go to:** https://github.com/nickykapur/job-scrapper/settings/secrets/actions
2. **Click "New repository secret"**
3. **Name:** `DISCORD_WEBHOOK_URL`
4. **Value:** Paste the webhook URL you copied
5. **Click "Add secret"**

### Step 4: Done! ✅

That's it! You'll now get notifications on your iPhone.

---

## 📱 Enable iPhone Notifications

Make sure Discord can send push notifications:

1. **iOS Settings** → **Notifications** → **Discord**
2. Enable: ✅ **Allow Notifications**
3. Enable: ✅ **Sounds**
4. Enable: ✅ **Badges**
5. Enable: ✅ **Show on Lock Screen**

---

## 🧪 Test It

After setup, test the notifications:

1. **Go to:** https://github.com/nickykapur/job-scrapper/actions
2. **Click** "Parallel Job Scraper (Fast)"
3. **Click** "Run workflow" → "Run workflow"
4. **Wait 5-7 minutes**
5. **Check Discord** - You should see notifications!

---

## 📊 What You'll Receive

### Per-Country Notifications (as they complete):

```
✅ Ireland complete: 23 jobs found
✅ Spain complete: 15 jobs found
...
```

**Timing:** One every 30-60 seconds as countries finish

### Final Summary (after all complete):

```
╔═══════════════════════════════════╗
║ 🎉 Job Scraper Complete          ║
║ ✅ All countries completed        ║
║                                   ║
║ 📊 Total Jobs: 5,234             ║
║ 🧹 Jobs Cleaned: 142             ║
║ ⏱️ Run: #47                       ║
║                                   ║
║ Job Scraper                       ║
║ Oct 30, 2024 2:25 PM             ║
╚═══════════════════════════════════╝
```

**Features:**
- Rich embed with colors
- Total job count
- Cleanup statistics
- Timestamp
- Run number

### Failure Alerts:

```
❌ Germany failed
```

If any country fails, you'll be notified immediately.

---

## 📅 Notification Schedule

**Automatic runs: 7 times per day**
- 9:00 AM Dublin time
- 11:00 AM Dublin time
- 1:00 PM Dublin time
- 3:00 PM Dublin time
- 4:00 PM Dublin time
- 6:00 PM Dublin time
- 8:00 PM Dublin time

**Per run:**
- 8 notifications (7 countries + 1 summary)
- Over 5-7 minutes

**Total daily:**
- 56 notifications (8 × 7 runs)

---

## 🔕 Too Many Notifications?

If 56 notifications per day is too much:

### Option 1: Mute Country Notifications

Edit `.github/workflows/parallel-scraper.yml`:

```yaml
# Comment out this section (lines 51-76):
# - name: Country completion notification
#   ...
```

This will only send the final summary (7 notifications/day instead of 56).

### Option 2: Mute Discord Server

In Discord:
1. Long press on "Job Alerts" server
2. Tap "Notifications"
3. Choose "Only @mentions"

You'll still see notifications in Discord, but no phone alerts.

### Option 3: Quiet Hours

In iOS Discord settings:
1. Discord app → Settings → Notifications
2. Set quiet hours (e.g., 10 PM - 8 AM)

---

## 🎯 Troubleshooting

### "Not receiving notifications"

**Check webhook:**
```bash
# Test your webhook:
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test notification from job scraper!"}'
```

You should see "Test notification from job scraper!" appear in Discord.

**Check GitHub Secret:**
1. Go to: https://github.com/nickykapur/job-scrapper/settings/secrets/actions
2. Verify `DISCORD_WEBHOOK_URL` exists
3. If not, add it (see Step 3 above)

**Check Discord permissions:**
1. iOS Settings → Notifications → Discord → ✅ Enabled
2. Discord app → User Settings → Notifications → ✅ Enabled

### "Webhook invalid or revoked"

This means the webhook was deleted. Create a new one:
1. Discord → Channel Settings → Webhooks
2. Create new webhook
3. Copy new URL
4. Update GitHub Secret with new URL

### "Too many requests"

Discord has rate limits (30 messages per 60 seconds). Our workflow respects this:
- 7 countries = 7 messages (spread over 5-7 minutes)
- 1 summary = 1 message
- Total: 8 messages over 5-7 minutes ✅ Well within limits

---

## 🎨 Customize Notifications

### Change Webhook Name/Avatar:

In Discord webhook settings:
1. **Name:** "Job Scraper Bot"
2. **Avatar:** Upload an icon (optional)

### Add Link to View Jobs:

Edit `.github/workflows/parallel-scraper.yml` (line 136-139):

```yaml
\"fields\": [
  {\"name\": \"📊 Total Jobs\", \"value\": \"$TOTAL_JOBS\", \"inline\": true},
  {\"name\": \"🧹 Jobs Cleaned\", \"value\": \"$JOBS_DELETED\", \"inline\": true},
  {\"name\": \"🔗 View\", \"value\": \"[Open Jobs](https://web-production-110bb.up.railway.app)\", \"inline\": true}
],
```

---

## 🆚 Why Discord?

| Feature | Discord | GitHub Mobile | Email |
|---------|---------|---------------|-------|
| **Push notifications** | ✅ Instant | ❌ Doesn't work | ⚠️ Delayed |
| **Rich formatting** | ✅ Embeds | ❌ Basic | ❌ Basic |
| **Free** | ✅ | ✅ | ✅ |
| **Setup time** | 5 min | 2 min | 0 min |
| **Reliability** | ✅✅✅ | ❌ | ⚠️ |
| **Works on iPhone** | ✅ | ❌ | ✅ |

**Winner: Discord** - Most reliable, best formatting, works great!

---

## 📚 Example Flow

**Real notification sequence:**

```
2:00 PM - Workflow starts

2:01 PM - 📱 "✅ Ireland complete: 23 jobs found"
2:02 PM - 📱 "✅ Spain complete: 15 jobs found"
2:02 PM - 📱 "✅ Panama complete: 8 jobs found"
2:03 PM - 📱 "✅ Chile complete: 12 jobs found"
2:03 PM - 📱 "✅ Netherlands complete: 7 jobs found"
2:04 PM - 📱 "✅ Germany complete: 10 jobs found"
2:04 PM - 📱 "✅ Sweden complete: 5 jobs found"

2:05 PM - 📱 [Rich Summary Card]
           🎉 Job Scraper Complete
           ✅ All countries completed
           📊 Total Jobs: 5,234
           🧹 Jobs Cleaned: 142
```

**Tap any notification → Opens Discord → See full details**

---

## ✅ Quick Checklist

After following this guide, verify:

- [ ] Discord app installed on iPhone
- [ ] Server created
- [ ] Webhook created and copied
- [ ] GitHub Secret added (`DISCORD_WEBHOOK_URL`)
- [ ] iOS notifications enabled for Discord
- [ ] Tested with manual workflow run
- [ ] Received test notifications ✅

**All done? You're ready!** 🎉

Next automatic run will send notifications to your iPhone.

---

## 🔗 Related Files

- `parallel-scraper.yml` - Workflow that sends notifications
- `HOW_NOTIFICATIONS_WORK.md` - Technical details
- `SUMMARY_OF_FIXES.md` - All fixes applied today
