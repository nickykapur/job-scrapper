# How Notifications Work

## 📱 Notification System Overview

The job scraper sends notifications at 3 different stages during execution:

```
┌─────────────────────────────────────────────────────────┐
│  Start: Parallel scraping of 7 countries                │
└─────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │ Ireland │    │  Spain  │    │ Panama  │  ... (7 countries)
    └────┬────┘    └────┬────┘    └────┬────┘
         │               │               │
    🔔 Notify      🔔 Notify       🔔 Notify  (Per-country)
         │               │               │
         └───────────────┼───────────────┘
                         │
                    ┌────▼────┐
                    │ Cleanup │
                    └────┬────┘
                         │
                    🔔 Final Summary
```

---

## 🔔 Notification Types

### 1. Per-Country Notifications (7 notifications per run)

**When:** As each country completes scraping (5-7 minutes)

**Where it appears:**
- ✅ GitHub mobile app push notification
- ✅ GitHub Actions web UI
- ✅ GitHub Actions logs

**Example:**
```
┌─────────────────────────────────┐
│ Ireland ✅                       │
│ Completed - 23 jobs found       │
│ 2 minutes ago                   │
└─────────────────────────────────┘
```

**How it works:**
```yaml
# In .github/workflows/parallel-scraper.yml
- name: Country completion notification
  run: |
    echo "::notice title=Ireland ✅::Completed - 23 jobs found"
```

The `::notice` syntax is GitHub Actions' special annotation format that:
- Creates a visible annotation in the workflow
- Triggers a notification if you're watching the repo
- Shows up in the GitHub mobile app

---

### 2. Final Summary Notification (1 per run)

**When:** After all 7 countries finish + cleanup completes

**Where it appears:**
- ✅ GitHub mobile app
- ✅ GitHub Actions summary page
- ✅ Discord/Slack (optional)

**Example:**
```
┌──────────────────────────────────────────┐
│ ✅ Job Scraping Complete!                │
│                                          │
│ 📊 Results:                              │
│ • Total Jobs: 5,234                      │
│ • Old Jobs Cleaned: 142                  │
│ • Countries: 7                           │
│                                          │
│ 🌍 Country Results:                      │
│ ✅ Ireland: 23 jobs                      │
│ ✅ Spain: 15 jobs                        │
│ ✅ Panama: 8 jobs                        │
│ ✅ Chile: 12 jobs                        │
│ ✅ Netherlands: 7 jobs                   │
│ ✅ Germany: 10 jobs                      │
│ ✅ Sweden: 5 jobs                        │
│                                          │
│ View jobs at Railway                     │
└──────────────────────────────────────────┘
```

---

### 3. Failure Notifications

**When:** If any country fails or error occurs

**Example:**
```
┌─────────────────────────────────┐
│ Germany ❌                       │
│ Scraping failed                 │
│ 3 minutes ago                   │
└─────────────────────────────────┘
```

---

## 📲 How to Receive Notifications on iPhone

### Method 1: GitHub Mobile App (Recommended - FREE)

**Setup (2 minutes):**

1. **Install GitHub app** from App Store
2. **Login** with your account
3. **Enable notifications:**
   - App Settings → Notifications → ✅ "Actions"
4. **Watch repository:**
   - Go to: github.com/nickykapur/job-scrapper
   - Tap "Watch" → "Custom" → ✅ "Actions"

**What you'll receive:**

| Time | Notification |
|------|-------------|
| 0:00 | 🇮🇪 Ireland ✅ - 23 jobs |
| 0:30 | 🇪🇸 Spain ✅ - 15 jobs |
| 1:00 | 🇵🇦 Panama ✅ - 8 jobs |
| 1:30 | 🇨🇱 Chile ✅ - 12 jobs |
| 2:00 | 🇳🇱 Netherlands ✅ - 7 jobs |
| 2:30 | 🇩🇪 Germany ✅ - 10 jobs |
| 3:00 | 🇸🇪 Sweden ✅ - 5 jobs |
| 3:30 | ✅ Complete! Total: 5,234 jobs |

