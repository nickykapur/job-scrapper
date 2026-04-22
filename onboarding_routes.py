"""
Onboarding + scraper-config endpoints.

Self-service flow for new users:

  POST /api/auth/register-quick        — create account with default password pass1234
  GET  /api/onboarding/status          — whether the current user has finished onboarding
  POST /api/onboarding/complete        — mark onboarding complete
  GET  /api/users/me/derived-keywords  — auto-generated keywords from the parsed CV
  GET  /api/users/me/scraper-config    — current scraper config
  POST /api/users/me/scraper-config    — save country + derived keywords + complete onboarding

No endpoint here accepts free-form keywords. Keywords are always derived
from the CV (primary tech stack + target roles + seniority) server-side.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from auth_utils import (
    generate_token_response,
    get_current_user,
    validate_email,
    validate_password_strength,
)
from user_database import UserDatabase

logger = logging.getLogger(__name__)

user_db = UserDatabase()

# Default password for MVP onboarding. Users receive it in the UI and are
# encouraged to change it from Settings. This is intentional for the MVP.
DEFAULT_SIGNUP_PASSWORD = "pass1234"

# ── Schema bootstrap ────────────────────────────────────────────────────────

_CREATE_TABLES = """
ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS user_scraper_configs (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    country     TEXT NOT NULL,
    keywords    JSONB NOT NULL,
    active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, country)
);

