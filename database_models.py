#!/usr/bin/env python3
"""
Database models and utilities for LinkedIn Job Manager
Supports both PostgreSQL and JSON fallback
"""

import os
import json
import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncpg
from dataclasses import dataclass

@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    posted_date: str
    job_url: str
    scraped_at: str
    applied: bool = False
    is_new: bool = False
    category: Optional[str] = None
    notes: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen_24h: Optional[str] = None
    excluded: bool = False

class JobDatabase:
    def __init__(self):
        # Try PostgreSQL first, fallback to JSON
        self.db_url = os.environ.get('DATABASE_URL')
        self.use_postgres = bool(self.db_url)
        self.json_file = "jobs_database.json"
        self._pool = None  # Connection pool — reuses connections instead of opening new ones

        if self.use_postgres:
            print("🐘 Using PostgreSQL database")
        else:
            print("📄 Using JSON file fallback")

    @staticmethod
    def normalize_job_title(title: str) -> str:
        """
        Normalize job title by removing seniority levels, location info, and common variations.
        This helps identify when a company reposts the same job.
        """
        if not title:
            return ""

        # Convert to lowercase
        normalized = title.lower().strip()

        # Remove seniority levels
        normalized = re.sub(r'\b(senior|sr\.?|junior|jr\.?|mid-level|mid level|lead|principal|staff|i|ii|iii|iv|v)\b', '', normalized, flags=re.IGNORECASE)

        # Remove location info
        normalized = re.sub(r'\b(remote|hybrid|onsite|on-site)\b', '', normalized, flags=re.IGNORECASE)

        # Remove employment type
        normalized = re.sub(r'\b(full time|full-time|part time|part-time|contract|temporary)\b', '', normalized, flags=re.IGNORECASE)

        # Remove special characters except spaces and dashes
        normalized = re.sub(r'[^a-z0-9\s\-]', '', normalized)

        # Collapse multiple spaces into one
        normalized = re.sub(r'\s+', ' ', normalized)

        return normalized.strip()

    async def check_if_repost(self, company: str, title: str, country: str, days_window: int = 30, conn=None) -> Tuple[bool, Optional[str]]:
        """
        Check if a job is likely a repost of a job the user has already applied to.

        Args:
            company: Company name
            title: Job title
            country: Country where job is located
            days_window: Number of days to look back for similar jobs (default 30)
            conn: Optional existing database connection to reuse

        Returns:
            Tuple of (is_repost: bool, original_job_id: Optional[str])
        """
        if not self.use_postgres:
            return False, None

        normalized_title = self.normalize_job_title(title)
        if not normalized_title:
            return False, None

        own_conn = conn is None
        if own_conn:
            conn = await self.get_connection()
            if not conn:
                return False, None

        try:
            # Check if we have a matching signature in the last X days
            cutoff_date = datetime.now() - timedelta(days=days_window)

            result = await conn.fetchrow("""
                SELECT original_job_id, applied_date
                FROM job_signatures
                WHERE LOWER(company) = LOWER($1)
                  AND normalized_title = $2
                  AND (country = $3 OR country IS NULL OR $3 IS NULL)
                  AND applied_date >= $4
                ORDER BY applied_date DESC
                LIMIT 1
            """, company, normalized_title, country, cutoff_date)

            if result:
                print(f"🔍 Detected repost: '{title}' at {company} (originally applied on {result['applied_date'].strftime('%Y-%m-%d')})")
                return True, result['original_job_id']

            return False, None

        except Exception as e:
            print(f"⚠️  Error checking for repost: {e}")
            return False, None
        finally:
            if own_conn:
                await self._release(conn)

    async def add_job_signature(self, company: str, title: str, country: str, job_id: str) -> bool:
        """
        Add a job signature to track that the user has applied to this type of job at this company.

        Args:
            company: Company name
            title: Job title
            country: Country where job is located
            job_id: ID of the job

        Returns:
            bool: Success status
        """
        if not self.use_postgres:
            return False

        normalized_title = self.normalize_job_title(title)
        if not normalized_title:
            return False

        conn = await self.get_connection()
        if not conn:
            return False

        try:
            await conn.execute("""
                INSERT INTO job_signatures (company, normalized_title, country, original_job_id)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (company, normalized_title, country)
                DO UPDATE SET
                    applied_date = CURRENT_TIMESTAMP,
                    original_job_id = EXCLUDED.original_job_id
            """, company, normalized_title, country, job_id)

            print(f"✅ Added job signature: '{normalized_title}' at {company}")
            return True

        except Exception as e:
            print(f"⚠️  Error adding job signature: {e}")
            return False
        finally:
            await self._release(conn)

    def _parse_datetime_string(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not date_string or date_string == "None":
            return None

        try:
            # Handle ISO format strings
            if isinstance(date_string, str):
                # Remove timezone info if present for simplicity
                if 'T' in date_string:
                    date_string = date_string.split('.')[0]  # Remove microseconds
                    date_string = date_string.replace('T', ' ')
                    return datetime.fromisoformat(date_string)
                else:
                    return datetime.fromisoformat(date_string)
            return date_string
        except Exception as e:
            print(f"Warning: Could not parse date '{date_string}': {e}")
            return None

    async def _ensure_pool(self):
        """Create connection pool if not already created."""
        if self._pool is not None:
            return
        try:
            self._pool = await asyncpg.create_pool(
                self.db_url,
                min_size=2,   # Keep 2 connections always ready
                max_size=10,  # Max 10 concurrent connections
                command_timeout=60,
                # DB-level safety net: any query running >2 min is cancelled by
                # PostgreSQL itself, so a slow query can never hold a connection
                # until Railway's 900s HTTP timeout kills the request and leaks it.
                server_settings={"statement_timeout": "120000"},
            )
            print("🔗 PostgreSQL connection pool created (min=2, max=10, statement_timeout=120s)")
        except Exception as e:
            print(f"❌ Failed to create connection pool: {e}")
            self.use_postgres = False

    async def get_connection(self):
        """Acquire a connection from the pool."""
        if not self.use_postgres:
            return None
        await self._ensure_pool()
        if self._pool is None:
            return None
        try:
            return await self._pool.acquire()
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None

    async def _release(self, conn):
        """Return a connection back to the pool."""
        if self._pool and conn:
            try:
                await self._pool.release(conn)
            except Exception:
                pass

    async def init_database(self):
        """Initialize database tables"""
        if not self.use_postgres:
            return True

        # Create pool eagerly on startup so the first real request doesn't pay for it
        await self._ensure_pool()

        conn = await self.get_connection()
        if not conn:
            return False
            
        try:
            # Read and execute schema
            with open('database_setup.sql', 'r') as f:
                schema = f.read()
            await conn.execute(schema)
            print("✅ Database initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
        finally:
            await self._release(conn)

    async def get_all_jobs(self) -> Dict[str, Any]:
        """Get all jobs from database or JSON"""
        if self.use_postgres:
            return await self._get_jobs_from_postgres()
        else:
            return self._get_jobs_from_json()

    async def _get_jobs_from_postgres(self) -> Dict[str, Any]:
        """Get jobs from PostgreSQL"""
        conn = await self.get_connection()
        if not conn:
            return self._get_jobs_from_json()
        
        try:
            # 7-day window keeps the query fast by capping result size.
            # enforce-country-limit runs every 2h and keeps per-type counts
            # manageable (1000 software, 100 marketing, 60 others per country)
            # so there should never be more than ~17k rows in this window.
            # Previously 14 days — caused 60s+ timeouts when enforce was down.
            jobs_query = """
                SELECT id, title, company, location, posted_date, job_url,
                       scraped_at, applied, rejected, is_new, easy_apply, category, notes,
                       first_seen, last_seen_24h, excluded, country, job_type, experience_level,
                       easy_apply_status, easy_apply_verified_at, easy_apply_verification_method
                FROM jobs
                WHERE scraped_at > NOW() - INTERVAL '7 days'
                ORDER BY scraped_at DESC
                LIMIT 20000
            """
            rows = await conn.fetch(jobs_query)

            # Convert to dictionary format
            jobs = {}
            for row in rows:
                job_data = {
                    "id": row['id'],
                    "title": row['title'],
                    "company": row['company'],
                    "location": row['location'],
                    "posted_date": row['posted_date'],
                    "job_url": row['job_url'],
                    "scraped_at": row['scraped_at'].isoformat() if row['scraped_at'] else None,
                    "applied": row['applied'],
                    "rejected": row['rejected'],
                    "is_new": row['is_new'],
                    "easy_apply": row['easy_apply'],
                    "category": row['category'],
                    "notes": row['notes'],
                    "first_seen": row['first_seen'].isoformat() if row['first_seen'] else None,
                    "last_seen_24h": row['last_seen_24h'].isoformat() if row['last_seen_24h'] else None,
                    "excluded": row['excluded'],
                    "country": row['country'],
                    "job_type": row['job_type'],
                    "experience_level": row['experience_level'],
                    "easy_apply_status": row['easy_apply_status'],
                    "easy_apply_verified_at": row['easy_apply_verified_at'].isoformat() if row['easy_apply_verified_at'] else None,
                    "easy_apply_verification_method": row['easy_apply_verification_method']
                }
                jobs[row['id']] = job_data
            
            # Add metadata
            stats_query = """
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(*) FILTER (WHERE applied = TRUE) as applied_jobs,
                    COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                    COUNT(*) FILTER (WHERE location ILIKE '%dublin%') as dublin_jobs,
                    COUNT(*) FILTER (WHERE category = 'last_24h') as last_24h_jobs,
                    MAX(scraped_at) as last_updated
                FROM jobs
            """
            stats = await conn.fetchrow(stats_query)
            
            result = {
                "_metadata": {
                    "last_updated": stats['last_updated'].isoformat() if stats['last_updated'] else None,
                    "total_jobs": stats['total_jobs'],
                    "dublin_jobs": stats['dublin_jobs'],
                    "new_jobs_count": stats['new_jobs'],
                    "last_24h_jobs_count": stats['last_24h_jobs'],
                    "applied_jobs": stats['applied_jobs'],
                    "database_type": "postgresql"
                },
                **jobs
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error fetching jobs from PostgreSQL: {e}")
            # Re-raise so the API returns a 500 instead of silently returning
            # 0 jobs (the JSON fallback file doesn't exist in production).
            raise
        finally:
            await self._release(conn)

    def _get_jobs_from_json(self) -> Dict[str, Any]:
        """Fallback: Get jobs from JSON file"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "_metadata" not in data:
                        data["_metadata"] = {
                            "database_type": "json_fallback",
                            "total_jobs": len([k for k in data.keys() if not k.startswith("_")])
                        }
                    return data
            else:
                return {
                    "_metadata": {
                        "database_type": "json_fallback",
                        "total_jobs": 0,
                        "message": "No jobs database found"
                    }
                }
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return {"_metadata": {"error": str(e), "database_type": "json_fallback"}}

    async def update_job_applied_status(self, job_id: str, applied: bool) -> bool:
        """Update job's applied status"""
        if self.use_postgres:
            return await self._update_job_postgres(job_id, applied)
        else:
            return self._update_job_json(job_id, applied)

    async def update_job_status(self, job_id: str, applied: Optional[bool] = None, rejected: Optional[bool] = None) -> bool:
        """Update job's applied and/or rejected status"""
        if self.use_postgres:
            return await self._update_job_status_postgres(job_id, applied, rejected)
        else:
            return self._update_job_status_json(job_id, applied, rejected)

    async def _update_job_postgres(self, job_id: str, applied: bool) -> bool:
        """Update job in PostgreSQL"""
        conn = await self.get_connection()
        if not conn:
            return self._update_job_json(job_id, applied)
        
        try:
            await conn.execute(
                "UPDATE jobs SET applied = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2",
                applied, job_id
            )
            return True
        except Exception as e:
            print(f"❌ Error updating job in PostgreSQL: {e}")
            return False
        finally:
            await self._release(conn)

    async def _update_job_status_postgres(self, job_id: str, applied: Optional[bool] = None, rejected: Optional[bool] = None) -> bool:
        """Update job applied and/or rejected status in PostgreSQL"""
        conn = await self.get_connection()
        if not conn:
            return self._update_job_status_json(job_id, applied, rejected)

        try:
            # First check if job exists and get its details
            existing = await conn.fetchrow("SELECT id, rejected, applied, title, company, country FROM jobs WHERE id = $1", job_id)
            if not existing:
                return False

            # Build dynamic SQL based on what fields need updating
            updates = []
            params = []
            param_count = 1

            if applied is not None:
                updates.append(f"applied = ${param_count}")
                params.append(applied)
                param_count += 1

            if rejected is not None:
                updates.append(f"rejected = ${param_count}")
                params.append(rejected)
                param_count += 1
                # If rejecting, also set applied to false
                if rejected and applied is None:
                    updates.append(f"applied = ${param_count}")
                    params.append(False)
                    param_count += 1

            if not updates:
                return True  # Nothing to update

            # Add job_id as last parameter
            params.append(job_id)

            # Build and execute query with explicit transaction
            query = f"UPDATE jobs SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ${param_count}"

            # Use explicit transaction to ensure changes are committed
            async with conn.transaction():
                result = await conn.execute(query, *params)

                # Check if any rows were affected (job was found and updated)
                rows_affected = int(result.split()[-1]) if result and 'UPDATE' in result else 0

            # If marking as applied OR rejected, add job signature for deduplication
            if (applied or rejected) and rows_affected > 0:
                await self.add_job_signature(
                    company=existing['company'],
                    title=existing['title'],
                    country=existing['country'],
                    job_id=job_id
                )
                if rejected:
                    print(f"✅ Added job signature for rejected job (will skip future reposts)")

            return rows_affected > 0
        except Exception as e:
            print(f"❌ Error updating job in PostgreSQL: {e}")
            return False
        finally:
            await self._release(conn)

    def _update_job_json(self, job_id: str, applied: bool) -> bool:
        """Fallback: Update job in JSON"""
        try:
            data = self._get_jobs_from_json()
            if job_id in data:
                data[job_id]['applied'] = applied
                with open(self.json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            return False
        except Exception as e:
            print(f"❌ Error updating JSON: {e}")
            return False

    def _update_job_status_json(self, job_id: str, applied: Optional[bool] = None, rejected: Optional[bool] = None) -> bool:
        """Fallback: Update job applied and/or rejected status in JSON"""
        try:
            data = self._get_jobs_from_json()
            if job_id in data:
                if applied is not None:
                    data[job_id]['applied'] = applied
                if rejected is not None:
                    data[job_id]['rejected'] = rejected
                    # If rejecting, also set applied to false
                    if rejected and applied is None:
                        data[job_id]['applied'] = False

                with open(self.json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            return False
        except Exception as e:
            print(f"❌ Error updating JSON: {e}")
            return False

    async def sync_jobs_from_scraper(self, jobs_data: Dict[str, Any]) -> Dict[str, int]:
        """Sync jobs from local scraper"""
        if self.use_postgres:
            return await self._sync_jobs_postgres(jobs_data)
        else:
            return self._sync_jobs_json(jobs_data)

    async def _cleanup_old_jobs_postgres(self, conn, max_jobs_per_country: int = 300) -> int:
        """Delete old jobs from PostgreSQL, keeping only max_jobs_per_country most recent per country

        IMPORTANT: Never deletes jobs that users have interacted with (applied/rejected/saved)
        """
        try:
            # Get list of countries
            countries = await conn.fetch("""
                SELECT DISTINCT country FROM jobs WHERE country IS NOT NULL
            """)

            total_deleted = 0

            for row in countries:
                country = row['country']

                # Delete old jobs for this country, keeping max_jobs_per_country newest
                # CRITICAL: Exclude jobs that users have interacted with
                result = await conn.execute("""
                    DELETE FROM jobs
                    WHERE id IN (
                        SELECT id FROM (
                            SELECT
                                id,
                                ROW_NUMBER() OVER (
                                    PARTITION BY country
                                    ORDER BY scraped_at DESC NULLS LAST
                                ) as rn
                            FROM jobs
                            WHERE country = $1
                            -- CRITICAL: Don't delete jobs users have interacted with
                            AND NOT EXISTS (
                                SELECT 1 FROM user_job_interactions uji
                                WHERE uji.job_id = jobs.id
                            )
                        ) ranked
                        WHERE rn > $2
                    )
                """, country, max_jobs_per_country)

                # Extract deleted count from result like "DELETE 50"
                deleted_count = int(result.split()[-1]) if result and result.split() else 0
                if deleted_count > 0:
                    print(f"   ✂️ {country}: Removed {deleted_count} old jobs (kept {max_jobs_per_country} newest)")
                    total_deleted += deleted_count

            return total_deleted

        except Exception as e:
            print(f"⚠️  Warning: Could not clean up old jobs: {e}")
            return 0

    def _clean_job_row(self, job_id: str, job_data: Dict[str, Any], is_update: bool):
        """Return a tuple of cleaned values for INSERT or UPDATE, matching the jobs table columns."""
        title    = str(job_data['title'])[:500]      if job_data.get('title')      else 'No title'
        company  = str(job_data['company'])[:300]    if job_data.get('company')    else 'Unknown'
        location = str(job_data['location'])[:300]   if job_data.get('location')   else ''
        posted_date = str(job_data['posted_date'])[:100] if job_data.get('posted_date') else ''
        job_url  = job_data.get('job_url', '')
        country  = str(job_data['country'])[:100]    if job_data.get('country')    else None
        job_type = str(job_data['job_type'])[:50]    if job_data.get('job_type')   else None
        experience_level = str(job_data['experience_level'])[:50] if job_data.get('experience_level') else None
        easy_apply = bool(job_data.get('easy_apply', False))
        easy_apply_status = str(job_data.get('easy_apply_status', 'unverified'))[:50]
        easy_apply_verified_at = self._parse_datetime_string(job_data.get('easy_apply_verified_at'))
        easy_apply_verification_method = str(job_data['easy_apply_verification_method'])[:100] if job_data.get('easy_apply_verification_method') else None

        if is_update:
            is_new = bool(job_data.get('is_new', False))
            # UPDATE tuple order matches the SQL below: id first for WHERE clause
            return (job_id, title, company, location, posted_date, job_url, is_new, easy_apply,
                    country, job_type, experience_level, easy_apply_status,
                    easy_apply_verified_at, easy_apply_verification_method)
        else:
            applied  = bool(job_data.get('applied', False))
            is_new   = bool(job_data.get('is_new', True))
            # INSERT tuple order matches the column list below
            return (job_id, title, company, location, posted_date, job_url, applied, is_new,
                    easy_apply, country, job_type, experience_level, easy_apply_status,
                    easy_apply_verified_at, easy_apply_verification_method)

    async def _sync_jobs_postgres(self, jobs_data: Dict[str, Any]) -> Dict[str, int]:
        """Sync jobs to PostgreSQL using bulk operations (4 queries regardless of batch size)."""
        conn = await self.get_connection()
        if not conn:
            return self._sync_jobs_json(jobs_data)

        try:
            # ── 1. Collect real job entries (skip metadata keys) ──────────────
            incoming = {k: v for k, v in jobs_data.items() if not k.startswith('_')}
            if not incoming:
                return {"new_jobs": 0, "updated_jobs": 0, "skipped_reposts": 0,
                        "new_software": 0, "new_hr": 0, "new_cybersecurity": 0,
                        "new_sales": 0, "new_finance": 0, "new_marketing": 0,
                        "new_biotech": 0, "new_engineering": 0, "new_events": 0,
                        "deleted_jobs": 0}

            all_ids = list(incoming.keys())

            # ── 2. Single query: which IDs already exist? ─────────────────────
            existing_ids = {
                row['id']
                for row in await conn.fetch(
                    "SELECT id FROM jobs WHERE id = ANY($1::text[])", all_ids
                )
            }

            new_candidate_ids  = [jid for jid in all_ids if jid not in existing_ids]
            update_ids         = [jid for jid in all_ids if jid in existing_ids]

            # ── 3. Single query: bulk repost check for all new candidates ─────
            skipped_reposts = 0
            insert_ids = new_candidate_ids  # assume all pass; filter below

            if new_candidate_ids:
                cutoff = datetime.now() - timedelta(days=30)
                # Build (company_lower, normalized_title) pairs for all new jobs
                candidate_pairs = []
                for jid in new_candidate_ids:
                    jd = incoming[jid]
                    company = str(jd.get('company', '') or '').strip()
                    title   = str(jd.get('title',   '') or '').strip()
                    norm    = self.normalize_job_title(title)
                    if company and norm:
                        candidate_pairs.append((jid, company.lower(), norm))

                if candidate_pairs:
                    companies  = [p[1] for p in candidate_pairs]
                    norm_titles = [p[2] for p in candidate_pairs]

                    repost_sigs = await conn.fetch("""
                        SELECT LOWER(js.company) AS company, js.normalized_title
                        FROM job_signatures js
                        WHERE js.applied_date >= $1
                          AND LOWER(js.company) = ANY($2::text[])
                          AND js.normalized_title = ANY($3::text[])
                    """, cutoff, companies, norm_titles)

                    repost_set = {(r['company'], r['normalized_title']) for r in repost_sigs}

                    repost_ids = set()
                    for jid, comp_lower, norm in candidate_pairs:
                        if (comp_lower, norm) in repost_set:
                            jd = incoming[jid]
                            print(f"⏭️  Skipping repost: '{jd.get('title')}' at {jd.get('company')}")
                            repost_ids.add(jid)
                            skipped_reposts += 1

                    insert_ids = [jid for jid in new_candidate_ids if jid not in repost_ids]

            # ── 4a. Bulk INSERT new jobs ───────────────────────────────────────
            if insert_ids:
                insert_rows = [self._clean_job_row(jid, incoming[jid], is_update=False)
                               for jid in insert_ids]
                await conn.executemany("""
                    INSERT INTO jobs (id, title, company, location, posted_date, job_url,
                                      applied, is_new, easy_apply, country, job_type,
                                      experience_level, easy_apply_status,
                                      easy_apply_verified_at, easy_apply_verification_method)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)
                    ON CONFLICT (id) DO NOTHING
                """, insert_rows)

            # ── 4b. Bulk UPDATE existing jobs ─────────────────────────────────
            if update_ids:
                update_rows = [self._clean_job_row(jid, incoming[jid], is_update=True)
                               for jid in update_ids]
                await conn.executemany("""
                    UPDATE jobs SET
                        title=$2, company=$3, location=$4, posted_date=$5,
                        job_url=$6, is_new=$7, easy_apply=$8,
                        country=$9, job_type=$10, experience_level=$11,
                        easy_apply_status=$12, easy_apply_verified_at=$13,
                        easy_apply_verification_method=$14
                    WHERE id=$1
                """, update_rows)

            # ── 5. Count new jobs by type ─────────────────────────────────────
            type_counts = {t: 0 for t in ('software','hr','cybersecurity','sales',
                                           'finance','marketing','biotech','engineering','events')}
            for jid in insert_ids:
                jt = incoming[jid].get('job_type') or ''
                if jt in type_counts:
                    type_counts[jt] += 1

            new_jobs    = len(insert_ids)
            updated_jobs = len(update_ids)

            # ── 6. Log scraping session ───────────────────────────────────────
            await conn.execute("""
                INSERT INTO scraping_sessions (total_jobs_found, new_jobs_count, updated_jobs_count, notes)
                VALUES ($1, $2, $3, $4)
            """, len(incoming), new_jobs, updated_jobs, "Synced from local scraper")

            print(f"✅ PostgreSQL: {new_jobs} new, {updated_jobs} updated, {skipped_reposts} reposts skipped "
                  f"({type_counts['software']} sw, {type_counts['hr']} hr, {type_counts['cybersecurity']} cyber, "
                  f"{type_counts['sales']} sales, {type_counts['finance']} fin, {type_counts['marketing']} mkt, "
                  f"{type_counts['biotech']} bio, {type_counts['engineering']} eng, {type_counts['events']} evt)")

            return {
                "new_jobs":          new_jobs,
                "new_software":      type_counts['software'],
                "new_hr":            type_counts['hr'],
                "new_cybersecurity": type_counts['cybersecurity'],
                "new_sales":         type_counts['sales'],
                "new_finance":       type_counts['finance'],
                "new_marketing":     type_counts['marketing'],
                "new_biotech":       type_counts['biotech'],
                "new_engineering":   type_counts['engineering'],
                "new_events":        type_counts['events'],
                "updated_jobs":      updated_jobs,
                "deleted_jobs":      0,
                "skipped_reposts":   skipped_reposts,
            }

        except Exception as e:
            print(f"❌ Error syncing to PostgreSQL: {e}")
            return {"error": str(e)}
        finally:
            await self._release(conn)

    def _sync_jobs_json(self, jobs_data: Dict[str, Any]) -> Dict[str, int]:
        """Fallback: Sync jobs to JSON"""
        try:
            existing_data = self._get_jobs_from_json()
            new_jobs = 0
            updated_jobs = 0
            
            for job_id, job_data in jobs_data.items():
                if job_id.startswith("_"):
                    continue
                    
                if job_id in existing_data:
                    # Preserve applied status
                    job_data['applied'] = existing_data[job_id].get('applied', False)
                    updated_jobs += 1
                else:
                    new_jobs += 1
                
                existing_data[job_id] = job_data
            
            # Update metadata
            existing_data["_metadata"] = {
                "last_updated": datetime.now().isoformat(),
                "total_jobs": len([k for k in existing_data.keys() if not k.startswith("_")]),
                "database_type": "json_fallback",
                "last_sync": datetime.now().isoformat()
            }
            
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            return {"new_jobs": new_jobs, "updated_jobs": updated_jobs}
            
        except Exception as e:
            print(f"❌ Error syncing JSON: {e}")
            return {"error": str(e)}