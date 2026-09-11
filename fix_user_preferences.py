#!/usr/bin/env python3
"""
Set a user's job preferences from their own parsed CV.

Registration seeds user_preferences from the column defaults in
001_add_multi_user_support.sql (job_types=['software'],
preferred_countries=['Ireland'], experience_levels=entry/junior/mid), and
onboarding writes user_scraper_configs — a table nothing reads. So a user whose
CV says "Mechanical Engineer" still gets filtered down to junior software roles
in Ireland.

This reads what the CV parser already extracted (user_cv_data.insights) plus the
country picked during onboarding, and writes real values into user_preferences —
the table that /api/jobs and /api/admin/scraping-targets actually read.

Dry-run by default. Pass --apply to write.

    python3 fix_user_preferences.py --user kashish
    python3 fix_user_preferences.py --user kashish --apply
    python3 fix_user_preferences.py --user kashish --job-types engineering,software --apply

Output is deliberately PII-free (user id, not name/email) because this runs in
GitHub Actions on a public repository.
"""

import argparse
import asyncio
import json
import os
import sys

import asyncpg

# Job types the UI offers (SettingsPage.tsx) — anything written here must be one
# of these, or the Settings checkboxes won't reflect it.
VALID_JOB_TYPES = [
    'software', 'hr', 'cybersecurity', 'sales', 'finance',
    'marketing', 'data', 'design', 'biotech', 'engineering', 'events',
]
VALID_LEVELS = ['entry', 'junior', 'mid', 'senior', 'executive']

# Maps CV free text (target_roles, current_title, industries, top_skills) onto
# those job types. First match wins per phrase; a CV can land on several types.
TYPE_KEYWORDS = {
    'engineering':   ['mechanical', 'manufacturing', 'process engineer', 'design engineer',
                      'quality engineer', 'production', 'aerospace', 'automotive', 'civil',
                      'electrical engineer', 'industrial', 'maintenance engineer', 'cad',
                      'solidworks', 'autocad', 'matlab', 'lean', 'six sigma'],
    'software':      ['software', 'developer', 'programmer', 'full stack', 'backend',
                      'frontend', 'devops', 'sre', 'cloud engineer', 'mobile developer',
                      'web developer', 'python', 'java', 'javascript', 'react', '.net'],
    'data':          ['data scientist', 'data analyst', 'data engineer', 'machine learning',
                      'analytics', 'bi analyst', 'business intelligence'],
    'cybersecurity': ['security', 'cyber', 'soc analyst', 'infosec', 'penetration',
                      'incident response', 'vulnerability'],
    'finance':       ['finance', 'accountant', 'accounting', 'financial analyst', 'audit',
                      'treasury', 'fp&a', 'investment', 'tax'],
    'hr':            ['human resources', 'recruiter', 'recruitment', 'talent acquisition',
                      'people operations', 'hr generalist', 'hr business partner'],
    'sales':         ['sales', 'account executive', 'account manager', 'business development',
                      'customer success', 'revenue'],
    'marketing':     ['marketing', 'seo', 'content', 'social media', 'brand', 'campaign',
                      'communications', 'public relations', 'copywriter'],
    'biotech':       ['biotech', 'life science', 'laboratory', 'lab scientist', 'research scientist',
                      'molecular', 'clinical', 'pharma', 'crispr', 'cell culture'],
    'design':        ['ux', 'ui designer', 'product designer', 'graphic design', 'figma'],
    'events':        ['event manager', 'event coordinator', 'conference', 'hospitality',
                      'venue', 'catering', 'wedding planner'],
}

# insights.seniority is finer-grained than user_preferences.experience_levels.
SENIORITY_TO_LEVELS = {
    'intern':    ['entry'],
    'junior':    ['entry', 'junior'],
    'mid':       ['junior', 'mid'],
    'senior':    ['mid', 'senior'],
    'lead':      ['senior', 'executive'],
    'principal': ['senior', 'executive'],
    'director':  ['senior', 'executive'],
    'executive': ['executive'],
}


def derive_job_types(insights):
    """Match CV text against TYPE_KEYWORDS. Returns types ordered by hit count."""
    phrases = []
    for field in ('target_roles', 'industries', 'top_skills', 'primary_tech_stack'):
        val = insights.get(field) or []
        if isinstance(val, list):
            phrases += [p for p in val if isinstance(p, str)]
    for field in ('current_title', 'highest_education'):
        val = insights.get(field)
        if isinstance(val, str):
            phrases.append(val)

    haystack = ' | '.join(phrases).lower()
    scored = []
    for job_type, keywords in TYPE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in haystack)
        if hits:
            scored.append((hits, job_type))
    scored.sort(reverse=True)
    return [job_type for _, job_type in scored]


def derive_levels(insights):
    seniority = (insights.get('seniority') or '').strip().lower()
    return SENIORITY_TO_LEVELS.get(seniority, [])


def csv_arg(value):
    return [v.strip() for v in value.split(',') if v.strip()] if value else []


async def find_user(conn, selector):
    """Look up by numeric id, then exact username, then a fuzzy name/email match."""
    if selector.isdigit():
        row = await conn.fetchrow(
            "SELECT id, is_active FROM users WHERE id = $1", int(selector))
        if row:
            return [row]

    rows = await conn.fetch(
        "SELECT id, is_active FROM users WHERE lower(username) = lower($1)", selector)
    if rows:
        return rows

    return await conn.fetch(
        """
        SELECT id, is_active FROM users
        WHERE username ILIKE '%' || $1 || '%'
           OR full_name ILIKE '%' || $1 || '%'
           OR email     ILIKE '%' || $1 || '%'
        ORDER BY id
        """,
        selector,
    )