CREATE INDEX IF NOT EXISTS idx_scraper_cfg_active ON user_scraper_configs(active);
CREATE INDEX IF NOT EXISTS idx_scraper_cfg_user   ON user_scraper_configs(user_id);
"""


async def init_onboarding_tables():
    conn = await user_db.get_connection()
    if not conn:
        print("⚠️  Onboarding table init skipped: DB unavailable")
        return
    try:
        await conn.execute(_CREATE_TABLES)
        print("✅ Onboarding tables ready")
    except Exception as e:
        print(f"⚠️  Onboarding table init error: {e}")
    finally:
        await user_db._release(conn)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _username_from_email(email: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]", "", email.split("@")[0])[:40] or "user"
    return base.lower()


async def _unique_username(email: str) -> str:
    base = _username_from_email(email)
    candidate = base
    suffix = 1
    while await user_db.get_user_by_username(candidate):
        suffix += 1
        candidate = f"{base}{suffix}"
        if suffix > 500:
            raise HTTPException(status_code=500, detail="could not allocate username")
    return candidate


async def _fetch_cv(user_id: int) -> Optional[Dict[str, Any]]:
    conn = await user_db.get_connection()
    if not conn:
        return None
    try:
        row = await conn.fetchrow("SELECT * FROM user_cv_data WHERE user_id = $1", user_id)
        if not row:
            return None
        d = dict(row)
        for k in ("skills", "experience", "education", "languages", "certifications"):
            v = d.get(k)
            if isinstance(v, str):
                try: d[k] = json.loads(v)
                except Exception: d[k] = []
        ins = d.get("insights")
        if isinstance(ins, str):
            try: d["insights"] = json.loads(ins)
            except Exception: d["insights"] = {}
        elif ins is None:
            d["insights"] = {}
        return d
    finally:
        await user_db._release(conn)


def _derive_keywords(cv: Dict[str, Any], limit: int = 8) -> List[str]:
    """Turn the parsed CV into scraper keywords.

    Priority: target_roles → primary_tech_stack → current_title.
    Never includes company names, locations, or free text.
    """
    if not cv:
        return []
    ins = cv.get("insights") or {}
    out: List[str] = []

    target_roles = ins.get("target_roles") or []
    if isinstance(target_roles, list):
        for r in target_roles:
            if isinstance(r, str) and r.strip():
                out.append(r.strip())

    tech_stack = ins.get("primary_tech_stack") or []
    if isinstance(tech_stack, list):
        for t in tech_stack:
            if isinstance(t, str) and t.strip():
                out.append(t.strip())

    current_title = ins.get("current_title")
    if isinstance(current_title, str) and current_title.strip():
        out.append(current_title.strip())

    # Deduplicate preserving order, trim to limit
    seen = set()
    unique: List[str] = []
    for k in out:
        kl = k.lower()
        if kl in seen:
            continue
        seen.add(kl)
        unique.append(k)
    return unique[:limit]


# ── Routers ──────────────────────────────────────────────────────────────────

auth_quick_router = APIRouter(prefix="/api/auth", tags=["Onboarding auth"])
onboarding_router = APIRouter(prefix="/api/onboarding", tags=["Onboarding"])
me_router = APIRouter(prefix="/api/users/me", tags=["User profile"])


# ── Register-quick: email + full name → pass1234 account ────────────────────

class RegisterQuickRequest(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


@auth_quick_router.post("/register-quick", status_code=status.HTTP_201_CREATED)
async def register_quick(request: RegisterQuickRequest):
    valid, err = validate_email(request.email)
    if not valid:
        raise HTTPException(status_code=400, detail=err)

    existing = await user_db.get_user_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Ensure default password still passes policy (letter + digit + 8 chars).
    ok, perr = validate_password_strength(DEFAULT_SIGNUP_PASSWORD)
    if not ok:
        raise HTTPException(status_code=500, detail=f"Default password policy fail: {perr}")

    username = await _unique_username(request.email)
    user = await user_db.create_user(
        username=username,
        email=request.email,
        password=DEFAULT_SIGNUP_PASSWORD,
        full_name=request.full_name,
        is_admin=False,
    )
    if not user:
        raise HTTPException(status_code=400, detail="Could not create account")

    user_data = {
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name"),
        "is_admin": user["is_admin"],
    }
    token_resp = generate_token_response(user_data)
    token_resp["default_password"] = DEFAULT_SIGNUP_PASSWORD
    token_resp["user"]["onboarding_completed"] = False
    return token_resp


# ── Onboarding status + completion ──────────────────────────────────────────

@onboarding_router.get("/status")
async def onboarding_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        row = await conn.fetchrow(
            "SELECT onboarding_completed FROM users WHERE id = $1",
            current_user["user_id"],
        )
        completed = bool(row and row["onboarding_completed"])

        cv_row = await conn.fetchrow(
            "SELECT 1 FROM user_cv_data WHERE user_id = $1", current_user["user_id"]
        )
        has_cv = cv_row is not None

        cfg_row = await conn.fetchrow(
            "SELECT country FROM user_scraper_configs WHERE user_id = $1 AND active = TRUE "
            "ORDER BY updated_at DESC LIMIT 1",
            current_user["user_id"],
        )
        has_config = cfg_row is not None
    finally:
        await user_db._release(conn)

    if completed:
        next_step = None
    elif not has_cv:
        next_step = "upload_cv"
    elif not has_config:
        next_step = "pick_country"
    else:
        next_step = "review"

    return {
        "onboarding_completed": completed,
        "has_cv": has_cv,
        "has_scraper_config": has_config,
        "next_step": next_step,
    }


@onboarding_router.post("/complete")
async def onboarding_complete(current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        await conn.execute(
            "UPDATE users SET onboarding_completed = TRUE WHERE id = $1",
            current_user["user_id"],
        )
    finally:
        await user_db._release(conn)
    return {"ok": True}


# ── Derived keywords + scraper config ───────────────────────────────────────

@me_router.get("/derived-keywords")
async def derived_keywords(current_user: Dict[str, Any] = Depends(get_current_user)):
    cv = await _fetch_cv(current_user["user_id"])
    if not cv:
        return {"keywords": [], "has_cv": False}
    kws = _derive_keywords(cv)
    return {
        "keywords": kws,
        "has_cv": True,
        "basis": {
            "target_roles":       (cv.get("insights") or {}).get("target_roles") or [],
            "primary_tech_stack": (cv.get("insights") or {}).get("primary_tech_stack") or [],
            "current_title":      (cv.get("insights") or {}).get("current_title"),
            "seniority":          (cv.get("insights") or {}).get("seniority"),
        },
    }


class ScraperConfigRequest(BaseModel):
    country: str = Field(..., min_length=2, max_length=64)


@me_router.get("/scraper-config")
async def get_scraper_config(current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        rows = await conn.fetch(
            "SELECT country, keywords, active, created_at, updated_at "
            "FROM user_scraper_configs WHERE user_id = $1 ORDER BY updated_at DESC",
            current_user["user_id"],
        )
    finally:
        await user_db._release(conn)
    configs = []
    for r in rows:
        kws = r["keywords"]
        if isinstance(kws, str):
            try: kws = json.loads(kws)
            except Exception: kws = []
        configs.append({
            "country": r["country"],
            "keywords": kws,
            "active": r["active"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            "updated_at": r["updated_at"].isoformat() if r["updated_at"] else None,
        })
    return {"configs": configs}


@me_router.post("/scraper-config")
async def save_scraper_config(
    request: ScraperConfigRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    cv = await _fetch_cv(current_user["user_id"])
    if not cv:
        raise HTTPException(
            status_code=400,
            detail="Upload your CV before configuring the scraper.",
        )
    keywords = _derive_keywords(cv)
    if not keywords:
        raise HTTPException(
            status_code=400,
            detail=("We could not derive any keywords from your CV. "
                    "Make sure target roles or tech stack are filled in."),
        )

    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        await conn.execute(
            """
            INSERT INTO user_scraper_configs (user_id, country, keywords, active, created_at, updated_at)
            VALUES ($1, $2, $3::jsonb, TRUE, NOW(), NOW())
            ON CONFLICT (user_id, country) DO UPDATE SET
                keywords   = EXCLUDED.keywords,
                active     = TRUE,
                updated_at = NOW()
            """,
            current_user["user_id"], request.country.strip(), json.dumps(keywords),
        )
        # Completing onboarding is atomic with saving the first config.
        await conn.execute(
            "UPDATE users SET onboarding_completed = TRUE WHERE id = $1",
            current_user["user_id"],
        )
    finally:
        await user_db._release(conn)

    return {"ok": True, "country": request.country.strip(), "keywords": keywords}


__all__ = [
    "auth_quick_router",
    "onboarding_router",
    "me_router",
    "init_onboarding_tables",
    "DEFAULT_SIGNUP_PASSWORD",
]
