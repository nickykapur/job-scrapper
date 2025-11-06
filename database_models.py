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

    async def check_if_repost(self, company: str, title: str, country: str, days_window: int = 30) -> Tuple[bool, Optional[str]]:
        """
        Check if a job is likely a repost of a job the user has already applied to.

        Args:
            company: Company name
            title: Job title
            country: Country where job is located
            days_window: Number of days to look back for similar jobs (default 30)

        Returns:
            Tuple of (is_repost: bool, original_job_id: Optional[str])
        """
        if not self.use_postgres:
            return False, None

        normalized_title = self.normalize_job_title(title)
        if not normalized_title:
            return False, None

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
            await conn.close()

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
            await conn.close()

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

    async def get_connection(self):
        """Get database connection"""
        if not self.use_postgres:
            return None
        
        try:
            return await asyncpg.connect(self.db_url)
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.use_postgres = False
            return None

    async def init_database(self):
        """Initialize database tables"""
        if not self.use_postgres:
            return True
            
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
            await conn.close()

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
            # Get jobs
            jobs_query = """
                SELECT id, title, company, location, posted_date, job_url,
                       scraped_at, applied, rejected, is_new, easy_apply, category, notes,
                       first_seen, last_seen_24h, excluded, country, job_type, experience_level
                FROM jobs
                ORDER BY scraped_at DESC
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
                    "experience_level": row['experience_level']
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
            return self._get_jobs_from_json()
        finally:
            await conn.close()

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
            await conn.close()

    async def _update_job_status_postgres(self, job_id: str, applied: Optional[bool] = None, rejected: Optional[bool] = None) -> bool:
        """Update job applied and/or rejected status in PostgreSQL"""
        print(f"🔄 DEBUG: _update_job_status_postgres called for job {job_id} - applied: {applied}, rejected: {rejected}")

        conn = await self.get_connection()
        if not conn:
            print(f"❌ DEBUG: No PostgreSQL connection, falling back to JSON")
            return self._update_job_status_json(job_id, applied, rejected)

        try:
            # First check if job exists and get its details
            existing = await conn.fetchrow("SELECT id, rejected, applied, title, company, country FROM jobs WHERE id = $1", job_id)
            if not existing:
                print(f"❌ DEBUG: Job {job_id} not found in PostgreSQL database")
                return False

            print(f"✅ DEBUG: Found job {job_id} in database - current status: rejected={existing['rejected']}, applied={existing['applied']}")

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
            print(f"🔄 DEBUG: Executing SQL: {query}")
            print(f"🔄 DEBUG: With parameters: {params}")

            # Use explicit transaction to ensure changes are committed
            async with conn.transaction():
                result = await conn.execute(query, *params)
                print(f"✅ DEBUG: SQL execution result: {result}")

                # Check if any rows were affected (job was found and updated)
                rows_affected = int(result.split()[-1]) if result and 'UPDATE' in result else 0
                print(f"✅ DEBUG: Rows affected: {rows_affected}")

                if rows_affected > 0:
                    # Verify the update by reading the job back WITHIN the same transaction
                    updated_job = await conn.fetchrow("SELECT id, rejected, applied FROM jobs WHERE id = $1", job_id)
                    if updated_job:
                        print(f"✅ DEBUG: After update WITHIN transaction - job {job_id}: rejected={updated_job['rejected']}, applied={updated_job['applied']}")
                    else:
                        print(f"❌ DEBUG: Could not verify update - job {job_id} not found after update")

            # Verify the update OUTSIDE the transaction to confirm persistence
            final_check = await conn.fetchrow("SELECT id, rejected, applied FROM jobs WHERE id = $1", job_id)
            if final_check:
                print(f"🔍 DEBUG: Final verification OUTSIDE transaction - job {job_id}: rejected={final_check['rejected']}, applied={final_check['applied']}")
            else:
                print(f"❌ DEBUG: Final verification failed - job {job_id} not found")

            # If marking as applied, add job signature for deduplication
            if applied and rows_affected > 0:
                await self.add_job_signature(
                    company=existing['company'],
                    title=existing['title'],
                    country=existing['country'],
                    job_id=job_id
                )

            return rows_affected > 0
        except Exception as e:
            print(f"❌ Error updating job in PostgreSQL: {e}")
            return False
        finally:
            await conn.close()

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
        """Delete old jobs from PostgreSQL, keeping only max_jobs_per_country most recent per country"""
        try:
            # Get list of countries
            countries = await conn.fetch("""
                SELECT DISTINCT country FROM jobs WHERE country IS NOT NULL
            """)

            total_deleted = 0

            for row in countries:
                country = row['country']

                # Delete old jobs for this country, keeping max_jobs_per_country newest
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

    async def _sync_jobs_postgres(self, jobs_data: Dict[str, Any]) -> Dict[str, int]:
        """Sync jobs to PostgreSQL"""
        conn = await self.get_connection()
        if not conn:
            return self._sync_jobs_json(jobs_data)

        try:
            new_jobs = 0
            updated_jobs = 0
            new_software = 0
            new_hr = 0
            skipped_reposts = 0

            for job_id, job_data in jobs_data.items():
                if job_id.startswith("_"):  # Skip metadata
                    continue

                # Check if job exists
                existing = await conn.fetchrow("SELECT id, applied FROM jobs WHERE id = $1", job_id)

                # If this is a new job, check if it's a repost
                if not existing:
                    title = str(job_data['title'])[:500] if job_data.get('title') else 'No title'
                    company = str(job_data['company'])[:300] if job_data.get('company') else 'Unknown'
                    country = str(job_data.get('country', ''))[:100] if job_data.get('country') else None

                    is_repost, original_job_id = await self.check_if_repost(company, title, country, days_window=30)

                    if is_repost:
                        print(f"⏭️  Skipping repost: '{title}' at {company} (you applied to a similar job)")
                        skipped_reposts += 1
                        continue  # Skip this job entirely

                if existing:
                    # Update existing job, preserve applied status
                    scraped_at = self._parse_datetime_string(job_data.get('scraped_at'))
                    is_new_bool = bool(job_data.get('is_new', False))

                    # Clean and limit string fields
                    title = str(job_data['title'])[:500] if job_data.get('title') else 'No title'
                    company = str(job_data['company'])[:300] if job_data.get('company') else 'Unknown'
                    location = str(job_data['location'])[:300] if job_data.get('location') else ''
                    posted_date = str(job_data['posted_date'])[:100] if job_data.get('posted_date') else ''
                    category = str(job_data.get('category', ''))[:50] if job_data.get('category') else None

                    # Update with all fields including country, job_type, experience_level
                    easy_apply_bool = bool(job_data.get('easy_apply', False))
                    country = str(job_data.get('country', ''))[:100] if job_data.get('country') else None
                    job_type = str(job_data.get('job_type', ''))[:50] if job_data.get('job_type') else None
                    experience_level = str(job_data.get('experience_level', ''))[:50] if job_data.get('experience_level') else None

                    await conn.execute("""
                        UPDATE jobs SET
                            title = $2, company = $3, location = $4, posted_date = $5,
                            job_url = $6, is_new = $7, easy_apply = $8,
                            country = $9, job_type = $10, experience_level = $11
                        WHERE id = $1
                    """, job_id, title, company, location, posted_date, job_data['job_url'], is_new_bool, easy_apply_bool,
                         country, job_type, experience_level)
                    updated_jobs += 1
                else:
                    # Insert new job
                    scraped_at = self._parse_datetime_string(job_data.get('scraped_at'))
                    first_seen = self._parse_datetime_string(job_data.get('first_seen'))

                    # Ensure proper data types for database consistency
                    applied_bool = bool(job_data.get('applied', False))
                    is_new_bool = bool(job_data.get('is_new', True))

                    # Clean and limit string fields to prevent type errors
                    title = str(job_data['title'])[:500] if job_data.get('title') else 'No title'
                    company = str(job_data['company'])[:300] if job_data.get('company') else 'Unknown'
                    location = str(job_data['location'])[:300] if job_data.get('location') else ''
                    posted_date = str(job_data['posted_date'])[:100] if job_data.get('posted_date') else ''
                    category = str(job_data.get('category', ''))[:50] if job_data.get('category') else None

                    # Extract new fields
                    country = str(job_data.get('country', ''))[:100] if job_data.get('country') else None
                    job_type = str(job_data.get('job_type', ''))[:50] if job_data.get('job_type') else None
                    experience_level = str(job_data.get('experience_level', ''))[:50] if job_data.get('experience_level') else None

                    # INSERT with all fields including country, job_type, experience_level
                    easy_apply_bool = bool(job_data.get('easy_apply', False))
                    await conn.execute("""
                        INSERT INTO jobs (id, title, company, location, posted_date, job_url, applied, is_new, easy_apply, country, job_type, experience_level)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    """, job_id, title, company, location, posted_date, job_data['job_url'], applied_bool, is_new_bool, easy_apply_bool,
                         country, job_type, experience_level)
                    new_jobs += 1

                    # Track software vs HR new jobs
                    if job_type == 'software':
                        new_software += 1
                    elif job_type == 'hr':
                        new_hr += 1
            
            # Log scraping session
            await conn.execute("""
                INSERT INTO scraping_sessions (total_jobs_found, new_jobs_count, updated_jobs_count, notes)
                VALUES ($1, $2, $3, $4)
            """, len(jobs_data), new_jobs, updated_jobs, f"Synced from local scraper")

            print(f"✅ PostgreSQL: {new_jobs} new jobs ({new_software} software, {new_hr} HR), {updated_jobs} updated jobs")
            if skipped_reposts > 0:
                print(f"⏭️  Skipped {skipped_reposts} reposted jobs (already applied to similar positions)")

            # IMPORTANT: Clean up old jobs to maintain 300 per country limit
            print(f"\n✂️ Cleaning up old jobs (maintaining 300 per country)...")
            deleted_jobs = await self._cleanup_old_jobs_postgres(conn, max_jobs_per_country=300)
            if deleted_jobs > 0:
                print(f"🗑️  PostgreSQL: Deleted {deleted_jobs} old jobs total")
            else:
                print(f"✅ No cleanup needed - all countries within limit")

            return {
                "new_jobs": new_jobs,
                "new_software": new_software,
                "new_hr": new_hr,
                "updated_jobs": updated_jobs,
                "deleted_jobs": deleted_jobs,
                "skipped_reposts": skipped_reposts
            }

        except Exception as e:
            print(f"❌ Error syncing to PostgreSQL: {e}")
            return {"error": str(e)}
        finally:
            await conn.close()

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