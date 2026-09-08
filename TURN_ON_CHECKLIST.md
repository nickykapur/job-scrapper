# Turn-On Checklist

What to verify — and what to restore first — before the scraper can run again.

## Situation

Two separate things are switched off, and only one of them is a switch.

| Fact | Value |
|---|---|
| Last successful scrape | run #1544, **2026-06-24 17:49 UTC** |
| Why scraping stopped | GitHub set `parallel-scraper.yml` to `disabled_inactivity` (scheduled workflows are auto-disabled after 60 days without repo activity) |
| Why it can't just be re-enabled | **Railway is no longer being paid** — the backend and its Postgres are gone |
| Time since | ~2.5 months |
| Repo visibility | **public** (Actions minutes are free — hosting is the only cost) |

The scraper never wrote to Postgres directly. It POSTs to `$RAILWAY_URL/sync_jobs`, hardcoded in
`parallel-scraper.yml` to `https://web-production-110bb.up.railway.app`. With nothing at that URL,
re-enabling the workflow produces green runs that upload into the void. **Restoring a backend is a
prerequisite, not a follow-up.**

Current workflow states:

| Workflow | State | Action |
|---|---|---|
| `parallel-scraper.yml` | `disabled_inactivity` | re-enable **after** a backend exists |
| `daily-analytics.yml` | `disabled_manually` | needs `DATABASE_URL` + `SLACK_WEBHOOK_URL` |
| `start-vm.yml` | `disabled_inactivity` | leftover Azure VM starter, unrelated to the product |
| `test-scraper.yml` | active (manual) | **usable right now — needs no backend** |
| `backfill-countries.yml` | active (manual) | writes via `DATABASE_URL` directly |

---

## 0. Time-sensitive: try to rescue the database

Do this before anything else, because the window closes on its own.

Everything user-facing existed **only** in the Railway Postgres. The committed
`jobs_database.json` is jobs-only, in the pre-multi-user format, and months stale — it is not a
backup of any of this:

| Table | Contents | Backed up anywhere? |
|---|---|---|
| `users` | accounts, password hashes | **no** |
| `user_preferences` | per-user countries + job types | **no** |
| `user_job_interactions` | who applied to / rejected what | **no** |
| `user_cv_data` | uploaded CVs and parsed fields | **no** |
| `interview_tracker` | application pipeline, recruiter contacts, notes | **no** |
| `user_rewards` / `user_badges` | points, streaks, badges | **no** |
| `job_signatures` | dedup state | **no** |
| `jobs` | job listings | partially — stale JSON in git |

Log into Railway and check whether the Postgres volume still exists. Hosts generally suspend
before they delete, and there may be a grace period, but do not rely on that — check today. If the
database is still there in any form, **`pg_dump` it before touching anything else**:

```bash
pg_dump "$DATABASE_URL" > jobscrapper-backup-$(date +%F).sql   # do NOT commit this file
```

That dump makes every option below reversible. Without it, restoring service means every user
re-registers from scratch and all application history is gone.

---

## 1. Decide where the backend lives

What actually has to be hosted is smaller than it looks:

- a **stateless** FastAPI app (`railway_server.py`) that also serves the built React files
- a **real Postgres** — the code uses JSONB, window functions, `TIMESTAMPTZ` and asyncpg, so
  SQLite is not a drop-in
- a **public HTTPS URL** for GitHub Actions to POST to

No Chrome, no Selenium, no persistent disk on the server — all scraping happens on GitHub's
runners. That keeps the hosting requirement modest and portable.

Broad options, roughly in order of effort:

| Option | Effort | Notes |
|---|---|---|
| Pay Railway again | lowest | everything is already configured for it; may also bring the data back |
| App host + separate managed Postgres | moderate | a container/Python host plus a managed Postgres provider; `DATABASE_URL` is the only wiring |
| Scraper writes straight to Postgres, no web app | larger code change | keeps *collecting* jobs while the UI stays down — see below |
| Stay off | none | jobs stop accumulating; LinkedIn listings expire anyway |

Check current free-tier terms yourself before committing — they move around, and this app needs
the Postgres to persist rather than reset.

**On the third option:** `backfill-countries.yml` already proves the pattern — it runs a script
against `DATABASE_URL` with no web app involved. But `daily_single_country_scraper.py` uploads
over HTTP only (`/sync_jobs`, then a queue worker inside the server), so pointing it at a database
directly is a real code change, not a config flag. Worth it only if you want data collection to
continue while the UI stays down.

