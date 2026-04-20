# JobScraper Auto-Apply — Chrome Extension

Fills job-application forms on LinkedIn, Greenhouse, Lever, and Workday
using the CV profile parsed by the JobScraper backend.

## Install (developer mode)

1. Open `chrome://extensions`
2. Enable **Developer mode** (top-right)
3. Click **Load unpacked** → pick this folder
4. Pin the **JobScraper Auto-Apply** icon to the toolbar
5. Click the icon → sign in with your JobScraper account
6. Open a job application page (e.g. a LinkedIn Easy Apply modal)
7. Click the floating **Auto-Fill** button in the bottom-right corner
8. Review the filled fields, then submit manually

## How it works

- **Popup** (`popup.html`) — login + shows your cached CV summary
- **Content script** (`content.js`) — runs on apply pages, collects form fields, calls the backend mapper, fills the values
- **Background** (`background.js`) — holds the auth token in `chrome.storage.local`, proxies all API calls so the token never leaves the extension
- **Backend** — `POST /api/autoapply/map-fields` takes the scraped fields + your profile and returns `{ field_id: value }` via Claude Haiku

## What's filled today

- Name, email, phone, location, LinkedIn, GitHub, portfolio URL
- Years of experience, current title/company, seniority
- Skills list, work authorization (if in profile)

## What's NOT filled (by design)

- Cover letters / motivation fields — you write these
- Salary expectations, notice period — not in CV by default
- Demographic / voluntary disclosure fields
- Anything the mapper isn't confident about (returns null)

## Adding a new ATS

Edit `content.js:detectApplyForm()` and add a CSS selector for the site's
application form container. The rest of the pipeline is site-agnostic.
