#!/usr/bin/env python3
"""
One-off database maintenance tasks that need DATABASE_URL.

    migrate      apply a SQL file from database_migrations/
    purge-langs  delete jobs whose title is not in an acceptable language
    purge-stale  trim the backlog of old jobs down to the per-country caps

Both are dry-run unless --apply is passed.

purge-langs exists because the language filter only runs at scrape time. Rows
collected while the filter still only knew engineering vocabulary are already in
the database and stay visible until something removes them.

It reuses detect_job_language from linkedin_job_scraper rather than
reimplementing it, so the cleanup and the scraper can never disagree about what
counts as English.
"""

import argparse
import asyncio
import os
import sys

import asyncpg


def load_language_detector():
    """Pull in the real detector without constructing a browser.

    linkedin_job_scraper imports selenium at module scope, so importing the
    module is fine but instantiating the class is not — we only need the one
    method, which touches no instance state.
    """
    from linkedin_job_scraper import LinkedInJobScraper
    return LinkedInJobScraper.detect_job_language.__get__(
        object.__new__(LinkedInJobScraper), LinkedInJobScraper)


async def run_migration(conn, name, apply):
    path = os.path.join('database_migrations', name)
    if not os.path.exists(path):
        print(f"[ERROR] No such migration: {path}")
        return 1

    sql = open(path).read()
    print(f"[INFO] {name} — {len(sql.splitlines())} lines")

    if not apply:
        print("[DRY-RUN] Not executed. Re-run with --apply.")
        return 0

    # Migrations here are written to be idempotent (IF NOT EXISTS / IF EXISTS),
    # so a re-run is safe. The transaction still means a failure leaves nothing
    # half-applied.
    async with conn.transaction():
        await conn.execute(sql)
    print(f"[SAVED] {name} applied")
    return 0


async def purge_languages(conn, apply):
    detect = load_language_detector()

    rows = await conn.fetch("SELECT id, title, location, country FROM jobs")
    print(f"[INFO] Scanning {len(rows)} jobs")

    doomed = []
    for row in rows:
        title = row['title'] or ''
        location = row['location'] or row['country'] or ''
        if not detect(title, location):
            doomed.append(row)

    print(f"[INFO] {len(doomed)} jobs fail the language check")

    by_country = {}
    for row in doomed:
        by_country[row['country'] or 'Unknown'] = by_country.get(row['country'] or 'Unknown', 0) + 1
    for country, n in sorted(by_country.items(), key=lambda kv: -kv[1]):
        print(f"         {country}: {n}")

    # A sample so the decision isn't blind. Titles only — no company, no URL.
    for row in doomed[:15]:
        print(f"   [DROP] {row['title'][:70]}")

    if not doomed:
        return 0

    if not apply:
        print("[DRY-RUN] Nothing deleted. Re-run with --apply.")
        return 0

    # Never delete a job somebody acted on: their applied/rejected history
    # references it, and the interview tracker may too.
    ids = [r['id'] for r in doomed]
    protected = await conn.fetchval(
        "SELECT COUNT(*) FROM user_job_interactions WHERE job_id = ANY($1::varchar[])", ids)
    if protected:
        print(f"[INFO] {protected} of these have user interactions — keeping those")

    result = await conn.execute(
        """
        DELETE FROM jobs
        WHERE id = ANY($1::varchar[])
          AND id NOT IN (SELECT job_id FROM user_job_interactions)
        """,
        ids,
    )
    print(f"[SAVED] {result}")
    return 0


# Same caps enforce-country-limit uses, so the one-off backlog trim and the
# routine per-scrape cleanup agree.
CAPS = {'software': 1000, 'marketing': 100}
DEFAULT_CAP = 60