**Frequency:**
- 7 times per day (9 AM, 11 AM, 1 PM, 3 PM, 4 PM, 6 PM, 8 PM Dublin time)
- 8 notifications per run (7 countries + 1 summary)
- Total: ~56 notifications per day

---

### Method 2: Discord (Also FREE)

**Setup (5 minutes):**

1. **Install Discord** from App Store
2. **Create server** (free)
3. **Create webhook:**
   - Channel → Settings → Integrations → Webhooks
   - Copy webhook URL
4. **Add to GitHub:**
   - Go to: github.com/nickykapur/job-scrapper/settings/secrets/actions
   - New secret: `NOTIFICATION_WEBHOOK_URL`
   - Paste Discord webhook URL

**What you'll receive:**

```
╔═══════════════════════════════════════╗
║  Job Scraper Complete                 ║
║  ✅ All countries completed           ║
║                                       ║
║  Total Jobs       Jobs Cleaned        ║
║  5,234           142                  ║
║                                       ║
║  Duration: Run #47                    ║
║  2024-10-30 14:25:30 UTC             ║
║                                       ║
║  View jobs →                          ║
╚═══════════════════════════════════════╝
```

**Advantage:** Only 1 notification per run (not 8)

---

## 🔧 Technical Details

### GitHub Actions Annotations

GitHub Actions supports special commands that create notifications:

```bash
# Success notification
echo "::notice title=Ireland ✅::Completed - 23 jobs found"

# Warning notification
echo "::warning title=⚠️ Some Issues::Check logs for details"

# Error notification
echo "::error title=Germany ❌::Scraping failed"
```

**Where these appear:**
1. **Workflow logs** - Highlighted annotations
2. **Workflow summary** - Collected at the top
3. **Mobile notifications** - Push notifications
4. **Email** - If email notifications enabled

---

### How Per-Country Notifications Work

**Code in daily_single_country_scraper.py:**

```python
# After scraping completes for a country
print(f"\n::notice title={country_name} Complete::{len(all_new_jobs)} new jobs found and uploaded")

# Set output for GitHub Actions
if os.getenv('GITHUB_OUTPUT'):
    with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
        f.write(f"jobs_found={len(all_new_jobs)}\n")
        f.write(f"country={country_name}\n")
```

**Then in workflow:**

```yaml
- name: Run scraper for Ireland
  id: scrape
  run: python daily_single_country_scraper.py --country Ireland

- name: Country completion notification
  if: always()
  run: |
    if [ "${{ steps.scrape.outcome }}" == "success" ]; then
      echo "::notice title=Ireland ✅::Completed - ${{ steps.scrape.outputs.jobs_found }} jobs found"
    else
      echo "::error title=Ireland ❌::Scraping failed"
    fi
```

---

### How Summary Notifications Work

**After all countries complete:**

```yaml
- name: Create summary and notification
  run: |
    # Create GitHub Actions summary (visible in UI)
    echo "### 🎉 Job Scraping Complete!" >> $GITHUB_STEP_SUMMARY
    echo "- **Total Jobs:** 5,234" >> $GITHUB_STEP_SUMMARY

    # Send mobile notification
    echo "::notice title=✅ Scraping Complete::All 7 countries processed. Total jobs: 5,234"
```

---

## 📊 Notification Comparison

| Method | Setup | iPhone | Desktop | Email | Rich Format | Frequency Control |
|--------|-------|--------|---------|-------|-------------|-------------------|
| **GitHub Mobile** | 2 min | ✅ Push | ✅ | ⚠️ Optional | Basic | Per-notification |
| **Discord** | 5 min | ✅ Push | ✅ | ❌ | ✅ Rich embeds | Per-server |
| **Slack** | 5 min | ✅ Push | ✅ | ❌ | ✅ Rich embeds | Per-workspace |
| **Email** | 0 min | ⚠️ Delayed | ✅ | ✅ | Basic | Limited control |

