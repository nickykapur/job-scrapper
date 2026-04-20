#!/usr/bin/env python3
"""CV upload, parsing, and profile management routes — Auto-Apply Pilot."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import re
import io
import json

from auth_utils import get_current_user
from user_database import UserDatabase

try:
    import slack_notify  # type: ignore
except Exception:
    slack_notify = None

try:
    import cv_parser  # type: ignore
except Exception as _e:
    cv_parser = None  # type: ignore
    print(f"⚠️  cv_parser not available, will fall back to regex: {_e}")

router = APIRouter(prefix="/api/cv", tags=["CV"])
admin_router = APIRouter(prefix="/api/admin", tags=["Admin CV"])
user_db = UserDatabase()


def _require_admin(user: Dict[str, Any]) -> None:
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

# ── Table bootstrap ───────────────────────────────────────────────────────────

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS user_cv_data (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name     TEXT,
    email         TEXT,
    phone         TEXT,
    location      TEXT,
    linkedin_url  TEXT,
    github_url    TEXT,
    portfolio_url TEXT,
    skills        JSONB NOT NULL DEFAULT '[]'::jsonb,
    experience    JSONB NOT NULL DEFAULT '[]'::jsonb,
    education     JSONB NOT NULL DEFAULT '[]'::jsonb,
    languages     JSONB NOT NULL DEFAULT '[]'::jsonb,
    summary       TEXT,
    cv_filename   TEXT,
    cv_raw_text   TEXT,
    uploaded_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_cv_data_user_id ON user_cv_data(user_id);

-- Additive columns for Claude-derived enrichment (idempotent)
ALTER TABLE user_cv_data ADD COLUMN IF NOT EXISTS headline TEXT;
ALTER TABLE user_cv_data ADD COLUMN IF NOT EXISTS certifications JSONB NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE user_cv_data ADD COLUMN IF NOT EXISTS insights JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE user_cv_data ADD COLUMN IF NOT EXISTS parse_model TEXT;
ALTER TABLE user_cv_data ADD COLUMN IF NOT EXISTS parse_input_tokens INTEGER;
ALTER TABLE user_cv_data ADD COLUMN IF NOT EXISTS parse_output_tokens INTEGER;
"""


async def init_cv_table():
    conn = await user_db.get_connection()
    if not conn:
        print("⚠️  CV table init skipped: DB unavailable")
        return
    try:
        await conn.execute(_CREATE_TABLE)
        print("✅ CV table ready")
    except Exception as e:
        print(f"⚠️  CV table init error: {e}")
    finally:
        await user_db._release(conn)


# ── Text extraction helpers ───────────────────────────────────────────────────

def _extract_email(text: str) -> Optional[str]:
    m = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
    return m.group() if m else None


def _extract_phone(text: str) -> Optional[str]:
    m = re.search(r"(\+?\d[\d\s\-().]{7,}\d)", text)
    return m.group().strip() if m else None


def _extract_linkedin(text: str) -> Optional[str]:
    m = re.search(r"linkedin\.com/in/[\w\-]+", text, re.I)
    return f"https://{m.group()}" if m else None


def _extract_github(text: str) -> Optional[str]:
    m = re.search(r"github\.com/[\w\-]+", text, re.I)
    return f"https://{m.group()}" if m else None


_SKILLS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "kotlin", "swift", "php", "ruby", "scala", "r", "matlab",
    "react", "angular", "vue", "svelte", "next.js", "nuxt",
    "node.js", "express", "fastapi", "django", "flask", "spring boot", "spring",
    "sql", "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
    "dynamodb", "cassandra", "neo4j",
    "docker", "kubernetes", "terraform", "ansible", "jenkins", "github actions",
    "aws", "gcp", "azure", "heroku", "vercel", "netlify",
    "git", "ci/cd", "rest api", "graphql", "grpc", "microservices",
    "html", "css", "sass", "tailwind", "bootstrap",
    "machine learning", "deep learning", "tensorflow", "pytorch", "pandas",
    "numpy", "scikit-learn", "sklearn", "nlp", "computer vision",
    "linux", "bash", "powershell", "nginx", "apache",
    "agile", "scrum", "kanban", "jira", "confluence",
    "figma", "photoshop", "illustrator", "sketch",
    "excel", "tableau", "power bi", "looker", "dbt",
]


