"""
User management API routes for X University.
Admin-only routes for user management operations.
"""
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin, get_auth_service
from app.db.base import get_db_session
from app.models.auth import User, UserRole
from app.schemas.auth import UserResponse, UserProfileResponse
from app.services.auth_service import AuthService


router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get basic information about the authenticated user",
    responses={
        200: {"description": "User information retrieved successfully"},
        401: {"description": "Authentication required"}
    }
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponse:
    """
    Get current user information.
    
    Returns basic user information for the authenticated user.
    """
    return UserResponse.model_validate(current_user)


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get user profile",
    description="Get detailed profile information (alias for /auth/me)",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Authentication required"}
    }
)
async def get_user_profile(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponse:
    """
    Get user profile.
    
    Alias endpoint for user profile information.
    """
    return UserResponse.model_validate(current_user)


# Admin-only endpoints
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID (Admin only)",
    description="Get user information by ID - requires admin privileges",
    dependencies=[Depends(require_admin)],
    responses={
        200: {"description": "User found"},
        403: {"description": "Admin access required"},
        404: {"description": "User not found"}
    }
)
async def get_user_by_id(
    user_id: int,
    current_user: Annotated[User, Depends(require_admin)]
) -> UserResponse:
    """
    Get user by ID.
    
    Admin-only endpoint to retrieve any user's information by their ID.
    """
    # This is a placeholder - in a full implementation, you'd query the database
    # For now, we'll just return a 404 since we don't have user lookup service here
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List all users (Admin only)",
    description="Get a list of all users - requires admin privileges",
    dependencies=[Depends(require_admin)],
    responses={
        200: {"description": "Users retrieved successfully"},
        403: {"description": "Admin access required"}
    }
)
async def list_users(
    current_user: Annotated[User, Depends(require_admin)]
) -> list[UserResponse]:
    """
    List all users.
    
    Admin-only endpoint to retrieve all users in the system.
    """
    # Placeholder - would implement user listing in full service
    return []
