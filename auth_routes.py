#!/usr/bin/env python3
"""
Authentication API routes for LinkedIn Job Manager
Handles user registration, login, and profile management
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from auth_utils import (
    validate_password_strength,
    validate_email,
    validate_username,
    generate_token_response,
    get_current_user,
    get_current_admin_user
)
from user_database import UserDatabase

# Create router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Initialize user database
user_db = UserDatabase()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    username: str  # Can be username or email
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    full_name: Optional[str]
    is_admin: bool
    created_at: str
    last_login: Optional[str]

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register a new user

    - Creates new user account
    - Returns JWT token for immediate login
    - Creates default user preferences
    """
    # Validate username
    valid, error = validate_username(request.username)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    # Validate email
    valid, error = validate_email(request.email)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    # Validate password strength
    valid, error = validate_password_strength(request.password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    # Create user
    user = await user_db.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        is_admin=False
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    # Generate token response
    user_data = {
        "user_id": user['id'],
        "username": user['username'],
        "email": user['email'],
        "full_name": user.get('full_name'),
        "is_admin": user['is_admin']
    }

    return generate_token_response(user_data)


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login with username/email and password

    - Accepts either username or email
    - Returns JWT token on successful authentication
    - Updates last login timestamp
    """
    # Authenticate user
    user = await user_db.authenticate_user(request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate token response
    user_data = {
        "user_id": user['id'],
        "username": user['username'],
        "email": user['email'],
        "full_name": user.get('full_name'),
        "is_admin": user['is_admin']
    }

    return generate_token_response(user_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user's information

    - Requires valid JWT token
    - Returns user profile data
    """
    # Get full user details from database
    user = await user_db.get_user_by_id(current_user['user_id'])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "user_id": user['id'],
        "username": user['username'],
        "email": user['email'],
        "full_name": user.get('full_name'),
        "is_admin": user['is_admin'],
        "created_at": user['created_at'].isoformat() if user.get('created_at') else None,
        "last_login": user['last_login'].isoformat() if user.get('last_login') else None
    }


@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user profile information

    - Can update full_name and email
    - Requires valid JWT token
    """
    # TODO: Implement profile update in user_database.py
    # For now, return success message
    return {
        "success": True,
        "message": "Profile update endpoint - implementation pending"
    }


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Change user password

    - Requires old password verification
    - Validates new password strength
    """
    # Validate new password strength
    valid, error = validate_password_strength(request.new_password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    # Change password
    success = await user_db.change_password(
        user_id=current_user['user_id'],
        old_password=request.old_password,
        new_password=request.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password or password change failed"
        )

    return {
        "success": True,
        "message": "Password changed successfully"
    }


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout current user

    - Frontend should discard the JWT token
    - Server-side logout is stateless (JWT based)
    """
    return {
        "success": True,
        "message": "Logged out successfully. Please discard your token."
    }


# ============================================================================
# USER PREFERENCES ENDPOINTS
# ============================================================================

@router.get("/preferences")
async def get_preferences(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user's job preferences

    - Returns all preference settings
    - Used to filter jobs on dashboard
    """
    prefs = await user_db.get_user_preferences(current_user['user_id'])

    if not prefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )

    return prefs


class UpdatePreferencesRequest(BaseModel):
    job_types: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    excluded_keywords: Optional[List[str]] = None
    experience_levels: Optional[List[str]] = None
    exclude_senior: Optional[bool] = None
    preferred_countries: Optional[List[str]] = None
    preferred_cities: Optional[List[str]] = None
    exclude_locations: Optional[List[str]] = None
    excluded_companies: Optional[List[str]] = None
    preferred_companies: Optional[List[str]] = None
    easy_apply_only: Optional[bool] = None
    remote_only: Optional[bool] = None
    email_notifications: Optional[bool] = None
    daily_digest: Optional[bool] = None


@router.put("/preferences")
async def update_preferences(
    request: UpdatePreferencesRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user's job preferences

    - Updates only provided fields
    - Other fields remain unchanged
    """
    # Convert request to dict, excluding None values
    preferences = {k: v for k, v in request.dict().items() if v is not None}

    if not preferences:
        return {
            "success": True,
            "message": "No preferences to update"
        }

    success = await user_db.update_user_preferences(
        user_id=current_user['user_id'],
        preferences=preferences
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )

    return {
        "success": True,
        "message": "Preferences updated successfully"
    }


@router.get("/stats")
async def get_user_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get user statistics

    - Number of applied jobs
    - Number of rejected jobs
    - Number of saved jobs
    """
    stats = await user_db.get_user_stats(current_user['user_id'])

    return {
        "user_id": current_user['user_id'],
        "applied_jobs": stats.get('applied_count', 0),
        "rejected_jobs": stats.get('rejected_count', 0),
        "saved_jobs": stats.get('saved_count', 0),
        "hidden_jobs": stats.get('hidden_count', 0)
    }


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.get("/admin/users")
async def list_all_users(admin: Dict[str, Any] = Depends(get_current_admin_user)):
    """
    List all users (admin only)

    - Only accessible to admin users
    - Returns list of all users
    """
    # TODO: Implement list_all_users in user_database.py
    return {
        "message": "Admin user list endpoint - implementation pending"
    }


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: Dict[str, Any] = Depends(get_current_admin_user)
):
    """
    Delete a user (admin only)

    - Only accessible to admin users
    - Soft delete (sets is_active = FALSE)
    """
    # TODO: Implement delete_user in user_database.py
    return {
        "message": f"Delete user {user_id} endpoint - implementation pending"
    }


# Export router
__all__ = ['router']
