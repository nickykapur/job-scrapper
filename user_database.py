#!/usr/bin/env python3
"""
User database operations for LinkedIn Job Manager
Handles user authentication, preferences, and job interactions
"""

import os
from typing import Optional, Dict, List, Any
from datetime import datetime
import asyncpg
from auth_utils import hash_password, verify_password


class UserDatabase:
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        self.use_postgres = bool(self.db_url)

        if not self.use_postgres:
            print("⚠️  User database requires PostgreSQL")

    async def get_connection(self):
        """Get database connection"""
        if not self.use_postgres:
            return None

        try:
            return await asyncpg.connect(self.db_url)
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None

    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new user

        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            full_name: User's full name
            is_admin: Whether user has admin privileges

        Returns:
            User data dict if successful, None if failed
        """
        conn = await self.get_connection()
        if not conn:
            return None

        try:
            # Hash the password
            password_hash = hash_password(password)

            # Insert user
            user = await conn.fetchrow(
                """
                INSERT INTO users (username, email, password_hash, full_name, is_admin)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, username, email, full_name, is_admin, created_at
                """,
                username, email, password_hash, full_name, is_admin
            )

            # Create default preferences for the user
            await conn.execute(
                """
                INSERT INTO user_preferences (user_id)
                VALUES ($1)
                """,
                user['id']
            )

            return dict(user)

        except asyncpg.UniqueViolationError as e:
            # Username or email already exists
            if 'username' in str(e):
                print(f"❌ Username '{username}' already exists")
            elif 'email' in str(e):
                print(f"❌ Email '{email}' already exists")
            return None
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
        finally:
            await conn.close()

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        conn = await self.get_connection()
        if not conn:
            return None

        try:
            user = await conn.fetchrow(
                """
                SELECT id, username, email, password_hash, full_name, is_admin, is_active, created_at, last_login
                FROM users
                WHERE username = $1 AND is_active = TRUE
                """,
                username
            )

            if user:
                return dict(user)
            return None

        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
        finally:
            await conn.close()

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        conn = await self.get_connection()
        if not conn:
            return None

        try:
            user = await conn.fetchrow(
                """
                SELECT id, username, email, password_hash, full_name, is_admin, is_active, created_at, last_login
                FROM users
                WHERE email = $1 AND is_active = TRUE
                """,
                email
            )

            if user:
                return dict(user)
            return None

        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
        finally:
            await conn.close()

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = await self.get_connection()
        if not conn:
            return None

        try:
            user = await conn.fetchrow(
                """
                SELECT id, username, email, full_name, is_admin, is_active, created_at, last_login
                FROM users
                WHERE id = $1 AND is_active = TRUE
                """,
                user_id
            )

            if user:
                return dict(user)
            return None

        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
        finally:
            await conn.close()

    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with username and password

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            User data if authentication successful, None otherwise
        """
        # Try username first
        user = await self.get_user_by_username(username)

        # If not found, try email
        if not user:
            user = await self.get_user_by_email(username)

        if not user:
            return None

        # Verify password
        if not verify_password(password, user['password_hash']):
            return None

        # Update last login
        await self.update_last_login(user['id'])

        # Remove password hash from returned data
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        return user_data

    async def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        conn = await self.get_connection()
        if not conn:
            return False

        try:
            await conn.execute(
                """
                UPDATE users
                SET last_login = $1
                WHERE id = $2
                """,
                datetime.utcnow(), user_id
            )
            return True
        except Exception as e:
            print(f"❌ Error updating last login: {e}")
            return False
        finally:
            await conn.close()

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        conn = await self.get_connection()
        if not conn:
            return False

        try:
            # Get current password hash
            user = await conn.fetchrow(
                "SELECT password_hash FROM users WHERE id = $1",
                user_id
            )

            if not user:
                return False

            # Verify old password
            if not verify_password(old_password, user['password_hash']):
                return False

            # Hash new password
            new_hash = hash_password(new_password)

            # Update password
            await conn.execute(
                """
                UPDATE users
                SET password_hash = $1, updated_at = $2
                WHERE id = $3
                """,
                new_hash, datetime.utcnow(), user_id
            )

            return True

        except Exception as e:
            print(f"❌ Error changing password: {e}")
            return False
        finally:
            await conn.close()

    # ========================================================================
    # USER PREFERENCES
    # ========================================================================

    async def get_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        conn = await self.get_connection()
        if not conn:
            return None

        try:
            prefs = await conn.fetchrow(
                """
                SELECT *
                FROM user_preferences
                WHERE user_id = $1
                """,
                user_id
            )

            if prefs:
                return dict(prefs)
            return None

        except Exception as e:
            print(f"❌ Error getting preferences: {e}")
            return None
        finally:
            await conn.close()

    async def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        conn = await self.get_connection()
        if not conn:
            return False

        try:
            # Build dynamic update query based on provided fields
            update_fields = []
            values = []
            param_count = 1

            allowed_fields = [
                'job_types', 'keywords', 'excluded_keywords',
                'experience_levels', 'exclude_senior',
                'preferred_countries', 'preferred_cities', 'exclude_locations',
                'excluded_companies', 'preferred_companies',
                'easy_apply_only', 'remote_only',
                'email_notifications', 'daily_digest'
            ]

            for field in allowed_fields:
                if field in preferences:
                    update_fields.append(f"{field} = ${param_count}")
                    values.append(preferences[field])
                    param_count += 1

            if not update_fields:
                return True  # Nothing to update

            # Add updated_at
            update_fields.append(f"updated_at = ${param_count}")
            values.append(datetime.utcnow())
            param_count += 1

            # Add user_id for WHERE clause
            values.append(user_id)

            query = f"""
                UPDATE user_preferences
                SET {', '.join(update_fields)}
                WHERE user_id = ${param_count}
            """

            await conn.execute(query, *values)
            return True

        except Exception as e:
            print(f"❌ Error updating preferences: {e}")
            return False
        finally:
            await conn.close()

    # ========================================================================
    # USER JOB INTERACTIONS
    # ========================================================================

    async def get_user_job_interaction(self, user_id: int, job_id: str) -> Optional[Dict[str, Any]]:
        """Get user's interaction with a specific job"""
        conn = await self.get_connection()
        if not conn:
            return None

        try:
            interaction = await conn.fetchrow(
                """
                SELECT *
                FROM user_job_interactions
                WHERE user_id = $1 AND job_id = $2
                """,
                user_id, job_id
            )

            if interaction:
                return dict(interaction)
            return None

        except Exception as e:
            print(f"❌ Error getting interaction: {e}")
            return None
        finally:
            await conn.close()

    async def update_job_interaction(
        self,
        user_id: int,
        job_id: str,
        applied: Optional[bool] = None,
        rejected: Optional[bool] = None,
        saved: Optional[bool] = None,
        hidden: Optional[bool] = None,
        notes: Optional[str] = None,
        rating: Optional[int] = None
    ) -> bool:
        """
        Update or create user's interaction with a job

        Args:
            user_id: User ID
            job_id: Job ID
            applied: Mark as applied
            rejected: Mark as rejected
            saved: Mark as saved
            hidden: Mark as hidden
            notes: User notes
            rating: User rating (1-5)

        Returns:
            True if successful, False otherwise
        """
        conn = await self.get_connection()
        if not conn:
            return False

        try:
            # Check if interaction exists
            existing = await self.get_user_job_interaction(user_id, job_id)

            if existing:
                # Update existing interaction
                update_fields = []
                values = []
                param_count = 1

                if applied is not None:
                    update_fields.append(f"applied = ${param_count}")
                    values.append(applied)
                    param_count += 1
                    if applied:
                        update_fields.append(f"applied_at = ${param_count}")
                        values.append(datetime.utcnow())
                        param_count += 1

                if rejected is not None:
                    update_fields.append(f"rejected = ${param_count}")
                    values.append(rejected)
                    param_count += 1
                    if rejected:
                        update_fields.append(f"rejected_at = ${param_count}")
                        values.append(datetime.utcnow())
                        param_count += 1

                if saved is not None:
                    update_fields.append(f"saved = ${param_count}")
                    values.append(saved)
                    param_count += 1
                    if saved:
                        update_fields.append(f"saved_at = ${param_count}")
                        values.append(datetime.utcnow())
                        param_count += 1

                if hidden is not None:
                    update_fields.append(f"hidden = ${param_count}")
                    values.append(hidden)
                    param_count += 1

                if notes is not None:
                    update_fields.append(f"notes = ${param_count}")
                    values.append(notes)
                    param_count += 1

                if rating is not None:
                    update_fields.append(f"rating = ${param_count}")
                    values.append(rating)
                    param_count += 1

                # Add updated_at
                update_fields.append(f"updated_at = ${param_count}")
                values.append(datetime.utcnow())
                param_count += 1

                # Add WHERE clause parameters
                values.extend([user_id, job_id])

                query = f"""
                    UPDATE user_job_interactions
                    SET {', '.join(update_fields)}
                    WHERE user_id = ${param_count} AND job_id = ${param_count + 1}
                """

                await conn.execute(query, *values)

            else:
                # Create new interaction
                await conn.execute(
                    """
                    INSERT INTO user_job_interactions
                    (user_id, job_id, applied, rejected, saved, hidden, notes, rating, applied_at, rejected_at, saved_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """,
                    user_id, job_id,
                    applied if applied is not None else False,
                    rejected if rejected is not None else False,
                    saved if saved is not None else False,
                    hidden if hidden is not None else False,
                    notes,
                    rating,
                    datetime.utcnow() if applied else None,
                    datetime.utcnow() if rejected else None,
                    datetime.utcnow() if saved else None
                )

            return True

        except Exception as e:
            print(f"❌ Error updating interaction: {e}")
            return False
        finally:
            await conn.close()

    async def get_user_applied_jobs(self, user_id: int) -> List[str]:
        """Get list of job IDs user has applied to"""
        conn = await self.get_connection()
        if not conn:
            return []

        try:
            rows = await conn.fetch(
                """
                SELECT job_id
                FROM user_job_interactions
                WHERE user_id = $1 AND applied = TRUE
                ORDER BY applied_at DESC
                """,
                user_id
            )

            return [row['job_id'] for row in rows]

        except Exception as e:
            print(f"❌ Error getting applied jobs: {e}")
            return []
        finally:
            await conn.close()

    async def get_user_rejected_jobs(self, user_id: int) -> List[str]:
        """Get list of job IDs user has rejected"""
        conn = await self.get_connection()
        if not conn:
            return []

        try:
            rows = await conn.fetch(
                """
                SELECT job_id
                FROM user_job_interactions
                WHERE user_id = $1 AND rejected = TRUE
                ORDER BY rejected_at DESC
                """,
                user_id
            )

            return [row['job_id'] for row in rows]

        except Exception as e:
            print(f"❌ Error getting rejected jobs: {e}")
            return []
        finally:
            await conn.close()

    async def get_user_saved_jobs(self, user_id: int) -> List[str]:
        """Get list of job IDs user has saved"""
        conn = await self.get_connection()
        if not conn:
            return []

        try:
            rows = await conn.fetch(
                """
                SELECT job_id
                FROM user_job_interactions
                WHERE user_id = $1 AND saved = TRUE
                ORDER BY saved_at DESC
                """,
                user_id
            )

            return [row['job_id'] for row in rows]

        except Exception as e:
            print(f"❌ Error getting saved jobs: {e}")
            return []
        finally:
            await conn.close()

    async def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """Get user statistics"""
        conn = await self.get_connection()
        if not conn:
            return {}

        try:
            stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) FILTER (WHERE applied = TRUE) as applied_count,
                    COUNT(*) FILTER (WHERE rejected = TRUE) as rejected_count,
                    COUNT(*) FILTER (WHERE saved = TRUE) as saved_count,
                    COUNT(*) FILTER (WHERE hidden = TRUE) as hidden_count
                FROM user_job_interactions
                WHERE user_id = $1
                """,
                user_id
            )

            return dict(stats) if stats else {}

        except Exception as e:
            print(f"❌ Error getting user stats: {e}")
            return {}
        finally:
            await conn.close()


# Testing
if __name__ == "__main__":
    import asyncio

    async def test():
        db = UserDatabase()

        # Test user creation
        print("Testing user creation...")
        user = await db.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User"
        )
        print(f"Created user: {user}")

        # Test authentication
        print("\nTesting authentication...")
        auth_user = await db.authenticate_user("testuser", "TestPassword123")
        print(f"Authenticated: {auth_user}")

        # Test preferences
        if auth_user:
            print("\nTesting preferences...")
            prefs = await db.get_user_preferences(auth_user['id'])
            print(f"Preferences: {prefs}")

    # asyncio.run(test())
    print("User database module loaded. Run test() to test functionality.")
