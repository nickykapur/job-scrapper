# Turn-On Checklist

What to verify before re-enabling automated scraping.

## Situation

This system is not un-launched — it ran successfully **1,544 times** and then stopped.

| Fact | Value |
|---|---|
| Last successful scrape | run #1544, **2026-06-24 17:49 UTC** |
| Why it stopped | GitHub set `parallel-scraper.yml` to `disabled_inactivity` (scheduled workflows are auto-disabled after 60 days without repo activity) |
| Time since | ~2.5 months |
| Repo visibility | **public** (so Actions minutes are free — no quota concern) |

So "turning it on" = re-enabling a disabled workflow, and the real risk is **drift** over the
2.5 months it was off, not first-time setup.

Current workflow states:

| Workflow | State | Action |
|---|---|---|
| `parallel-scraper.yml` | `disabled_inactivity` | **the one to re-enable** |
| `daily-analytics.yml` | `disabled_manually` | decide — needs `DATABASE_URL` + `SLACK_WEBHOOK_URL` |
| `start-vm.yml` | `disabled_inactivity` | leftover Azure VM starter, unrelated to the product — delete or confirm |
| `test-scraper.yml` | active (manual) | **use this first, see step 2** |
| `backfill-countries.yml` | active (manual) | leave alone |

---

## Verify in this order

### 1. Is the Railway backend still alive?

Everything hangs off this. The scraper does not write to Postgres directly — it POSTs to
`$RAILWAY_URL/sync_jobs`, and `parallel-scraper.yml` has the URL **hardcoded** to
`https://web-production-110bb.up.railway.app`. If the service was torn down, slept, or got a new
domain in the last 2.5 months, every scrape run will "succeed" while uploading nothing.

```bash
curl -s https://web-production-110bb.up.railway.app/health
# want: {"status":"healthy","database":"postgresql"}
```

- `"database":"json_fallback"` → **stop.** `DATABASE_URL` is unset or unreachable, and
  `database_models.py:211` silently flips `use_postgres = False`. The server then serves the
  stale committed `jobs_database.json` (6,435 jobs from months ago) and every write is lost. It
  looks alive. It is not.
- Anything else (502 / no response) → fix Railway before touching the workflow.

Also confirm the Postgres instance itself still exists — a deleted/expired DB is the most likely
casualty of a 2.5-month idle period.

### 2. Do the LinkedIn selectors still work?

The highest-probability drift. LinkedIn changes its DOM constantly, and the scraper has been
blind for 2.5 months. **Do not skip this — it is the whole point of the dry-run workflow.**

Run **Actions → "Test Scraper (Dry Run)" → Ireland**, `min_jobs_expected: 5`.

It scrapes for real but skips all DB writes, uploads the results as an artifact, and fails loudly
if too few jobs come back. Check the step summary: sample job titles should look like real jobs,
not empty strings or nav text.

If it returns 0 jobs, `linkedin_job_scraper.py` already detects the auth wall
(`/login`, `/checkpoint`, `/authwall` at lines 224–247) — check the log for that before assuming
the selectors broke.

### 3. Is there at least one active user?

`parallel-scraper.yml` calls `get_scraping_targets.py` → `/api/admin/scraping-targets` first, and
**skips the entire run if zero active users**. It will report success and do nothing.

```bash
curl -s https://web-production-110bb.up.railway.app/api/admin/scraping-targets
```

Confirm `active_users_count > 0` and that the returned countries/job types are the ones you
actually want scraped — that response, not the workflow file, decides what gets searched.

### 4. Secrets still present

Settings → Secrets and variables → Actions:

| Secret | Used by | If missing |
|---|---|---|
| `DATABASE_URL` | daily-analytics, backfill-countries | those workflows fail; **scraper unaffected** (it goes via the API) |
| `SLACK_WEBHOOK_URL` | scraper cleanup job, daily-analytics | notifications silently skipped, scraping still works |
| `SENTRY_DSN` | scraper, test-scraper | error tracking off, scraping still works |
| `AZURE_CREDENTIALS` | start-vm | that workflow fails daily |

On Railway, confirm these service variables:

| Variable | Consequence if unset |
|---|---|
| `DATABASE_URL` | **silent JSON fallback — see step 1** |
| `JWT_SECRET_KEY` | falls back to the literal `"your-secret-key-change-this-in-production"` (`auth_utils.py:20`). Anyone can forge an admin token. **Set this.** Note: changing it invalidates all existing logins. |
| `ANTHROPIC_API_KEY` | CV parsing and auto-apply field mapping return `{"error": "ANTHROPIC_API_KEY not set"}` |
| `SLACK_WEBHOOK_URL` | register/apply notifications skipped |
| `SENTRY_DSN` | error tracking off |

### 5. Expect the first run to delete a lot of jobs

`enforce-country-limit` protects everything scraped in the last 72 hours and trims what's older to
**60 jobs per (country, job_type)** — 1,000 for software, 100 for marketing. After 2.5 months idle,
*every* job in the DB is older than 72h, so the first cleanup will trim hard. That is correct
behavior, not a bug, but users will see a thin board until a couple of scrape cycles land.

The workflow does guard against the worse case: if the scrape matrix fails, it skips cleanup
entirely rather than wiping the board.

(Aside: the README's "maximum 300 jobs" and the `{"max_jobs": 300}` the workflow POSTs are both
dead — `max_jobs` is a query param that the SQL never reads. The per-type limits above are the
real ones.)

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

Read this before re-enabling anything, not after.

**Live account passwords are in public source.** `railway_server.py:1949, 2049, 2153` and the
`create_*_user.py` scripts contain working credentials: `glo` / `GloSecure2024!`, `sales` /
`SalesPro2024!`, `finance` / `FinancePro2024!`, and several accounts on `pass123`. Anyone can read
these and log in. Rotate every one of them. Removing the lines does not help on its own — the
values stay in git history, so the passwords must actually change.

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

1. Actions → "Optimized Job Scraper (Active Users Only)" → **Enable workflow**.
2. Trigger it manually first (`workflow_dispatch` → Ireland) rather than waiting for cron. Manual
   runs skip the active-users check, so this tests the scrape+upload path in isolation.
3. Watch for: matrix jobs green, `[API] Chunk n/n` upload lines in the log, Slack summary arrives.
4. Confirm the jobs actually landed — `GET /api/jobs` count should climb, and the board should
   show today's dates.
5. Only then let the schedule run (7×/day, 18 locations, `max-parallel: 11`).

Note the cron is in UTC (`0 9,11,13,15,16,18,20 * * *`) despite the "Dublin time" comment — during
Irish Summer Time these fire an hour later than the comment claims. Cosmetic.

Re-enabling does not permanently fix the 60-day auto-disable. Any repo activity resets the clock;
if the repo goes quiet for another 60 days, GitHub will switch it off again.
