#!/usr/bin/env python3
"""
Database models and utilities for LinkedIn Job Manager
Supports both PostgreSQL and JSON fallback
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
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
                       scraped_at, applied, is_new, category, notes,
                       first_seen, last_seen_24h, excluded
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
                    "is_new": row['is_new'],
                    "category": row['category'],
                    "notes": row['notes'],
                    "first_seen": row['first_seen'].isoformat() if row['first_seen'] else None,
                    "last_seen_24h": row['last_seen_24h'].isoformat() if row['last_seen_24h'] else None,
                    "excluded": row['excluded']
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
        conn = await self.get_connection()
        if not conn:
            return self._update_job_status_json(job_id, applied, rejected)

        try:
            # First check if job exists
            existing = await conn.fetchrow("SELECT id FROM jobs WHERE id = $1", job_id)
            if not existing:
                print(f"❌ Job {job_id} not found in PostgreSQL database")
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

            # Build and execute query
            query = f"UPDATE jobs SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ${param_count}"
            result = await conn.execute(query, *params)

            # Check if any rows were affected (job was found and updated)
            rows_affected = int(result.split()[-1]) if result and 'UPDATE' in result else 0
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

    async def _sync_jobs_postgres(self, jobs_data: Dict[str, Any]) -> Dict[str, int]:
        """Sync jobs to PostgreSQL"""
        conn = await self.get_connection()
        if not conn:
            return self._sync_jobs_json(jobs_data)
        
        try:
            new_jobs = 0
            updated_jobs = 0
            
            for job_id, job_data in jobs_data.items():
                if job_id.startswith("_"):  # Skip metadata
                    continue
                
                # Check if job exists
                existing = await conn.fetchrow("SELECT id, applied FROM jobs WHERE id = $1", job_id)
                
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

                    # Use simpler UPDATE with only core fields
                    await conn.execute("""
                        UPDATE jobs SET
                            title = $2, company = $3, location = $4, posted_date = $5,
                            job_url = $6, is_new = $7
                        WHERE id = $1
                    """, job_id, title, company, location, posted_date, job_data['job_url'], is_new_bool)
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

                    # Use simpler INSERT with only core fields to avoid schema mismatches
                    await conn.execute("""
                        INSERT INTO jobs (id, title, company, location, posted_date, job_url, applied, is_new)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """, job_id, title, company, location, posted_date, job_data['job_url'], applied_bool, is_new_bool)
                    new_jobs += 1
            
            # Log scraping session
            await conn.execute("""
                INSERT INTO scraping_sessions (total_jobs_found, new_jobs_count, updated_jobs_count, notes)
                VALUES ($1, $2, $3, $4)
            """, len(jobs_data), new_jobs, updated_jobs, f"Synced from local scraper")
            
            return {"new_jobs": new_jobs, "updated_jobs": updated_jobs}
            
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