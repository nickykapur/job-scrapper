# Telegram Notifications Setup (3 minutes)

Get instant, reliable push notifications on your iPhone!

---

## 📱 Step 1: Install Telegram (1 minute)

1. **Download Telegram** from App Store
2. **Create account** (uses your phone number)
3. **Done!**

---

## 🤖 Step 2: Create Bot (2 minutes)

1. **Open Telegram**
2. **Search for:** `@BotFather`
3. **Start chat** with BotFather
4. **Send:** `/newbot`
5. **Follow prompts:**
   - Bot name: `Job Scraper` (or anything)
   - Bot username: `yourname_jobscraper_bot` (must be unique)
6. **Copy the bot token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Screenshot of what you'll see:**
```
Done! Congratulations on your new bot.

Token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

Keep your token secure and store it safely,
it can be used by anyone to control your bot.
```

---

## 💬 Step 3: Get Your Chat ID (30 seconds)

1. **In Telegram, search for your bot** (the username you just created)
2. **Start the bot** - tap "START" or send any message like "hello"
3. **Open this link** in Safari (replace YOUR_TOKEN with your actual token):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
   Example:
   ```
   https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz/getUpdates
   ```
4. **Find your chat ID** in the response:
   ```json
   {"result":[{"message":{"chat":{"id":123456789}}}]}
   ```
   Your chat ID is: `123456789`

---

## 🔐 Step 4: Add to GitHub (1 minute)

1. **Go to:** https://github.com/nickykapur/job-scrapper/settings/secrets/actions
2. **Click "New repository secret"**
3. **Add first secret:**
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token (from Step 2)
   - Click "Add secret"
4. **Click "New repository secret" again**
5. **Add second secret:**
   - Name: `TELEGRAM_CHAT_ID`
   - Value: Your chat ID (from Step 3)
   - Click "Add secret"

---

## ✅ Done!

That's it! After I add the code and you deploy, you'll get notifications like:

```
🤖 Job Scraper

🇮🇪 Ireland: 23 jobs ✅
🇪🇸 Spain: 15 jobs ✅
🇵🇦 Panama: 8 jobs ✅
🇨🇱 Chile: 12 jobs ✅
🇳🇱 Netherlands: 7 jobs ✅
🇩🇪 Germany: 10 jobs ✅
🇸🇪 Sweden: 5 jobs ✅

🎉 Complete!
📊 Total: 5,234 jobs
🧹 Cleaned: 142 old jobs
⏱️ Time: 5 minutes
```

---

## 📲 What You'll Receive

**8 notifications per run:**
1. Ireland complete (as it finishes)
2. Spain complete (as it finishes)
3. Panama complete
4. Chile complete
5. Netherlands complete
6. Germany complete
7. Sweden complete
8. **Final summary** with all stats

**Frequency:** 7 times per day = 56 notifications per day

**Timing:**
- 9 AM Dublin time
- 11 AM Dublin time
- 1 PM Dublin time
- 3 PM Dublin time
- 4 PM Dublin time
- 6 PM Dublin time
- 8 PM Dublin time

---

## 🔕 Too Many Notifications?

**Option 1: Mute per-country, keep summary**
- Tell me and I'll only send the final summary
- 7 notifications/day instead of 56

**Option 2: Mute Telegram chat**
- Long-press on bot chat → Mute
- Still see messages, no alerts

---

## 🧪 Test It

After setup, I'll add a test command. You can test anytime:

```bash
curl -s -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" \
  -d "chat_id=<YOUR_CHAT_ID>" \
  -d "text=Test notification! 🎉"
```

You should see "Test notification! 🎉" appear in Telegram immediately!

---

## 🔒 Security

**Is this safe?**
- ✅ Bot token is secret (only you and GitHub have it)
- ✅ Chat ID is not sensitive
- ✅ Only your bot can message you
- ✅ No one else can send you messages through your bot

**Keep token safe:**
- ❌ Don't share bot token
- ❌ Don't commit token to git
- ✅ Only store in GitHub Secrets

---

## ❓ Troubleshooting

### "getUpdates returns empty"
- Make sure you sent a message to your bot first
- The bot can't find your chat ID until you start the conversation

### "Unauthorized" error
- Check your bot token is correct
- Make sure there are no extra spaces when copying

### "Not receiving notifications"
- Check iOS Settings → Notifications → Telegram → ✅ Enabled
- Check Telegram app → Settings → Notifications → ✅ Enabled
- Try test command above

---

## 📱 Example Notification

Real notification you'll receive:

```
┌─────────────────────────────────────┐
│ 🤖 Job Scraper                      │
│                                     │
│ 🇮🇪 Ireland: 23 jobs ✅              │
│ 🇪🇸 Spain: 15 jobs ✅                │
│ 🇵🇦 Panama: 8 jobs ✅                │
│ 🇨🇱 Chile: 12 jobs ✅                │
│ 🇳🇱 Netherlands: 7 jobs ✅           │
│ 🇩🇪 Germany: 10 jobs ✅              │
│ 🇸🇪 Sweden: 5 jobs ✅                │
│                                     │
│ 🎉 All countries complete!          │
│ 📊 Total: 5,234 jobs                │
│ 🧹 Cleaned: 142 old jobs            │
│ ⏱️ Duration: 5 minutes              │
│                                     │
│ View jobs: railway.app              │
└─────────────────────────────────────┘
```

---

## 🎯 Ready?

Once you complete these 4 steps above, tell me:
- "I added the secrets"

Then I'll:
1. Add Telegram notification code to workflow
2. Commit everything
3. Push to GitHub
4. You'll start receiving notifications!

---

**Telegram is THE BEST because it just works.** Millions of developers use it for notifications. You'll love it! 🚀