### If you rebuild the database from scratch

`database_setup.sql` creates `jobs` and the rewards/tracker tables, but it references `users`,
which is created by `database_migrations/001_add_multi_user_support.sql`. Run the migrations in
order first (`001` → `002` → `003`), then `database_setup.sql`. The app also creates
`user_activity_events` and `job_upload_queue` itself on startup.

`jobs_database.json` can reseed the `jobs` table, but those listings are from months ago and
mostly expired — probably not worth importing.

---

## 2. Do the LinkedIn selectors still work?

Worth doing **regardless of the hosting decision**, and it needs no backend at all — this is the
one useful thing you can do right now.

Run **Actions → "Test Scraper (Dry Run)" → Ireland**, `min_jobs_expected: 5`. It scrapes for real,
skips all DB writes, uploads results as an artifact, and fails loudly on low counts. Check the
sample titles in the step summary — they should look like real jobs.

If it returns 0, the scraper already detects the auth wall (`/login`, `/checkpoint`, `/authwall`
at `linkedin_job_scraper.py:224-247`) — check the log for that before assuming the selectors
broke. After 2.5 months, selector drift is likely; **if this fails, the hosting question is moot
until the scraper is fixed.** Cheap test, run it first.

---

## 3. Once a backend exists

```bash
curl -s https://<your-new-host>/health
# want: {"status":"healthy","database":"postgresql"}
```

`"database":"json_fallback"` means `DATABASE_URL` is unset or unreachable — `database_models.py:211`
silently flips `use_postgres = False` and serves the stale committed JSON while every write is
lost. It looks healthy. It is not. This is the failure mode most likely to waste a day.

Then update **both** places the old URL is hardcoded:

- `parallel-scraper.yml` — `RAILWAY_URL` (upload target) and `API_BASE_URL` (active-users check),
  plus the `curl` calls in the cleanup job
- `get_scraping_targets.py:17` — default `api_base_url`

Better: make them a repo variable rather than three hardcoded copies.

Finally, confirm at least one **active** user exists with countries and job types set —
`parallel-scraper.yml` calls `/api/admin/scraping-targets` first and silently skips the entire run
if there are none. On a rebuilt database that will be the default state.

### Expect a big trim on the first cleanup run

`enforce-country-limit` protects everything scraped in the last 72 hours and trims what's older to
**60 jobs per (country, job_type)** — 1,000 for software, 100 for marketing. Correct behavior, but
on restored-from-backup data everything is older than 72h. The workflow does skip cleanup entirely
if the scrape matrix fails, which protects the board from the worse case.

(Aside: the README's "maximum 300 jobs" and the `{"max_jobs": 300}` the workflow POSTs are both
dead — `max_jobs` is a query param the SQL never reads.)

---

## 4. Secrets to recreate

Whatever host you land on, these have to exist again.

Settings → Secrets and variables → Actions:

| Secret | Used by | If missing |
|---|---|---|
| `DATABASE_URL` | daily-analytics, backfill-countries | those workflows fail; **scraper unaffected** (it goes via the API) |
| `SLACK_WEBHOOK_URL` | scraper cleanup job, daily-analytics | notifications silently skipped, scraping still works |
| `SENTRY_DSN` | scraper, test-scraper | error tracking off, scraping still works |
| `AZURE_CREDENTIALS` | start-vm | that workflow fails daily |

On the app host, these service variables:

| Variable | Consequence if unset |
|---|---|
| `DATABASE_URL` | **silent JSON fallback — see step 3** |
| `JWT_SECRET_KEY` | falls back to the literal `"your-secret-key-change-this-in-production"` (`auth_utils.py:20`). Anyone can forge an admin token. **Set this.** Note: changing it invalidates all existing logins. |
| `ANTHROPIC_API_KEY` | CV parsing and auto-apply field mapping return `{"error": "ANTHROPIC_API_KEY not set"}` |
| `SLACK_WEBHOOK_URL` | register/apply notifications skipped |
| `SENTRY_DSN` | error tracking off |

---

## Two landmines worth knowing before you touch the build

### Four deploy configs disagree with each other

| File | Says |
|---|---|
| `railway.json` | build: `npm install && npm run build` + `pip install -r requirements-fastapi.txt`; start: `railway_server.py` |
| `railway.toml` | start: `railway_server.py` |
| `Procfile` | web: `railway_server.py`; release: npm build |
| `nixpacks.toml` | install: `npm ci --only=production` + `requirements-fastapi.txt`; start: **`fastapi_server.py`** |

