#!/usr/bin/env python3
"""
Create a user account with preferences, without putting credentials in the repo.

The create_*_user.py scripts in this repository each hardcode a real email
address and a plaintext password ("pass123" in several) in a PUBLIC repository.
This replaces that pattern: the account details are arguments, and the password
is read from the TEMP_PASSWORD secret and never printed.

Output names the new user id only, not their email or name, because this runs
in GitHub Actions where the logs are world-readable.

Dry-run by default. --apply writes.

    python3 create_user.py --username leonie --email … --full-name "…" \
        --job-types sustainability --countries Germany --cities Hamburg \
        --enforce-city-filter --experience-levels entry,junior,mid
"""

import argparse
import asyncio
import os
import sys


def csv_arg(value):
    return [v.strip() for v in value.split(',') if v.strip()] if value else []


async def main():
    p = argparse.ArgumentParser(description='Create a user with preferences')
    p.add_argument('--username', required=True)
    p.add_argument('--email', required=True)
    p.add_argument('--full-name', default=None)
    p.add_argument('--job-types', type=csv_arg, default=[])
    p.add_argument('--countries', type=csv_arg, default=[])
    p.add_argument('--cities', type=csv_arg, default=[])
    p.add_argument('--enforce-city-filter', action='store_true',
                   help='Apply --cities. Needs migration 007.')
    p.add_argument('--experience-levels', type=csv_arg, default=[])
    p.add_argument('--keywords', type=csv_arg, default=[])
    p.add_argument('--apply', action='store_true', help='Write (default is dry-run)')
    args = p.parse_args()

    if not os.environ.get('DATABASE_URL'):
        print("[ERROR] DATABASE_URL not set")
        return 2

    password = os.environ.get('NEW_PASSWORD') or ''
    if not password:
        print("[ERROR] NEW_PASSWORD is empty — set the TEMP_PASSWORD secret.")
        return 2

    from auth_utils import validate_password_strength, validate_email, validate_username
    for label, check, value in (('username', validate_username, args.username),
                                ('email', validate_email, args.email),
                                ('password', validate_password_strength, password)):
        ok, err = check(value)
        if not ok:
            # Never echo the value — one of them is the password.
            print(f"[ERROR] Invalid {label}: {err}")
            return 2

    prefs = {}
    if args.job_types:
        prefs['job_types'] = args.job_types
    if args.countries:
        prefs['preferred_countries'] = args.countries
    if args.cities:
        prefs['preferred_cities'] = args.cities
    if args.experience_levels:
        prefs['experience_levels'] = args.experience_levels
    if args.keywords:
        prefs['keywords'] = args.keywords
    if args.enforce_city_filter:
        prefs['enforce_city_filter'] = True

    print(f"[PLAN] username={args.username}")   # username only; email is PII
    for k, v in prefs.items():
        print(f"       {k}={v}")

    if args.cities and not args.enforce_city_filter:
        print("[WARN] cities set without --enforce-city-filter, so they are ignored.")

    from user_database import UserDatabase
    db = UserDatabase()
    if not db.use_postgres:
        print("[ERROR] DATABASE_URL is set but UserDatabase is not using postgres")
        return 2

    # enforce_city_filter arrives in migration 007. Check before creating the
    # account, so a missing column fails cleanly instead of leaving a half
    # configured user behind.
    if args.enforce_city_filter:
        conn = await db.get_connection()
        if not conn:
            print("[ERROR] Could not connect to the database")
            return 2
        try:
            exists = await conn.fetchval(
                """SELECT EXISTS (
                       SELECT 1 FROM information_schema.columns
                       WHERE table_name = 'user_preferences'
                         AND column_name = 'enforce_city_filter'
                   )"""
            )
        finally:
            if hasattr(db, '_release'):
                await db._release(conn)
        if not exists:
            print("[ERROR] enforce_city_filter column does not exist.")
            print("        Apply 007_add_enforce_city_filter.sql first, then re-run.")
            return 2

    if not args.apply:
        print("[DRY-RUN] Nothing written. Re-run with apply ticked.")
        return 0

    user = await db.create_user(
        username=args.username,
        email=args.email,
        password=password,
        full_name=args.full_name,
    )
    if not user:
        print("[ERROR] Could not create the account — that username or email already exists.")
        return 1

    uid = user['id']
    print(f"[SAVED] user id {uid} created")

    if prefs:
        ok = await db.update_user_preferences(uid, prefs)
        print(f"[SAVED] preferences written" if ok else "[ERROR] preferences NOT written")
        if not ok:
            return 1

    conn = await db.get_connection()
    if conn:
        try:
            row = await conn.fetchrow(
                """SELECT job_types, preferred_countries, preferred_cities,
                          experience_levels, keywords
                   FROM user_preferences WHERE user_id = $1""", uid)
            if row:
                print(f"[VERIFY] job_types={list(row['job_types'] or [])}")
                print(f"[VERIFY] countries={list(row['preferred_countries'] or [])}")
                print(f"[VERIFY] cities={list(row['preferred_cities'] or [])}")
                print(f"[VERIFY] levels={list(row['experience_levels'] or [])}")
                print(f"[VERIFY] keywords={list(row['keywords'] or [])}")
        finally:
            if hasattr(db, '_release'):
                await db._release(conn)

    print("[NOTE] The password is the TEMP_PASSWORD secret and is deliberately not shown.")
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
