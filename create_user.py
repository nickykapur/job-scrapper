#!/usr/bin/env python3
"""
Create a user account with preferences, without putting credentials in the repo.

The create_*_user.py scripts in this repository each hardcode a real email
address and a plaintext password ("pass123" in several) in a PUBLIC repository.
This replaces that pattern: account details are arguments, and the password is
either the TEMP_PASSWORD secret or a strong random one generated here. Either
way it is never printed, because Actions logs on this repository are public.

Deliberately talks to the database with asyncpg and hashes with passlib
directly, exactly as reset_user_password.py does. Importing user_database would
pull in auth_utils, which imports python-jose AND fastapi, so the whole web
stack would have to be installed in the runner to insert one row.
CryptContext(schemes=["bcrypt"], deprecated="auto") is identical to the one in
auth_utils, so the hash written here is what the app expects.

Dry-run by default. --apply writes.
"""

import argparse
import asyncio
import os
import re
import secrets
import sys
from datetime import datetime

import asyncpg
from passlib.context import CryptContext

# Must match auth_utils.pwd_context, or nobody can log in with what we write.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def csv_arg(value):
    return [v.strip() for v in value.split(',') if v.strip()] if value else []


def generate_password():
    """16 chars, guaranteed a letter and a digit, no I O l 0 1 to misread."""
    alphabet = ('ABCDEFGHJKLMNPQRSTUVWXYZ'
                'abcdefghijkmnopqrstuvwxyz'
                '23456789')
    return (secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')
            + secrets.choice('23456789')
            + ''.join(secrets.choice(alphabet) for _ in range(14)))


# The same three rules as auth_utils.validate_password_strength, restated rather
# than imported for the reason given in the module docstring.
def check_password(pw):
    if len(pw) < 8:
        return False, "must be at least 8 characters"
    if not re.search(r'[a-zA-Z]', pw):
        return False, "must contain a letter"
    if not re.search(r'\d', pw):
        return False, "must contain a number"
    return True, ""


def check_username(name):
    if not re.fullmatch(r'[A-Za-z0-9_]{3,50}', name or ''):
        return False, "3-50 characters, letters, numbers and underscore only"
    return True, ""


def check_email(addr):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}", addr or ''):
        return False, "not a valid email address"
    return True, ""


async def main():
    p = argparse.ArgumentParser(description='Create a user with preferences')
    p.add_argument('--username', required=True)
    p.add_argument('--email', required=True)
    p.add_argument('--full-name', default=None)
    p.add_argument('--job-types', type=csv_arg, default=[])
    p.add_argument('--countries', type=csv_arg, default=[])
    p.add_argument('--cities', type=csv_arg, default=[])
    p.add_argument('--enforce-city-filter', action='store_true')
    p.add_argument('--experience-levels', type=csv_arg, default=[])
    p.add_argument('--keywords', type=csv_arg, default=[])
    p.add_argument('--apply', action='store_true', help='Write (default is dry-run)')
    args = p.parse_args()

    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL not set")
        return 2

    password = os.environ.get('NEW_PASSWORD') or ''
    generated = not password
    if generated:
        password = generate_password()

    for label, check, value in (('username', check_username, args.username),
                                ('email', check_email, args.email),
                                ('password', check_password, password)):
        ok, err = check(value)
        if not ok:
            print(f"[ERROR] Invalid {label}: {err}")   # never echo the value
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

    conn = await asyncpg.connect(db_url, command_timeout=30)
    try:
        if args.enforce_city_filter:
            exists = await conn.fetchval(
                """SELECT EXISTS (
                       SELECT 1 FROM information_schema.columns
                       WHERE table_name = 'user_preferences'
                         AND column_name = 'enforce_city_filter'
                   )"""
            )
            if not exists:
                print("[ERROR] enforce_city_filter column does not exist.")
                print("        Apply 007_add_enforce_city_filter.sql first, then re-run.")
                return 2

        clash = await conn.fetchrow(
            "SELECT id FROM users WHERE lower(username) = lower($1) OR lower(email) = lower($2)",
            args.username, args.email)
        if clash:
            print(f"[ERROR] username or email already belongs to user id {clash['id']}")
            return 1

        if not args.apply:
            print("[DRY-RUN] Nothing written. Re-run with apply ticked.")
            return 0

        # One transaction: an account without preferences is worse than none.
        async with conn.transaction():
            user_id = await conn.fetchval(
                """INSERT INTO users (username, email, password_hash, full_name, is_admin)
                   VALUES ($1, $2, $3, $4, FALSE)
                   RETURNING id""",
                args.username, args.email, pwd_context.hash(password), args.full_name)

            # Seed the preferences row the same way create_user does, then set
            # the real values on top of the column defaults.
            await conn.execute(
                "INSERT INTO user_preferences (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
                user_id)

            if prefs:
                cols, values = [], []
                for col, val in prefs.items():
                    values.append(val)
                    cols.append(f"{col} = ${len(values)}")
                values.append(user_id)
                await conn.execute(
                    f"UPDATE user_preferences SET {', '.join(cols)}, "
                    f"updated_at = CURRENT_TIMESTAMP WHERE user_id = ${len(values)}",
                    *values)

        print(f"[SAVED] user id {user_id} created")

        row = await conn.fetchrow(
            """SELECT job_types, preferred_countries, preferred_cities,
                      experience_levels, keywords, enforce_city_filter
               FROM user_preferences WHERE user_id = $1""", user_id)
        print(f"[VERIFY] job_types={list(row['job_types'] or [])}")
        print(f"[VERIFY] countries={list(row['preferred_countries'] or [])}")
        print(f"[VERIFY] cities={list(row['preferred_cities'] or [])}")
        print(f"[VERIFY] levels={list(row['experience_levels'] or [])}")
        print(f"[VERIFY] keywords={list(row['keywords'] or [])}")
        print(f"[VERIFY] enforce_city_filter={row['enforce_city_filter']}")

        active = await conn.fetchval("SELECT is_active FROM users WHERE id = $1", user_id)
        print(f"[VERIFY] is_active={active}  (must be true for the scraper to "
              f"pick up these job types)")

        if generated:
            print("[NOTE] A random 16-character password was generated and NOT printed —")
            print("       this log is public. To issue one they can use:")
            print("       Admin -> Users -> Password -> Generate, then Copy.")
        else:
            print("[NOTE] The password is the TEMP_PASSWORD secret, deliberately not shown.")
        return 0
    finally:
        await conn.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
