"""
Auto-Apply learning layer.

Four endpoints that turn the extension into a system that learns:

  POST /api/autoapply/classify-fields   — label → canonical field_key (cached per ATS)
  POST /api/autoapply/resolve-fields    — priority chain: user_own → cv_profile → cohort
  POST /api/autoapply/record-answer     — persist a user's answer for next time
  GET  /api/autoapply/my-answers        — list everything stored for this user

Design rules enforced here:
- Protected-class fields (race, religion, disability, ...) are NEVER aggregated
  and NEVER inferred from cohorts. User-provided only, or blank.
- Cohort suggestions require ≥20 samples and ≥85% agreement.
- `user_own` answers always win over CV profile and cohorts.
- `cohort` resolutions are returned as suggestions (suggestion_only=true),
  not silent fills — the extension shows them yellow and promotes to `user_own`
  after one click.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth_utils import get_current_user
from user_database import UserDatabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/autoapply", tags=["AutoApply Learning"])
user_db = UserDatabase()

# ── Canonical field keys ─────────────────────────────────────────────────────
# The stable identity of a field across every ATS. The raw HTML label varies
# ("Are you authorized…" vs "Work authorization" vs "Visa status?"), but they
# all resolve to the same key: `requires_visa_sponsorship`.

FIELD_KEYS = {
    # Tier 1 — identity (always fillable from CV)
    "full_name", "first_name", "last_name", "email", "phone",
    "location", "city", "country", "postal_code",
    "linkedin_url", "github_url", "portfolio_url", "personal_website",

    # Tier 2 — derived (from CV insights)
    "years_of_experience", "current_title", "current_company",
    "seniority", "highest_education", "university",

    # Tier 3 — user-provided (once, then remembered)
    "requires_visa_sponsorship", "work_authorization_country",
    "willing_to_relocate", "notice_period_weeks", "preferred_start_date",
    "english_proficiency", "other_languages",
    "preferred_salary_annual", "preferred_salary_currency",
    "preferred_contract_type", "remote_preference",
    "heard_from_source",

    # Tier 5 — never auto-filled (free text)
    "cover_letter", "motivation", "additional_info", "why_this_company",

    # Tier 6 — protected class (never aggregated, never cohort-inferred)
    "gender", "race", "ethnicity", "religion", "sexual_orientation",
    "disability_status", "veteran_status", "pregnancy_status",
    "criminal_record", "age", "marital_status", "medical_condition",

    # Catch-all
    "custom_question", "unknown",
}

PROTECTED_FIELDS = {
    "gender", "race", "ethnicity", "religion", "sexual_orientation",
    "disability_status", "veteran_status", "pregnancy_status",
    "criminal_record", "age", "marital_status", "medical_condition",
}

NEVER_INFER_FIELDS = PROTECTED_FIELDS | {
    "cover_letter", "motivation", "additional_info", "why_this_company",
    "preferred_start_date", "heard_from_source",
}

# Which context dimensions drive the cohort key for each field.
# None = never inferred from cohorts. Empty list = global cohort (all users).
COHORT_RULES: Dict[str, Optional[List[str]]] = {
    "requires_visa_sponsorship":  ["user_country", "job_country"],
    "willing_to_relocate":        ["user_country", "job_country"],
    "notice_period_weeks":        ["user_country"],
    "english_proficiency":        ["user_country"],
    "preferred_salary_annual":    ["job_country", "role_family", "seniority"],
    "preferred_contract_type":    ["user_country"],
    "remote_preference":          ["user_country"],
    "other_languages":            ["user_country"],
}

MIN_COHORT_SAMPLES = 20
MIN_COHORT_AGREEMENT = 0.85

CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CLASSIFY_MAX_TOKENS = 1200


# ── Schema bootstrap ─────────────────────────────────────────────────────────

_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS user_answers (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    field_key     TEXT NOT NULL,
    value         TEXT,
    confidence    SMALLINT NOT NULL DEFAULT 100,
    source        TEXT NOT NULL DEFAULT 'user_typed',
    job_context   JSONB,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, field_key)
);
CREATE INDEX IF NOT EXISTS idx_user_answers_user ON user_answers(user_id);
CREATE INDEX IF NOT EXISTS idx_user_answers_field ON user_answers(field_key);

CREATE TABLE IF NOT EXISTS field_key_mappings (
    id            SERIAL PRIMARY KEY,
    ats           TEXT NOT NULL,
    label_hash    TEXT NOT NULL,
    raw_label     TEXT NOT NULL,
    field_type    TEXT,
    field_key     TEXT NOT NULL,
    classified_by TEXT NOT NULL DEFAULT 'claude',
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (ats, label_hash)
);
CREATE INDEX IF NOT EXISTS idx_fkm_ats_hash ON field_key_mappings(ats, label_hash);

-- Opt-out flag for contributing to cohort aggregates (defaults to opt-in).
ALTER TABLE users ADD COLUMN IF NOT EXISTS share_answers_for_cohort BOOLEAN NOT NULL DEFAULT TRUE;
"""