---

## 🎯 Recommended Setup

**For maximum awareness:**
1. **Enable GitHub mobile** - Get all per-country notifications
2. **Add Discord webhook** - Get summary with rich formatting
3. **Result:**
   - Real-time updates on iPhone via GitHub
   - Summary card in Discord for quick overview

**For minimal notifications:**
1. **Add Discord webhook** - Only 1 notification per run
2. **Disable GitHub mobile** - No per-country spam
3. **Result:** 7 notifications/day instead of 56

---

## 🔍 Notification Troubleshooting

### "Not receiving any notifications"

**Check GitHub mobile app:**
```
1. iOS Settings → Notifications → GitHub → ✅ Allow Notifications
2. GitHub app → Settings → Notifications → ✅ Actions
3. Repository → Watch → Custom → ✅ Actions
```

**Check Discord:**
```
1. Webhook URL is correct in GitHub Secrets
2. Discord channel allows webhooks
3. Test with: curl -X POST "<webhook_url>" -H "Content-Type: application/json" -d '{"content":"test"}'
```

### "Too many notifications"

**Option 1: Use Discord only**
- Remove GitHub Actions watch
- Add Discord webhook
- Result: 7 notifications/day

**Option 2: Disable per-country**
- Edit `.github/workflows/parallel-scraper.yml`
- Remove the "Country completion notification" step
- Keep only final summary

### "Notifications delayed"

**GitHub mobile:** Usually instant (within seconds)
**Discord:** Instant
**Email:** Can be delayed 5-15 minutes

---

## 📅 Notification Schedule

**Automatic runs (7 times per day):**
- 9:00 AM Dublin time
- 11:00 AM Dublin time
- 1:00 PM Dublin time
- 3:00 PM Dublin time
- 4:00 PM Dublin time
- 6:00 PM Dublin time
- 8:00 PM Dublin time

**Each run:**
- Duration: 5-7 minutes
- Notifications: 8 (7 countries + 1 summary)
- Total daily: 56 notifications

---

## 🎉 Example Notification Flow

**Real-world example from a 5-minute run:**

```
14:00:00 - ⏰ Workflow starts

14:00:30 - 🇮🇪 Ireland ✅ (23 jobs)
14:01:00 - 🇪🇸 Spain ✅ (15 jobs)
14:01:30 - 🇵🇦 Panama ✅ (8 jobs)
14:02:00 - 🇨🇱 Chile ✅ (12 jobs)
14:02:30 - 🇳🇱 Netherlands ✅ (7 jobs)
14:03:00 - 🇩🇪 Germany ✅ (10 jobs)
14:03:30 - 🇸🇪 Sweden ✅ (5 jobs)

14:04:00 - 🧹 Cleanup (deleted 42 old jobs)

14:05:00 - ✅ Complete! (Total: 5,234 jobs)
```

**On your iPhone:**
- 8 notifications received over 5 minutes
- Tap any notification → Opens GitHub app
- Tap "View jobs" → Opens Railway frontend

---

## 🚀 Future Enhancements

Possible additions (not yet implemented):

1. **Telegram notifications** - Alternative to Discord
2. **SMS notifications** - Via Twilio (costs money)
3. **Custom notification sounds** - Per country
4. **Job quality score** - Show in notification
5. **Daily digest** - One summary per day instead of per-run
6. **Smart filtering** - Only notify for "interesting" jobs

---

## ✅ Summary

**Current implementation:**
- ✅ 8 notifications per run (7 countries + summary)
- ✅ Works with GitHub mobile app (free)
- ✅ Works with Discord/Slack (free)
- ✅ Real-time updates (within seconds)
- ✅ Rich formatting support
- ✅ Failure alerts
- ✅ 7 automatic runs per day

**To enable:**
1. Install GitHub mobile app
2. Enable Actions notifications
3. Watch repository with "Actions" checked
4. Done! 📱
