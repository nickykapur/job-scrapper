"""
Auto-Apply field mapper.

Takes a list of fields scraped from a job-application form and the user's
parsed CV profile, and asks Claude to return a {field_id: value} mapping.

Kept server-side so the Anthropic API key is never shipped to the extension.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth_utils import get_current_user
from user_database import UserDatabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/autoapply", tags=["AutoApply"])
user_db = UserDatabase()

MAX_FIELDS = 80
MAX_OUTPUT_TOKENS = 1500
DEFAULT_MODEL = "claude-haiku-4-5-20251001"


class FieldSpec(BaseModel):
    id: str
    label: Optional[str] = ""
    tag: Optional[str] = None
    type: Optional[str] = None
    required: bool = False
    options: Optional[List[Dict[str, Any]]] = None


class JobContext(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    host: Optional[str] = None


class MapFieldsRequest(BaseModel):
    fields: List[FieldSpec] = Field(..., max_items=MAX_FIELDS)
    job_context: Optional[JobContext] = None


SYSTEM_PROMPT = """You map job-application form fields to values from a user's CV profile.

Return ONLY a JSON object of the form:
{ "mapping": { "<field_id>": "<value_or_null>" } }

Rules:
- Use ONLY data present in the CV profile. Never invent names, emails, salaries, dates, or authorizations.
- If the CV profile does not contain a confident answer for a field, return null for that field.
- Match on the field's label + type, not just the name. "City" and "Location" both map to profile.location.
- For phone, strip spaces only if the field type is "tel".
- For <select> fields, pick an option from the options list whose label/value matches. If none match, return null.
- For yes/no questions (e.g. "Do you require visa sponsorship?"), only answer if work_authorization clearly implies it. Otherwise null.
- For free-text motivation / cover letter fields, return null (human writes these).
- For salary / notice period / availability / demographic fields, return null unless the profile explicitly contains the info.
- Never include fields that aren't in the input list.

Output the JSON object only. No markdown fence, no prose."""


def _safe_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Strip CV to the fields useful for form filling (keeps prompt small)."""
    insights = profile.get("insights") or {}
    return {
        "full_name": profile.get("full_name"),
        "email": profile.get("email"),
        "phone": profile.get("phone"),
        "location": profile.get("location"),
        "linkedin_url": profile.get("linkedin_url"),
        "github_url": profile.get("github_url"),
        "portfolio_url": profile.get("portfolio_url"),
        "headline": profile.get("headline"),
        "summary": profile.get("summary"),
        "years_of_experience": insights.get("years_of_experience"),
        "current_title": insights.get("current_title"),
        "current_company": insights.get("current_company"),
        "seniority": insights.get("seniority"),
        "target_roles": insights.get("target_roles") or [],
        "highest_education": insights.get("highest_education"),
        "work_authorization": insights.get("work_authorization"),
        "availability": insights.get("availability"),
        "top_skills": (insights.get("top_skills") or profile.get("skills") or [])[:15],
    }


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
    conn = await user_db.get_connection()
    if not conn:
        return None
    try:
        row = await conn.fetchrow("SELECT * FROM user_cv_data WHERE user_id = $1", user_id)
        if not row:
            return None
        d = dict(row)
        for key in ("skills", "experience", "education", "languages", "certifications"):
            val = d.get(key)
            if isinstance(val, str):
                try:
                    d[key] = json.loads(val)
                except Exception:
                    d[key] = []
        insights = d.get("insights")
        if isinstance(insights, str):
            try:
                d["insights"] = json.loads(insights)
            except Exception:
                d["insights"] = {}
        elif insights is None:
            d["insights"] = {}
        return d
    finally:
        await user_db._release(conn)


@router.post("/map-fields")
async def map_fields(
    request: MapFieldsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    profile = await _fetch_profile(current_user["user_id"])
    if not profile:
        raise HTTPException(status_code=400, detail="Upload a CV first before using Auto-Apply.")

    safe_profile = _safe_profile(profile)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Auto-Apply mapper unavailable (no API key)")

    try:
        import anthropic
    except ImportError:
        raise HTTPException(status_code=503, detail="Auto-Apply mapper unavailable (SDK missing)")

    field_list = [f.dict(exclude_none=True) for f in request.fields[:MAX_FIELDS]]

    user_msg = json.dumps(
        {
            "profile": safe_profile,
            "job_context": request.job_context.dict() if request.job_context else None,
            "fields": field_list,
        },
        ensure_ascii=False,
    )

    client = anthropic.Anthropic(api_key=api_key)
    try:
        resp = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=MAX_OUTPUT_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:
        logger.warning("Auto-apply map failed: %s", e)
        raise HTTPException(status_code=502, detail=f"Mapper error: {type(e).__name__}")

    raw = ""
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            raw += block.text

    parsed = _extract_json(raw)
    mapping = parsed.get("mapping") or parsed or {}

    valid_ids = {f.id for f in request.fields}
    clean_mapping = {k: v for k, v in mapping.items() if k in valid_ids}

    return {
        "mapping": clean_mapping,
        "usage": {
            "model": resp.model,
            "input_tokens": getattr(resp.usage, "input_tokens", 0),
            "output_tokens": getattr(resp.usage, "output_tokens", 0),
        },
    }


__all__ = ["router"]
