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
                    await conn.execute("""
                        UPDATE jobs SET
                            title = $2, company = $3, location = $4, posted_date = $5,
                            job_url = $6, scraped_at = $7, is_new = $8, category = $9,
                            last_seen_24h = CASE WHEN $9 = 'last_24h' THEN CURRENT_TIMESTAMP ELSE last_seen_24h END,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = $1
                    """, job_id, job_data['title'], job_data['company'], job_data['location'],
                        job_data['posted_date'], job_data['job_url'], scraped_at,
                        job_data.get('is_new', False), job_data.get('category'))
                    updated_jobs += 1
                else:
                    # Insert new job
                    scraped_at = self._parse_datetime_string(job_data.get('scraped_at'))
                    first_seen = self._parse_datetime_string(job_data.get('first_seen'))
                    await conn.execute("""
                        INSERT INTO jobs (id, title, company, location, posted_date, job_url,
                                        scraped_at, applied, is_new, category, first_seen)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """, job_id, job_data['title'], job_data['company'], job_data['location'],
                        job_data['posted_date'], job_data['job_url'], scraped_at,
                        job_data.get('applied', False), job_data.get('is_new', True),
                        job_data.get('category'), first_seen or datetime.now())
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