async def main():
    parser = argparse.ArgumentParser(description="Set a user's preferences from their CV")
    parser.add_argument('--user', required=True,
                        help='User id, username, or part of their name/email')
    parser.add_argument('--apply', action='store_true',
                        help='Write the change (default is dry-run)')
    parser.add_argument('--job-types', type=csv_arg, default=[],
                        help='Override the CV-derived job types, comma separated')
    parser.add_argument('--countries', type=csv_arg, default=[],
                        help='Override the onboarding country, comma separated')
    parser.add_argument('--experience-levels', type=csv_arg, default=[],
                        help='Override the CV-derived experience levels, comma separated')
    parser.add_argument('--keywords', type=csv_arg, default=[],
                        help='Extra LinkedIn search terms for this user, comma separated. '
                             '/api/admin/scraping-targets aggregates these into the scrape, '
                             'so they widen what gets collected, not just what is shown.')
    args = parser.parse_args()

    for name, values, allowed in (
        ('job type', args.job_types, VALID_JOB_TYPES),
        ('experience level', args.experience_levels, VALID_LEVELS),
    ):
        bad = [v for v in values if v not in allowed]
        if bad:
            print(f"[ERROR] Unknown {name}(s): {', '.join(bad)}")
            print(f"        Valid values: {', '.join(allowed)}")
            return 2

    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL not set")
        return 2

    conn = await asyncpg.connect(db_url, command_timeout=30)
    try:
        matches = await find_user(conn, args.user)
        if not matches:
            print(f"[ERROR] No user matched '{args.user}'")
            return 1
        if len(matches) > 1:
            ids = ', '.join(str(m['id']) for m in matches)
            print(f"[ERROR] '{args.user}' matched {len(matches)} users (ids: {ids})")
            print("        Re-run with the exact user id.")
            return 1

        user_id = matches[0]['id']
        print(f"[INFO] User id {user_id} (active={matches[0]['is_active']})")

        current = await conn.fetchrow(
            """SELECT job_types, preferred_countries, experience_levels, keywords
               FROM user_preferences WHERE user_id = $1""",
            user_id,
        )
        if not current:
            print(f"[ERROR] No user_preferences row for user {user_id}")
            return 1

        print(f"[CURRENT] job_types={list(current['job_types'] or [])} "
              f"countries={list(current['preferred_countries'] or [])} "
              f"levels={list(current['experience_levels'] or [])}")

        # CV insights — the column is added at runtime by cv_routes.py, so it may
        # be absent on an older database.
        insights = {}
        try:
            cv_row = await conn.fetchrow(
                "SELECT insights FROM user_cv_data WHERE user_id = $1", user_id)
            if cv_row and cv_row['insights']:
                raw = cv_row['insights']
                insights = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except asyncpg.UndefinedColumnError:
            print("[WARN] user_cv_data has no insights column — CV parsing never ran here")
        except asyncpg.UndefinedTableError:
            print("[WARN] user_cv_data table does not exist")

        if insights:
            print(f"[CV] seniority={insights.get('seniority')} "
                  f"target_roles={len(insights.get('target_roles') or [])} "
                  f"industries={len(insights.get('industries') or [])}")
        else:
            print("[CV] No parsed CV insights for this user")

        # Country comes from what they picked during onboarding.
        onboarding_country = None
        try:
            row = await conn.fetchrow(
                """SELECT country FROM user_scraper_configs
                   WHERE user_id = $1 AND active = TRUE
                   ORDER BY updated_at DESC LIMIT 1""",
                user_id,
            )
            if row:
                onboarding_country = row['country']
        except asyncpg.UndefinedTableError:
            pass

        job_types = args.job_types or derive_job_types(insights)
        levels = args.experience_levels or derive_levels(insights)
        countries = args.countries or ([onboarding_country] if onboarding_country else [])

        if not job_types:
            print("[ERROR] Could not derive any job type from the CV.")
            print("        Re-run with --job-types, e.g. --job-types engineering,software")
            print(f"        Valid values: {', '.join(VALID_JOB_TYPES)}")
            return 1

        updates, values = [], []
        for column, value in (('job_types', job_types),
                              ('preferred_countries', countries),
                              ('experience_levels', levels),
                              ('keywords', args.keywords)):
            if value:
                values.append(value)
                updates.append(f"{column} = ${len(values)}")

        print(f"[PROPOSED] job_types={job_types} countries={countries or '(unchanged)'} "
              f"levels={levels or '(unchanged)'} "
              f"keywords={args.keywords or '(unchanged)'}")

        if not args.apply:
            print("[DRY-RUN] Nothing written. Re-run with --apply to save.")
            return 0

        values.append(user_id)
        await conn.execute(
            f"UPDATE user_preferences SET {', '.join(updates)}, "
            f"updated_at = CURRENT_TIMESTAMP WHERE user_id = ${len(values)}",
            *values,
        )

        saved = await conn.fetchrow(
            """SELECT job_types, preferred_countries, experience_levels, keywords
               FROM user_preferences WHERE user_id = $1""",
            user_id,
        )
        print(f"[SAVED] job_types={list(saved['job_types'])} "
              f"countries={list(saved['preferred_countries'])} "
              f"levels={list(saved['experience_levels'])} "
              f"keywords={list(saved['keywords'] or [])}")
        print("[INFO] Takes effect on her next page load — /api/jobs filters per request.")
        return 0
    finally:
        await conn.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