def _extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    return [s for s in _SKILLS if s in text_lower]


def _parse_pdf(content: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        pass
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        raise ValueError("PDF parsing library not available. Upload a TXT or DOCX instead.")
    except Exception as e:
        raise ValueError(f"Could not read PDF: {e}")


def _parse_docx(content: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:
        raise ValueError("DOCX parsing library not available. Upload a PDF or TXT instead.")
    except Exception as e:
        raise ValueError(f"Could not read DOCX: {e}")


def _parse_file(filename: str, content: bytes) -> Dict[str, Any]:
    fname = filename.lower()
    if fname.endswith(".pdf"):
        raw = _parse_pdf(content)
    elif fname.endswith(".docx"):
        raw = _parse_docx(content)
    elif fname.endswith(".txt"):
        raw = content.decode("utf-8", errors="ignore")
    else:
        raise ValueError("Unsupported file type. Upload PDF, DOCX, or TXT.")

    return {
        "raw_text": raw,
        "email": _extract_email(raw),
        "phone": _extract_phone(raw),
        "linkedin_url": _extract_linkedin(raw),
        "github_url": _extract_github(raw),
        "skills": _extract_skills(raw),
    }


# ── DB helpers ────────────────────────────────────────────────────────────────

async def _fetch_cv(user_id: int) -> Optional[Dict]:
    conn = await user_db.get_connection()
    if not conn:
        return None
    try:
        row = await conn.fetchrow(
            "SELECT * FROM user_cv_data WHERE user_id = $1", user_id
        )
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
            elif val is None:
                d[key] = []
        insights_val = d.get("insights")
        if isinstance(insights_val, str):
            try:
                d["insights"] = json.loads(insights_val)
            except Exception:
                d["insights"] = {}
        elif insights_val is None:
            d["insights"] = {}
        return d
    finally:
        await user_db._release(conn)


# ── Endpoints ─────────────────────────────────────────────────────────────────

def _merge_parsed(claude: Dict[str, Any], regex: Dict[str, Any]) -> Dict[str, Any]:
    """Claude wins on every field it extracted. Regex fills gaps."""
    def pick(k: str, default=None):
        v = claude.get(k)
        if v in (None, "", [], {}):
            return regex.get(k, default)
        return v
    return {
        "full_name":      claude.get("name") or None,
        "email":          pick("email"),
        "phone":          pick("phone"),
        "location":       claude.get("location"),
        "linkedin_url":   pick("linkedin_url"),
        "github_url":     pick("github_url"),
        "portfolio_url":  claude.get("portfolio_url"),
        "headline":       claude.get("headline"),
        "summary":        claude.get("summary"),
        "skills":         claude.get("skills") or regex.get("skills") or [],
        "experience":     claude.get("experience") or [],
        "education":      claude.get("education") or [],
        "languages":      claude.get("languages") or [],
        "certifications": claude.get("certifications") or [],
        "insights":       claude.get("insights") or {},
    }


@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    content = await file.read()
    filename = file.filename or "file.txt"

    # 1. Robust text extraction (rejects garbage before tokens are spent)
    if cv_parser is not None:
        try:
            raw_text = cv_parser.extract_text(content, filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        regex_parsed = {
            "email": _extract_email(raw_text),
            "phone": _extract_phone(raw_text),
            "linkedin_url": _extract_linkedin(raw_text),
            "github_url": _extract_github(raw_text),
            "skills": _extract_skills(raw_text),
        }
    else:
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 5 MB)")
        try:
            legacy = _parse_file(filename, content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        raw_text = legacy["raw_text"]
        regex_parsed = legacy

    # 2. Try Claude for structured parsing. Fall back silently if it fails.
    claude_parsed: Dict[str, Any] = {}
    claude_usage: Dict[str, Any] = {}
    if cv_parser is not None:
        try:
            claude_parsed, claude_usage = cv_parser.parse_with_claude(raw_text)
        except Exception as e:
            print(f"⚠️  Claude parse unexpected error: {e}")
            claude_parsed, claude_usage = {}, {"error": str(e)}

    merged = _merge_parsed(claude_parsed, regex_parsed)

    user_id = current_user["user_id"]
    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        await conn.execute(
            """
            INSERT INTO user_cv_data
                (user_id, full_name, email, phone, location, linkedin_url, github_url,
                 portfolio_url, headline, summary, skills, experience, education, languages,
                 certifications, insights, parse_model, parse_input_tokens, parse_output_tokens,
                 cv_filename, cv_raw_text, uploaded_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11::jsonb, $12::jsonb,
                    $13::jsonb, $14::jsonb, $15::jsonb, $16::jsonb, $17, $18, $19,
                    $20, $21, NOW(), NOW())
            ON CONFLICT (user_id) DO UPDATE SET
                full_name           = EXCLUDED.full_name,
                email               = EXCLUDED.email,
                phone               = EXCLUDED.phone,
                location            = EXCLUDED.location,
                linkedin_url        = EXCLUDED.linkedin_url,
                github_url          = EXCLUDED.github_url,
                portfolio_url       = EXCLUDED.portfolio_url,
                headline            = EXCLUDED.headline,
                summary             = EXCLUDED.summary,
                skills              = EXCLUDED.skills,
                experience          = EXCLUDED.experience,
                education           = EXCLUDED.education,
                languages           = EXCLUDED.languages,
                certifications      = EXCLUDED.certifications,
                insights            = EXCLUDED.insights,
                parse_model         = EXCLUDED.parse_model,
                parse_input_tokens  = EXCLUDED.parse_input_tokens,
                parse_output_tokens = EXCLUDED.parse_output_tokens,
                cv_filename         = EXCLUDED.cv_filename,
                cv_raw_text         = EXCLUDED.cv_raw_text,
                updated_at          = NOW()
            """,
            user_id,
            merged["full_name"],
            merged["email"],
            merged["phone"],
            merged["location"],
            merged["linkedin_url"],
            merged["github_url"],
            merged["portfolio_url"],
            merged["headline"],
            merged["summary"],
            json.dumps(merged["skills"]),
            json.dumps(merged["experience"]),
            json.dumps(merged["education"]),
            json.dumps(merged["languages"]),
            json.dumps(merged["certifications"]),
            json.dumps(merged["insights"]),
            claude_usage.get("model"),
            claude_usage.get("input_tokens") or 0,
            claude_usage.get("output_tokens") or 0,
            filename,
            raw_text[:50000],
        )
    finally:
        await user_db._release(conn)

    if slack_notify is not None:
        try:
            await slack_notify.notify_cv_upload_async(
                username=current_user.get("username", "unknown"),
                display_name=current_user.get("full_name") or current_user.get("username", ""),
                filename=filename,
                file_size_kb=len(content) / 1024,
                skills_count=len(merged["skills"] or []),
            )
        except Exception as e:
            print(f"⚠️  Slack CV notification failed: {e}")

    return {
        "success": True,
        "message": "CV uploaded and parsed successfully",
        "parser": "claude" if claude_parsed else "regex",
        "usage": {
            "input_tokens": claude_usage.get("input_tokens", 0),
            "output_tokens": claude_usage.get("output_tokens", 0),
            "model": claude_usage.get("model"),
            "error": claude_usage.get("error"),
        },
        "extracted": {
            "full_name": merged["full_name"],
            "email": merged["email"],
            "phone": merged["phone"],
            "location": merged["location"],
            "linkedin_url": merged["linkedin_url"],
            "github_url": merged["github_url"],
            "portfolio_url": merged["portfolio_url"],
            "summary": merged["summary"],
            "skills": merged["skills"],
            "experience_count": len(merged["experience"] or []),
            "education_count": len(merged["education"] or []),
            "languages_count": len(merged["languages"] or []),
            "cv_filename": filename,
        },
    }


@router.get("/profile")
async def get_cv_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    cv = await _fetch_cv(current_user["user_id"])
    if not cv:
        return {"exists": False}

    def _iso(dt):
        return dt.isoformat() if dt else None

    insights = cv.get("insights")
    if isinstance(insights, str):
        try:
            insights = json.loads(insights)
        except Exception:
            insights = {}
    elif insights is None:
        insights = {}
    certifications = cv.get("certifications")
    if isinstance(certifications, str):
        try:
            certifications = json.loads(certifications)
        except Exception:
            certifications = []
    elif certifications is None:
        certifications = []

    return {
        "exists": True,
        "full_name": cv.get("full_name"),
        "email": cv.get("email"),
        "phone": cv.get("phone"),
        "location": cv.get("location"),
        "linkedin_url": cv.get("linkedin_url"),
        "github_url": cv.get("github_url"),
        "portfolio_url": cv.get("portfolio_url"),
        "headline": cv.get("headline"),
        "skills": cv.get("skills", []),
        "experience": cv.get("experience", []),
        "education": cv.get("education", []),
        "languages": cv.get("languages", []),
        "certifications": certifications,
        "insights": insights,
        "summary": cv.get("summary"),
        "cv_filename": cv.get("cv_filename"),
        "parse_model": cv.get("parse_model"),
        "parse_input_tokens": cv.get("parse_input_tokens"),
        "parse_output_tokens": cv.get("parse_output_tokens"),
        "uploaded_at": _iso(cv.get("uploaded_at")),
        "updated_at": _iso(cv.get("updated_at")),
    }


class UpdateCVRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    languages: Optional[List[str]] = None
    summary: Optional[str] = None


@router.put("/profile")
async def update_cv_profile(
    request: UpdateCVRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        await conn.execute(
            "INSERT INTO user_cv_data (user_id, updated_at) VALUES ($1, NOW()) "
            "ON CONFLICT (user_id) DO NOTHING",
            user_id,
        )
        updates = {k: v for k, v in request.dict().items() if v is not None}
        if not updates:
            return {"success": True, "message": "Nothing to update"}

        json_fields = {"skills", "experience", "education", "languages"}
        set_parts: List[str] = []
        values: List[Any] = [user_id]
        idx = 2
        for col, val in updates.items():
            if col in json_fields:
                set_parts.append(f"{col} = ${idx}::jsonb")
                values.append(json.dumps(val))
            else:
                set_parts.append(f"{col} = ${idx}")
                values.append(val)
            idx += 1
        set_parts.append("updated_at = NOW()")

        await conn.execute(
            f"UPDATE user_cv_data SET {', '.join(set_parts)} WHERE user_id = $1",
            *values,
        )
    finally:
        await user_db._release(conn)

    return {"success": True, "message": "CV profile updated"}


@router.delete("/")
async def delete_cv(current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        await conn.execute(
            "DELETE FROM user_cv_data WHERE user_id = $1", current_user["user_id"]
        )
    finally:
        await user_db._release(conn)
    return {"success": True, "message": "CV data deleted"}


@admin_router.get("/cv-uploads")
async def admin_list_cv_uploads(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    _require_admin(current_user)
    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        rows = await conn.fetch(
            """
            SELECT c.id, c.user_id, c.full_name, c.email, c.phone,
                   c.location, c.linkedin_url, c.github_url, c.portfolio_url,
                   c.skills, c.summary, c.cv_filename, c.uploaded_at, c.updated_at,
                   u.username, u.email AS user_email, u.full_name AS user_full_name,
                   u.is_admin, u.is_active
            FROM user_cv_data c
            JOIN users u ON u.id = c.user_id
            ORDER BY c.updated_at DESC NULLS LAST, c.uploaded_at DESC NULLS LAST
            """
        )
    finally:
        await user_db._release(conn)

    def _iso(dt):
        return dt.isoformat() if dt else None

    items = []
    for r in rows:
        d = dict(r)
        skills = d.get("skills")
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except Exception:
                skills = []
        elif skills is None:
            skills = []
        items.append({
            "id": d["id"],
            "user_id": d["user_id"],
            "username": d["username"],
            "user_email": d["user_email"],
            "user_full_name": d["user_full_name"],
            "is_admin": d["is_admin"],
            "is_active": d["is_active"],
            "full_name": d.get("full_name"),
            "email": d.get("email"),
            "phone": d.get("phone"),
            "location": d.get("location"),
            "linkedin_url": d.get("linkedin_url"),
            "github_url": d.get("github_url"),
            "portfolio_url": d.get("portfolio_url"),
            "skills": skills,
            "skills_count": len(skills),
            "summary": d.get("summary"),
            "cv_filename": d.get("cv_filename"),
            "uploaded_at": _iso(d.get("uploaded_at")),
            "updated_at": _iso(d.get("updated_at")),
        })
    return {"items": items, "count": len(items)}


__all__ = ["router", "admin_router", "init_cv_table"]