async def init_learning_tables():
    conn = await user_db.get_connection()
    if not conn:
        print("⚠️  Auto-Apply learning table init skipped: DB unavailable")
        return
    try:
        await conn.execute(_CREATE_TABLES)
        print("✅ Auto-Apply learning tables ready")
    except Exception as e:
        print(f"⚠️  Learning table init error: {e}")
    finally:
        await user_db._release(conn)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _normalize_label(label: str) -> str:
    return re.sub(r"\s+", " ", (label or "").strip().lower())


def _label_hash(label: str, field_type: Optional[str]) -> str:
    key = f"{_normalize_label(label)}||{(field_type or '').lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


def _extract_json(raw: str) -> Dict[str, Any]:
    if not raw:
        return {}
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```\s*$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return {}


async def _fetch_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """Read user_cv_data (parsed CV). Returns None if no CV uploaded."""
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


def _profile_value(profile: Dict[str, Any], field_key: str) -> Optional[str]:
    """Map canonical field_key → value from the parsed CV profile (if any)."""
    ins = profile.get("insights") or {}
    full_name = profile.get("full_name") or ""
    city, country = _split_location(profile.get("location"))
    direct = {
        "full_name":             full_name or None,
        "email":                 profile.get("email"),
        "phone":                 profile.get("phone"),
        "location":              profile.get("location"),
        "city":                  city,
        "country":               country,
        "linkedin_url":          profile.get("linkedin_url"),
        "github_url":            profile.get("github_url"),
        "portfolio_url":         profile.get("portfolio_url"),
        "personal_website":      profile.get("portfolio_url"),
        "years_of_experience":   ins.get("years_of_experience"),
        "current_title":         ins.get("current_title"),
        "current_company":       ins.get("current_company"),
        "seniority":             ins.get("seniority"),
        "highest_education":     ins.get("highest_education"),
        "work_authorization_country": ins.get("work_authorization"),
    }
    if field_key == "first_name":
        parts = full_name.split()
        return parts[0] if parts else None
    if field_key == "last_name":
        parts = full_name.split()
        return parts[-1] if len(parts) >= 2 else None
    v = direct.get(field_key)
    return str(v) if v is not None else None


def _split_location(loc: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not loc:
        return None, None
    parts = [p.strip() for p in loc.split(",") if p.strip()]
    if not parts:
        return None, None
    if len(parts) == 1:
        return None, parts[0]
    return parts[0], parts[-1]


def _user_country(profile: Optional[Dict[str, Any]]) -> Optional[str]:
    if not profile:
        return None
    _, country = _split_location(profile.get("location"))
    return country


# ── Cohort resolver (read-only, pure SQL) ────────────────────────────────────

async def _cohort_value(
    conn, field_key: str, cohort_values: Dict[str, Optional[str]]
) -> Optional[Dict[str, Any]]:
    """
    Aggregate answers across users whose job_context + profile match the cohort.
    Returns {value, sample_size, agreement} if confident, else None.
    """
    if field_key in NEVER_INFER_FIELDS:
        return None
    rule = COHORT_RULES.get(field_key)
    if rule is None:
        return None

    # Build WHERE clauses using job_context JSONB + a LATERAL join on user profile.
    # Simple approach: match job_context->>'user_country' etc. The recorder stamps
    # these fields on write so we don't need a join at read time.
    where, params = ["field_key = $1"], [field_key]
    idx = 2
    for dim in rule:
        val = cohort_values.get(dim)
        if not val:
            return None  # can't form cohort without this dimension
        where.append(f"job_context->>'{dim}' = ${idx}")
        params.append(val)
        idx += 1

    where.append("user_id IN (SELECT id FROM users WHERE share_answers_for_cohort IS NOT FALSE)")

    sql = f"""
      SELECT value, COUNT(*) AS n
      FROM user_answers
      WHERE {' AND '.join(where)} AND value IS NOT NULL AND value <> ''
      GROUP BY value
      ORDER BY n DESC
      LIMIT 5
    """
    rows = await conn.fetch(sql, *params)
    if not rows:
        return None
    total = sum(r["n"] for r in rows)
    if total < MIN_COHORT_SAMPLES:
        return None
    top = rows[0]
    agreement = top["n"] / total
    if agreement < MIN_COHORT_AGREEMENT:
        return None
    return {
        "value": top["value"],
        "sample_size": total,
        "agreement": round(agreement, 3),
    }


# ── Field classifier (label → field_key via Claude, cached) ──────────────────

class ClassifyField(BaseModel):
    id: str
    label: str
    type: Optional[str] = None

class ClassifyRequest(BaseModel):
    ats: str
    fields: List[ClassifyField] = Field(..., max_items=80)

_CLASSIFY_SYSTEM_PROMPT = f"""You classify job-application form field labels into canonical keys.

Return ONLY a JSON object:
{{ "mapping": {{ "<field_id>": "<canonical_key>" }} }}

Allowed canonical keys (use EXACTLY these, nothing else):
{sorted(FIELD_KEYS)}

Rules:
- Pick the single best key for each label.
- "custom_question" = a yes/no or free-text question that doesn't fit any other key.
- "unknown" = the label is uninterpretable or not an input we care about.
- Protected-class labels (gender / race / disability / veteran / sexual orientation / etc.)
  MUST map to their specific key (e.g. "gender") — never to "custom_question".
- Salary, notice period, relocation, visa sponsorship have dedicated keys — use them.
- Output JSON only, no prose."""


@router.post("/classify-fields")
async def classify_fields(
    request: ClassifyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    ats = (request.ats or "generic").lower()
    results: Dict[str, Dict[str, Any]] = {}
    unresolved: List[ClassifyField] = []

    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        # Cache lookup
        for f in request.fields:
            h = _label_hash(f.label, f.type)
            row = await conn.fetchrow(
                "SELECT field_key, classified_by FROM field_key_mappings WHERE ats=$1 AND label_hash=$2",
                ats, h,
            )
            if row:
                results[f.id] = {"field_key": row["field_key"], "cached": True}
            else:
                unresolved.append(f)

        # Call Claude only for the uncached subset
        if unresolved:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise HTTPException(status_code=503, detail="Classifier unavailable (no API key)")
            try:
                import anthropic
            except ImportError:
                raise HTTPException(status_code=503, detail="Classifier unavailable (SDK missing)")

            user_msg = json.dumps(
                {"fields": [f.dict(exclude_none=True) for f in unresolved]},
                ensure_ascii=False,
            )
            try:
                resp = anthropic.Anthropic(api_key=api_key).messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=CLASSIFY_MAX_TOKENS,
                    system=_CLASSIFY_SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_msg}],
                )
            except Exception as e:
                logger.warning("classify-fields Claude call failed: %s", e)
                raise HTTPException(status_code=502, detail=f"Classifier error: {type(e).__name__}")

            raw = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
            mapping = (_extract_json(raw).get("mapping") or {})

            for f in unresolved:
                fk = mapping.get(f.id, "unknown")
                if fk not in FIELD_KEYS:
                    fk = "unknown"
                results[f.id] = {"field_key": fk, "cached": False}
                try:
                    await conn.execute(
                        """
                        INSERT INTO field_key_mappings (ats, label_hash, raw_label, field_type, field_key, classified_by)
                        VALUES ($1, $2, $3, $4, $5, 'claude')
                        ON CONFLICT (ats, label_hash) DO NOTHING
                        """,
                        ats, _label_hash(f.label, f.type), f.label[:500], f.type, fk,
                    )
                except Exception as e:
                    logger.warning("field_key_mappings insert failed: %s", e)
    finally:
        await user_db._release(conn)

    return {"mapping": {fid: r["field_key"] for fid, r in results.items()}, "details": results}


# ── Resolver (priority chain) ────────────────────────────────────────────────

class ResolveRequest(BaseModel):
    field_keys: List[str]
    job_context: Optional[Dict[str, Any]] = None  # {country, role_family, company, ats, ...}

@router.post("/resolve-fields")
async def resolve_fields(
    request: ResolveRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    profile = await _fetch_profile(user_id)

    # Build cohort context from profile + job_context
    ctx = dict(request.job_context or {})
    ctx.setdefault("user_country", _user_country(profile))
    ins = (profile or {}).get("insights") or {}
    ctx.setdefault("seniority", ins.get("seniority"))

    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")

    resolutions: Dict[str, Dict[str, Any]] = {}
    try:
        # Batch fetch user_own answers
        user_rows = await conn.fetch(
            "SELECT field_key, value FROM user_answers WHERE user_id = $1 AND field_key = ANY($2::text[])",
            user_id, request.field_keys,
        )
        user_own = {r["field_key"]: r["value"] for r in user_rows}

        for fk in request.field_keys:
            if fk not in FIELD_KEYS:
                resolutions[fk] = {"value": None, "source": "unknown_field_key",
                                   "confidence": 0, "suggestion_only": False}
                continue

            # Protected-class → never auto-fill
            if fk in PROTECTED_FIELDS:
                if fk in user_own:
                    resolutions[fk] = {"value": user_own[fk], "source": "user_own",
                                       "confidence": 100, "suggestion_only": False}
                else:
                    resolutions[fk] = {"value": None, "source": "protected_skip",
                                       "confidence": 0, "suggestion_only": False}
                continue

            # 1. user_own
            if fk in user_own and user_own[fk] is not None:
                resolutions[fk] = {"value": user_own[fk], "source": "user_own",
                                   "confidence": 100, "suggestion_only": False}
                continue

            # 2. cv_profile
            pv = _profile_value(profile or {}, fk) if profile else None
            if pv is not None:
                resolutions[fk] = {"value": pv, "source": "cv_profile",
                                   "confidence": 90, "suggestion_only": False}
                continue

            # 3. cohort
            cohort = await _cohort_value(conn, fk, ctx)
            if cohort:
                resolutions[fk] = {
                    "value": cohort["value"],
                    "source": "cohort",
                    "confidence": int(cohort["agreement"] * 100),
                    "suggestion_only": True,
                    "basis": {
                        "sample_size": cohort["sample_size"],
                        "agreement": cohort["agreement"],
                        "cohort_dims": COHORT_RULES.get(fk),
                    },
                }
                continue

            # 4. unknown
            resolutions[fk] = {"value": None, "source": "unknown",
                               "confidence": 0, "suggestion_only": False}
    finally:
        await user_db._release(conn)

    return {"resolutions": resolutions, "context": ctx}


# ── Record (user typed / confirmed an answer) ────────────────────────────────

class RecordAnswerRequest(BaseModel):
    field_key: str
    value: Optional[str]
    source: str = "user_typed"        # user_typed | accepted_suggestion | user_edited_our_fill
    job_context: Optional[Dict[str, Any]] = None

@router.post("/record-answer")
async def record_answer(
    request: RecordAnswerRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if request.field_key not in FIELD_KEYS:
        raise HTTPException(status_code=400, detail="unknown field_key")
    confidence = {"user_typed": 100, "user_edited_our_fill": 100,
                  "accepted_suggestion": 95}.get(request.source, 80)

    # Stamp cohort dimensions onto the answer so the aggregate query is cheap.
    ctx = dict(request.job_context or {})
    if "user_country" not in ctx:
        profile = await _fetch_profile(current_user["user_id"])
        ctx["user_country"] = _user_country(profile)
        ins = (profile or {}).get("insights") or {}
        ctx.setdefault("seniority", ins.get("seniority"))

    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        await conn.execute(
            """
            INSERT INTO user_answers (user_id, field_key, value, confidence, source, job_context, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6::jsonb, NOW(), NOW())
            ON CONFLICT (user_id, field_key) DO UPDATE SET
                value       = EXCLUDED.value,
                confidence  = EXCLUDED.confidence,
                source      = EXCLUDED.source,
                job_context = EXCLUDED.job_context,
                updated_at  = NOW()
            """,
            current_user["user_id"], request.field_key, request.value,
            confidence, request.source, json.dumps(ctx),
        )
    finally:
        await user_db._release(conn)
    return {"ok": True}


# ── User views their stored answers ──────────────────────────────────────────

@router.get("/my-answers")
async def my_answers(current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        rows = await conn.fetch(
            "SELECT field_key, value, confidence, source, updated_at "
            "FROM user_answers WHERE user_id = $1 ORDER BY updated_at DESC",
            current_user["user_id"],
        )
    finally:
        await user_db._release(conn)
    return {"answers": [dict(r) | {"updated_at": r["updated_at"].isoformat()} for r in rows]}


class DeleteAnswerRequest(BaseModel):
    field_key: str

@router.post("/delete-answer")
async def delete_answer(
    request: DeleteAnswerRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        await conn.execute(
            "DELETE FROM user_answers WHERE user_id = $1 AND field_key = $2",
            current_user["user_id"], request.field_key,
        )
    finally:
        await user_db._release(conn)
    return {"ok": True}


__all__ = ["router", "init_learning_tables", "FIELD_KEYS", "PROTECTED_FIELDS"]