async def purge_stale(conn, apply):
    """Trim old jobs to the per-country caps, in batches.

    enforce-country-limit does this in a single statement, which cannot finish
    inside the pool's 60s timeout against a backlog this size. Batching keeps
    each statement short.

    Unlike that endpoint, this protects jobs someone has interacted with.
    user_job_interactions.job_id is ON DELETE CASCADE, so deleting a job also
    deletes every user's applied/rejected record for it — their history would
    disappear with the listing.
    """
    total = await conn.fetchval("SELECT COUNT(*) FROM jobs")
    protected_recent = await conn.fetchval(
        "SELECT COUNT(*) FROM jobs WHERE scraped_at >= NOW() - INTERVAL '72 hours'")
    protected_used = await conn.fetchval(
        "SELECT COUNT(DISTINCT job_id) FROM user_job_interactions")
    print(f"[INFO] {total} jobs | {protected_recent} scraped in last 72h | "
          f"{protected_used} with user history")

    select_doomed = """
        SELECT id FROM (
            SELECT id, job_type,
                   ROW_NUMBER() OVER (
                       PARTITION BY country, COALESCE(job_type, 'other')
                       ORDER BY scraped_at DESC
                   ) AS rn
            FROM jobs
            WHERE scraped_at < NOW() - INTERVAL '72 hours'
              AND id NOT IN (SELECT job_id FROM user_job_interactions
                             WHERE job_id IS NOT NULL)
        ) ranked
        WHERE (job_type = 'software'  AND rn > 1000)
           OR (job_type = 'marketing' AND rn > 100)
           OR (COALESCE(job_type, 'other') NOT IN ('software', 'marketing') AND rn > 60)
        LIMIT $1
    """

    would_go = await conn.fetchval(
        f"SELECT COUNT(*) FROM ({select_doomed.replace('LIMIT $1', '')}) x")
    print(f"[INFO] {would_go} jobs are over cap and safe to remove")
    print(f"[INFO] {total - would_go} would remain")

    if not apply or not would_go:
        if not apply:
            print("[DRY-RUN] Nothing deleted. Re-run with --apply.")
        return 0

    removed = 0
    while True:
        result = await conn.execute(
            f"DELETE FROM jobs WHERE id IN ({select_doomed})", 2000)
        n = int(result.split()[-1])
        removed += n
        print(f"[INFO] deleted {removed}/{would_go}")
        if n == 0:
            break

    remaining = await conn.fetchval("SELECT COUNT(*) FROM jobs")
    print(f"[SAVED] removed {removed} jobs; {remaining} remain")
    return 0



