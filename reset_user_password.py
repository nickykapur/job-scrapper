#!/usr/bin/env python3
"""
Reset a user's password.

Replaces the one-off reset_password_<name>.py scripts, which each hardcoded a
password in source — this repository is public, so anything written here is
readable by anyone and can never really be un-published.

The new password is read from the NEW_PASSWORD environment variable, never from
a command-line argument (argv shows up in shell history and process listings).
Omit it and a strong random one is generated.

    # Set a specific password
    NEW_PASSWORD='...' DATABASE_URL='...' python3 reset_user_password.py --user kashish --apply

    # Let it generate one
    DATABASE_URL='...' python3 reset_user_password.py --user kashish --apply

Prefer running this on your own machine. In GitHub Actions the run log is public
on this repository, so the script refuses to print a password there — supply one
via a repository secret instead, where GitHub masks it.
"""

import argparse
import asyncio
import os
import re
import secrets
import string
import sys
from datetime import datetime

import asyncpg
from passlib.context import CryptContext

# Same scheme auth_utils.py uses, so hashes verify against the running app.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

IN_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"


def validate_password_strength(password):
    """Mirrors auth_utils.validate_password_strength.

    Worth enforcing here: a temp password that fails this policy lets her log in
    but blocks her from setting a new one via /api/auth/change-password, which
    validates. She would be stuck.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, ""


def generate_password(length=16):
    """Random password that always satisfies the policy above."""
    alphabet = string.ascii_letters + string.digits
    while True:
        candidate = ''.join(secrets.choice(alphabet) for _ in range(length))
        if validate_password_strength(candidate)[0]:
            return candidate


async def find_user(conn, selector):
    """Look up by numeric id, then exact username, then a fuzzy name/email match."""
    if selector.isdigit():
        row = await conn.fetchrow(
            "SELECT id, username, is_active FROM users WHERE id = $1", int(selector))
        if row:
            return [row]

    rows = await conn.fetch(
        "SELECT id, username, is_active FROM users WHERE lower(username) = lower($1)",
        selector)
    if rows:
        return rows

    return await conn.fetch(
        """
        SELECT id, username, is_active FROM users
        WHERE username ILIKE '%' || $1 || '%'
           OR full_name ILIKE '%' || $1 || '%'
           OR email     ILIKE '%' || $1 || '%'
        ORDER BY id
        """,
        selector,
    )


async def main():
    parser = argparse.ArgumentParser(description="Reset a user's password")
    parser.add_argument('--user', required=True,
                        help='User id, username, or part of their name/email')
    parser.add_argument('--apply', action='store_true',
                        help='Write the change (default is dry-run)')
    args = parser.parse_args()

    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL not set")
        return 2

    supplied = os.environ.get('NEW_PASSWORD') or ''
    if supplied:
        ok, err = validate_password_strength(supplied)
        if not ok:
            print(f"[ERROR] NEW_PASSWORD rejected: {err}")
            print("        She could log in but not change it later — the "
                  "change-password endpoint enforces the same rule.")
            return 2
        password, generated = supplied, False
    else:
        if IN_ACTIONS:
            print("[ERROR] No NEW_PASSWORD supplied.")
            print("        Refusing to generate one here: Actions logs are public on")
            print("        this repository, so the password would be world-readable.")
            print("        Add it as a repository secret and pass it in as NEW_PASSWORD.")
            return 2
        password, generated = generate_password(), True

    conn = await asyncpg.connect(db_url, command_timeout=30)
    try:
        matches = await find_user(conn, args.user)
        if not matches:
            print(f"[ERROR] No user matched '{args.user}'")
            return 1
        if len(matches) > 1:
            ids = ', '.join(str(m['id']) for m in matches)
            print(f"[ERROR] '{args.user}' matched {len(matches)} users (ids: {ids})")
            print("        Re-run with the exact user id — resetting the wrong "
                  "person's password locks them out.")
            return 1

        user = matches[0]
        print(f"[INFO] User id {user['id']} (active={user['is_active']})")

        if not args.apply:
            print("[DRY-RUN] Password not changed. Re-run with --apply to reset.")
            return 0

        await conn.execute(
            "UPDATE users SET password_hash = $1, updated_at = $2 WHERE id = $3",
            pwd_context.hash(password), datetime.utcnow(), user['id'],
        )
        print(f"[SAVED] Password reset for user id {user['id']}")

        if IN_ACTIONS:
            # The secret is masked by GitHub, but never rely on that — just don't
            # emit it. Whoever set the secret already knows the value.
            print("[INFO] New password not printed here (public log). It is the "
                  "value you stored in the secret.")
        else:
            print()
            print(f"    Username: {user['username']}")
            print(f"    Password: {password}")
            print()
            if generated:
                print("[INFO] Generated — copy it now, it is not stored anywhere.")
            print("[INFO] Send it over a private channel and have her change it at")
            print("       Settings, which calls /api/auth/change-password.")

        print("[INFO] Existing JWTs stay valid up to 7 days — a password reset "
              "does not invalidate them.")
        return 0
    finally:
        await conn.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
