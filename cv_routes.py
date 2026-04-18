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

router = APIRouter(prefix="/api/cv", tags=["CV"])
user_db = UserDatabase()

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
        for key in ("skills", "experience", "education", "languages"):
            val = d.get(key)
            if isinstance(val, str):
                try:
                    d[key] = json.loads(val)
                except Exception:
                    d[key] = []
            elif val is None:
                d[key] = []
        return d
    finally:
        await user_db._release(conn)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")

    try:
        parsed = _parse_file(file.filename or "file.txt", content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user_id = current_user["user_id"]
    conn = await user_db.get_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        await conn.execute(
            """
            INSERT INTO user_cv_data
                (user_id, email, phone, linkedin_url, github_url,
                 skills, cv_filename, cv_raw_text, uploaded_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8, NOW(), NOW())
            ON CONFLICT (user_id) DO UPDATE SET
                email        = EXCLUDED.email,
                phone        = EXCLUDED.phone,
                linkedin_url = EXCLUDED.linkedin_url,
                github_url   = EXCLUDED.github_url,
                skills       = EXCLUDED.skills,
                cv_filename  = EXCLUDED.cv_filename,
                cv_raw_text  = EXCLUDED.cv_raw_text,
                updated_at   = NOW()
            """,
            user_id,
            parsed["email"],
            parsed["phone"],
            parsed["linkedin_url"],
            parsed["github_url"],
            json.dumps(parsed["skills"]),
            file.filename,
            parsed["raw_text"][:50000],
        )
    finally:
        await user_db._release(conn)

    return {
        "success": True,
        "message": "CV uploaded and parsed successfully",
        "extracted": {
            "email": parsed["email"],
            "phone": parsed["phone"],
            "linkedin_url": parsed["linkedin_url"],
            "github_url": parsed["github_url"],
            "skills": parsed["skills"],
            "cv_filename": file.filename,
        },
    }


@router.get("/profile")
async def get_cv_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    cv = await _fetch_cv(current_user["user_id"])
    if not cv:
        return {"exists": False}

    def _iso(dt):
        return dt.isoformat() if dt else None

    return {
        "exists": True,
        "full_name": cv.get("full_name"),
        "email": cv.get("email"),
        "phone": cv.get("phone"),
        "location": cv.get("location"),
        "linkedin_url": cv.get("linkedin_url"),
        "github_url": cv.get("github_url"),
        "portfolio_url": cv.get("portfolio_url"),
        "skills": cv.get("skills", []),
        "experience": cv.get("experience", []),
        "education": cv.get("education", []),
        "languages": cv.get("languages", []),
        "summary": cv.get("summary"),
        "cv_filename": cv.get("cv_filename"),
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


@router.delete("")
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


__all__ = ["router", "init_cv_table"]