async def diagnose(conn, user_ref):
    """Read-only. Walk the same path /api/jobs walks and count survivors.

    /api/jobs does not filter in SQL — it loads a window of jobs into memory and
    drops them one at a time in Python. When a board goes empty there is no log
    of which stage emptied it, so reproduce the stages here and print the count
    after each.
    """
    print("[STAGE 0] whole table")
    total = await conn.fetchval("SELECT COUNT(*) FROM jobs")
    print(f"  {total} rows in jobs")

    # get_all_jobs: WHERE scraped_at > NOW() - INTERVAL '7 days' LIMIT 20000.
    # Nothing outside this window can ever reach a user, whatever their prefs.
    window = await conn.fetchval(
        "SELECT COUNT(*) FROM jobs WHERE scraped_at > NOW() - INTERVAL '7 days'")
    served = min(window, 20000)
    print(f"[STAGE 1] 7-day window: {window} rows; /api/jobs serves at most {served} (LIMIT 20000)")
    if window > 20000:
        print(f"  [WARN] {window - 20000} rows in the window are past the LIMIT and never sent")

    user = await conn.fetchrow("""
        SELECT id FROM users
        WHERE CAST(id AS TEXT) = $1 OR username ILIKE $1
           OR username ILIKE '%' || $1 || '%' OR email ILIKE '%' || $1 || '%'
           OR COALESCE(full_name, '') ILIKE '%' || $1 || '%'
        ORDER BY id LIMIT 1
    """, user_ref)
    if not user:
        print(f"[ERROR] No user matched {user_ref!r}")
        return 1
    uid = user['id']
    print(f"[USER] id={uid}")   # id only — this repository is public

    prefs = await conn.fetchrow("""
        SELECT job_types, preferred_countries, experience_levels
        FROM user_preferences WHERE user_id = $1
    """, uid)
    if not prefs:
        print("  [WARN] no user_preferences row — /api/jobs returns the raw window unfiltered")
        return 0

    job_types = list(prefs['job_types'] or [])
    countries = list(prefs['preferred_countries'] or [])
    levels = list(prefs['experience_levels'] or [])
    print(f"  job_types={job_types}")
    print(f"  countries={countries}")
    print(f"  experience_levels={levels}")

    # Stage 2/3 mirror the two `continue` branches that reject a job outright.
    # A job with a NULL job_type falls through to keyword sniffing in Python, so
    # count it separately rather than pretending SQL decides it.
    n_country = await conn.fetchval("""
        SELECT COUNT(*) FROM jobs
        WHERE scraped_at > NOW() - INTERVAL '7 days'
          AND ($1::text[] IS NULL OR cardinality($1::text[]) = 0 OR country = ANY($1::text[]))
    """, countries)
    print(f"[STAGE 2] after country filter: {n_country}")

    n_type = await conn.fetchval("""
        SELECT COUNT(*) FROM jobs
        WHERE scraped_at > NOW() - INTERVAL '7 days'
          AND ($1::text[] IS NULL OR cardinality($1::text[]) = 0 OR country = ANY($1::text[]))
          AND (job_type IS NULL OR job_type = ANY($2::text[]))
    """, countries, job_types)
    typed = await conn.fetchval("""
        SELECT COUNT(*) FROM jobs
        WHERE scraped_at > NOW() - INTERVAL '7 days'
          AND ($1::text[] IS NULL OR cardinality($1::text[]) = 0 OR country = ANY($1::text[]))
          AND job_type = ANY($2::text[])
    """, countries, job_types)
    print(f"[STAGE 3] after job_type filter: {n_type} ({typed} typed + {n_type - typed} untyped)")

    print("[STAGE 4] what this user has already acted on")
    n_inter = await conn.fetchval(
        "SELECT COUNT(*) FROM user_job_interactions WHERE user_id = $1", uid)
    n_sig = await conn.fetchval(
        "SELECT COUNT(*) FROM job_signatures WHERE user_id = $1", uid)
    n_sig_active = await conn.fetchval("""
        SELECT COUNT(*) FROM job_signatures
        WHERE user_id = $1 AND (was_applied OR was_rejected)
    """, uid)
    print(f"  {n_inter} interactions, {n_sig} signatures ({n_sig_active} applied/rejected)")

    # A NULL company or normalized_title makes the signature loader raise
    # AttributeError on .lower(); the handler swallows it, so every later
    # signature is silently dropped and reposts come back.
    n_null = await conn.fetchval("""
        SELECT COUNT(*) FROM job_signatures
        WHERE user_id = $1 AND (company IS NULL OR normalized_title IS NULL)
    """, uid)
    if n_null:
        print(f"  [WARN] {n_null} signature rows have a NULL company or normalized_title")

    # Suppression matches on company + normalized_title, ignoring country.
    survivors = await conn.fetchval("""
        SELECT COUNT(*) FROM jobs j
        WHERE j.scraped_at > NOW() - INTERVAL '7 days'
          AND ($1::text[] IS NULL OR cardinality($1::text[]) = 0 OR j.country = ANY($1::text[]))
          AND (j.job_type IS NULL OR j.job_type = ANY($2::text[]))
          AND NOT EXISTS (
              SELECT 1 FROM job_signatures s
              WHERE s.user_id = $3
                AND (s.was_applied OR s.was_rejected)
                AND LOWER(s.company) = LOWER(j.company)
                AND LOWER(s.normalized_title) = LOWER(COALESCE(j.normalized_title, ''))
          )
    """, countries, job_types, uid)
    print(f"[STAGE 5] after repost suppression: {survivors}")
    print(f"[RESULT] roughly {survivors} jobs should reach user {uid} before "
          f"keyword and experience-level filtering in Python")
    return 0


async def main():
    parser = argparse.ArgumentParser(description='Database maintenance')
    parser.add_argument('task', choices=['migrate', 'purge-langs', 'purge-stale', 'diagnose'])
    parser.add_argument('--user', default='', help='User id/username/name fragment (diagnose only)')
    parser.add_argument('--migration', default='004_per_user_job_signatures.sql',
                        help='File in database_migrations/ (migrate only)')
    parser.add_argument('--apply', action='store_true', help='Write changes')
    args = parser.parse_args()

    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL not set")
        return 2

    conn = await asyncpg.connect(db_url, command_timeout=180)
    try:
        if args.task == 'migrate':
            return await run_migration(conn, args.migration, args.apply)
        if args.task == 'diagnose':
            if not args.user:
                print("[ERROR] diagnose needs --user")
                return 2
            return await diagnose(conn, args.user)
        if args.task == 'purge-stale':
            return await purge_stale(conn, args.apply)
        return await purge_languages(conn, args.apply)
    finally:
        await conn.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