Two concrete problems if `nixpacks.toml` ever wins:

- It starts **`fastapi_server.py`**, a different, much smaller app than the one everything else
  starts. Most features would just be gone.
- `npm ci --only=production` skips devDependencies, and **vite is a devDependency** — so
  `npm run build` fails outright.

Also: `requirements-fastapi.txt` omits **`sentry-sdk`** and **`python-dotenv`**, both imported
unconditionally at `railway_server.py:21` and `:44`. Since the deploy has been working, Railway
must in practice also be installing `requirements.txt` (Nixpacks' default Python install phase) or
using a build command set in the dashboard. Verify which — the moment you change the build config,
this turns into an ImportError at boot.

**Don't fix this speculatively while turning the system back on.** Confirm what Railway actually
runs (dashboard → service → Settings → Build/Deploy), then delete the configs that aren't it.

### A failed frontend build crashes the backend

`railway_server.py:196` mounts static assets like this:

```python
if os.path.exists("job-manager-ui/dist"):
    app.mount("/assets", StaticFiles(directory="job-manager-ui/dist/assets"), ...)
```

`dist/index.html` and `dist/vite.svg` are committed to git, but `dist/assets/` is gitignored. So
the guard passes on a fresh clone while the directory it mounts doesn't exist — and `StaticFiles`
raises `RuntimeError: Directory ... does not exist` at import time (verified). If the npm build is
ever skipped or fails, you don't get an API-only server; you get no server at all.

---

## Security — this repo is public

The outage is, awkwardly, the best moment to fix these — a rebuild is the one time changing
credentials and locking endpoints costs nothing.

**Account passwords are in public source.** `railway_server.py:1949, 2049, 2153` and the
`create_*_user.py` scripts contain real credentials: `glo` / `GloSecure2024!`, `sales` /
`SalesPro2024!`, `finance` / `FinancePro2024!`, and several accounts on `pass123`. They stop
mattering the moment the old database is gone — but they start mattering again the moment you
recreate those accounts, because the seeding scripts reuse the same strings. Change the values,
don't just delete the lines: git history keeps them either way.

**25 of 50 endpoints have no authentication.** Combined with `allow_origins=["*"]`
(`railway_server.py:187`), any origin can call them. The destructive ones:

| Endpoint | Effect |
|---|---|
| `DELETE /api/jobs/clear-all` | wipes the jobs table |
| `DELETE /api/jobs/by-country/{country}` | wipes one country |
| `POST /api/jobs/enforce-country-limit` | mass delete |
| `POST /sync_jobs` | inject arbitrary jobs into everyone's board |
| `POST /api/admin/create-{glo,sales,finance}-user` | create accounts with the known passwords above |
| `GET /api/admin/user-activity`, `GET /api/admin/analytics` | exposes usernames and activity |
| `GET /jobs_database.json` | dumps the job database |

`/sync_jobs` is the one the scraper depends on, so it needs a shared token rather than a blanket
block. The rest should move behind the same `Depends(get_current_user)` + `is_admin` check the
other 25 endpoints already use.

**`jobs_database.json` is committed** — 5.8 MB, 6,435 jobs, 907 flagged as applied — and it's real
user activity in a public repo.

---

## Flipping the switch

Only once a backend is up and answering `/health` with `"database":"postgresql"`:

1. Point the workflow at the new URL (three hardcoded copies — see step 3).
2. Actions → "Optimized Job Scraper (Active Users Only)" → **Enable workflow**.
3. Trigger it manually first (`workflow_dispatch` → Ireland) rather than waiting for cron. Manual
   runs skip the active-users check, so this tests the scrape+upload path in isolation.
4. Watch for: matrix jobs green, `[API] Chunk n/n` upload lines in the log, Slack summary arrives.
5. Confirm the jobs actually landed — `GET /api/jobs` count should climb, and the board should
   show today's dates. Green runs prove nothing on their own; the upload is fire-and-forget
   enough that it will look fine while writing nowhere.
6. Only then let the schedule run (7×/day, 18 locations, `max-parallel: 11`).

Note the cron is in UTC (`0 9,11,13,15,16,18,20 * * *`) despite the "Dublin time" comment — during
Irish Summer Time these fire an hour later than the comment claims. Cosmetic.

Re-enabling does not permanently fix the 60-day auto-disable. Any repo activity resets the clock;
if the repo goes quiet for another 60 days, GitHub will switch it off again — which is exactly
what happened in June.
