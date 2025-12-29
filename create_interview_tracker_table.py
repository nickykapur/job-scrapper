#!/usr/bin/env python3
"""
Create interview_tracker table in PostgreSQL database
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def create_interview_tracker_table():
    """Create the interview_tracker table"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        return

    conn = await asyncpg.connect(db_url)

    try:
        # Create table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS interview_tracker (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                location TEXT NOT NULL,
                stage TEXT NOT NULL CHECK (stage IN ('recruiter', 'technical', 'final')),
                application_date DATE NOT NULL,
                recruiter_date DATE,
                technical_date DATE,
                final_date DATE,
                expected_response_date DATE,
                salary_range TEXT,
                recruiter_contact TEXT,
                recruiter_email TEXT,
                notes TEXT,
                stage_notes JSONB DEFAULT '{}',
                last_updated TIMESTAMP NOT NULL,
                archived BOOLEAN DEFAULT FALSE,
                archive_outcome TEXT CHECK (archive_outcome IN ('rejected', 'no-response', 'accepted', 'declined')),
                archive_date TIMESTAMP,
                archive_notes TEXT,
                rejection_stage TEXT CHECK (rejection_stage IN ('recruiter', 'technical', 'final', 'application')),
                rejection_reasons TEXT[],
                rejection_details TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_interview_tracker_user
            ON interview_tracker(user_id)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_interview_tracker_archived
            ON interview_tracker(user_id, archived)
        """)

        print("✅ interview_tracker table created successfully")

    except Exception as e:
        print(f"❌ Error creating table: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_interview_tracker_table())
