#!/usr/bin/env python3
"""
One-off database maintenance tasks that need DATABASE_URL.

    migrate      apply a SQL file from database_migrations/
    purge-langs  delete jobs whose title is not in an acceptable language

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


async def main():
    parser = argparse.ArgumentParser(description='Database maintenance')
    parser.add_argument('task', choices=['migrate', 'purge-langs'])
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
        return await purge_languages(conn, args.apply)
    finally:
        await conn.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
