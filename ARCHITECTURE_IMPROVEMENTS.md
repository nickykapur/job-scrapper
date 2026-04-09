# Architecture Improvements

Backlog of planned improvements, ordered by priority. Safe items first, riskiest last.

---

## 1. Queue retry logic ✅ Safe — no risk to existing functionality

**Problem:** Failed queue items (scraped jobs that errored during sync) are marked `failed` and never retried. Scraping runs from GitHub Actions can silently lose jobs with no recovery.

**Fix:**
- Add a `retry_count` column to `job_upload_queue`
- On failure, increment count and reset status to `pending` if `retry_count < 3`
- Only mark `failed` permanently after 3 attempts
- Add a `/api/admin/queue-status` endpoint to surface queue depth, failed items, last processed

**Files to change:**
- `railway_server.py` — `_process_queue_once()` (lines ~332–415), startup migration

**Risk:** None. Additive only.

---

## 2. Replace 10 `create_user_*.py` scripts with admin API endpoint ✅ Safe — no risk to production

**Problem:** 10 nearly-identical scripts (`create_ashwani_user.py`, `create_blanca_user.py`, etc.) each ~260 lines of copy-pasted code with hardcoded usernames, passwords, and preferences. Maintenance nightmare.

**Fix:**
- Add `POST /api/admin/users/create` endpoint that accepts a full user config (username, email, password, job_types, keywords, countries, etc.)
- Delete the 10 individual scripts
- Optionally add a `user_configs/` folder with JSON files per user for reproducibility

**Files to change:**
- `railway_server.py` or `auth_routes.py` — new endpoint
- Delete: `create_ashwani_user.py`, `create_blanca_user.py`, `create_finance_user.py`, `create_glo_user.py`, `create_hr_user.py`, `create_manya_user.py`, `create_maria_user.py`, `create_melis_user.py`, `create_sales_user.py`

**Risk:** None. Scripts are only run manually, not at runtime.

---

## 3. Migration tracking ⚠️ Low risk

**Problem:** No record of which DB migrations have been applied. Schema is created inline at startup in `railway_server.py` AND in `database_migrations/*.sql` files — two sources of truth that can drift. Can't safely roll back or coordinate schema changes.

**Fix:**
- Create a `schema_migrations` table: `(id SERIAL, version VARCHAR, applied_at TIMESTAMPTZ)`
- Each migration gets a version string (e.g. `003_add_retry_count_to_queue`)
- Startup checks which versions have been applied and runs only new ones
- Move all inline `CREATE TABLE IF NOT EXISTS` blocks in `startup_event()` into versioned migration functions

**Files to change:**
- `railway_server.py` — `startup_event()` (~lines 267–330)
- `database_migrations/` — add new migration files

**Risk:** Low. Additive. Only risk is incorrect migration ordering at first deploy.

---

## 4. Split `railway_server.py` (4,620 lines) into routers + services ⚠️ Medium risk — needs testing after

**Problem:** Single god file with ~60 endpoints mixing routing, business logic, DB migrations, queue management, Slack integration, analytics, admin tools. Hard to maintain, impossible to unit test.

**Proposed structure:**
```
routes/
  jobs.py          # /api/jobs, /api/update_job, /api/jobs/bulk-reject etc.
  admin.py         # /api/admin/*, /api/migrate-schema, /api/backfill-*
  scraper.py       # /api/scraper-run, /api/scraping-targets
  analytics.py     # /api/analytics/*, /api/user-behaviour
  activity.py      # /api/activity
services/
  queue_service.py # _queue_worker, _process_queue_once
  job_service.py   # filtering logic (lines 492–760), feed construction
```

**Migration approach:**
- Extract one router at a time, test each before moving to the next
- Start with the most self-contained: `analytics.py`, then `scraper.py`, then `jobs.py`, then `admin.py`
- Use `app.include_router()` pattern (already used for `auth_routes.py`)

**Files to change:**
- `railway_server.py` — gutted to ~200 lines (app init, startup, static serving)
- New files in `routes/` and `services/`

**Risk:** Medium. Pure refactoring but high surface area. Any missed import or re-export breaks that endpoint. Needs end-to-end smoke test after each extraction.

---

## Already done

| Date | Fix |
|------|-----|
| 2026-04-09 | Connection pooling in `UserDatabase` — replaced per-call `asyncpg.connect()` with class-level pool (min=2, max=10) |
| 2026-04-09 | Fixed job type misclassification — reclassified 7,752 legacy LinkedIn-category jobs; fixed `'scientist'` biotech bug in scraper |
| 2026-04-09 | Landing page performance — enabled minification (2.8MB → ~473KB for guests), lazy-loaded dashboard chunk, added mobile nav, disabled parallax on mobile |
