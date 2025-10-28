#!/usr/bin/env python3
"""
Authentication utilities for LinkedIn Job Manager
Handles password hashing, JWT token generation/validation, and user authentication
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import re

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7  # Token valid for 7 days

# Security scheme for FastAPI
security = HTTPBearer()


# ============================================================================
# PASSWORD UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Previously hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets minimum requirements

    Requirements:
    - At least 8 characters
    - Contains at least one letter
    - Contains at least one number

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    return True, ""


# ============================================================================
# JWT TOKEN UTILITIES
# ============================================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in token (typically user_id and username)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token data if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================================================
# FASTAPI DEPENDENCIES
# ============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user from JWT token

    Usage:
        @app.get("/api/protected")
        async def protected_route(current_user = Depends(get_current_user)):
            return {"user_id": current_user["user_id"]}

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        Decoded token data containing user info

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = decode_access_token(token)

        if payload is None:
            raise credentials_exception

        user_id: int = payload.get("user_id")
        username: str = payload.get("username")

        if user_id is None or username is None:
            raise credentials_exception

        return {
            "user_id": user_id,
            "username": username,
            "is_admin": payload.get("is_admin", False)
        }

    except JWTError:
        raise credentials_exception


async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    FastAPI dependency to ensure current user is an admin

    Usage:
        @app.delete("/api/admin/users/{user_id}")
        async def delete_user(user_id: int, admin = Depends(get_current_admin_user)):
            # Only admins can access this route
            pass

    Args:
        current_user: Current authenticated user from get_current_user

    Returns:
        Current user data if they are an admin

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return current_user


# ============================================================================
# EMAIL VALIDATION
# ============================================================================

def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_regex, email):
        return False, "Invalid email format"

    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format

    Requirements:
    - 3-50 characters
    - Only letters, numbers, underscores, hyphens
    - Must start with a letter

    Args:
        username: Username to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 50:
        return False, "Username must be at most 50 characters long"

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        return False, "Username must start with a letter and contain only letters, numbers, underscores, and hyphens"

    return True, ""


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_token_response(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a complete token response for login/registration

    Args:
        user_data: User data dict with user_id, username, is_admin

    Returns:
        Dict containing access_token, token_type, and user info
    """
    access_token = create_access_token(
        data={
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "is_admin": user_data.get("is_admin", False)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "email": user_data.get("email"),
            "full_name": user_data.get("full_name"),
            "is_admin": user_data.get("is_admin", False)
        }
    }


# ============================================================================
# TESTING UTILITIES
# ============================================================================

if __name__ == "__main__":
    # Test password hashing
    print("Testing password hashing...")
    password = "TestPassword123"
    hashed = hash_password(password)
    print(f"Hashed: {hashed}")
    print(f"Verification: {verify_password(password, hashed)}")

    # Test password validation
    print("\nTesting password validation...")
    valid, msg = validate_password_strength("short")
    print(f"'short': {valid} - {msg}")
    valid, msg = validate_password_strength("ValidPassword123")
    print(f"'ValidPassword123': {valid} - {msg}")

    # Test JWT tokens
    print("\nTesting JWT tokens...")
    token = create_access_token({"user_id": 1, "username": "testuser"})
    print(f"Token: {token[:50]}...")
    decoded = decode_access_token(token)
    print(f"Decoded: {decoded}")

    # Test email validation
    print("\nTesting email validation...")
    valid, msg = validate_email("test@example.com")
    print(f"'test@example.com': {valid}")
    valid, msg = validate_email("invalid-email")
    print(f"'invalid-email': {valid} - {msg}")

    print("\n✅ All auth utilities working!")
