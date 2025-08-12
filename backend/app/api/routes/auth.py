"""
Authentication API routes for X University.
Handles user registration, login, logout, refresh, and user profile operations.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import (
    get_auth_service_with_client_info,
    get_current_user,
    get_current_user_id,
    get_auth_service,
    security
)
from app.core.security import AuthError
from app.models.auth import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    RefreshTokenRequest,
    LogoutRequest,
    TokenResponse,
    AccessTokenResponse,
    UserResponse,
    UserProfileResponse,
    AuthSuccessResponse,
    MessageResponse,
    AuthErrorResponse
)
from app.services.auth_service import AuthService


router = APIRouter()


@router.post(
    "/register",
    response_model=AuthSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account with email and password",
    responses={
        201: {
            "description": "User registered successfully",
            "model": AuthSuccessResponse
        },
        400: {
            "description": "Registration failed - invalid data or email already exists",
            "model": AuthErrorResponse
        }
    }
)
async def register(
    request: Request,
    user_data: UserRegisterRequest,
    auth_data: Annotated[tuple, Depends(get_auth_service_with_client_info)]
) -> AuthSuccessResponse:
    """
    Register a new user account.
    
    Creates a new user with the provided information and returns
    both the user data and authentication tokens.
    """
    auth_service, user_agent, ip_address = auth_data
    
    try:
        user_response, token_response = await auth_service.register_user(
            user_data=user_data,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        return AuthSuccessResponse(
            message="Registration successful",
            user=user_response
        )
        
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user with email and password, returns access and refresh tokens",
    responses={
        200: {
            "description": "Login successful",
            "model": TokenResponse
        },
        401: {
            "description": "Invalid credentials",
            "model": AuthErrorResponse
        }
    }
)
async def login(
    request: Request,
    login_data: UserLoginRequest,
    auth_data: Annotated[tuple, Depends(get_auth_service_with_client_info)]
) -> TokenResponse:
    """
    Authenticate user and return tokens.
    
    Validates user credentials and returns both access and refresh tokens
    for authenticated API access.
    """
    auth_service, user_agent, ip_address = auth_data
    
    try:
        user_response, token_response = await auth_service.login_user(
            login_data=login_data,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        return token_response
        
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token",
    responses={
        200: {
            "description": "Token refreshed successfully",
            "model": AccessTokenResponse
        },
        401: {
            "description": "Invalid or expired refresh token",
            "model": AuthErrorResponse
        }
    }
)
async def refresh(
    request: Request,
    token_data: RefreshTokenRequest,
    auth_data: Annotated[tuple, Depends(get_auth_service_with_client_info)]
) -> AccessTokenResponse:
    """
    Refresh access token.
    
    Uses a valid refresh token to generate a new access token.
    The refresh token must be valid and not expired.
    """
    auth_service, user_agent, ip_address = auth_data
    
    try:
        return await auth_service.refresh_access_token(
            refresh_token=token_data.refresh_token,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="User logout",
    description="Logout user by revoking session tokens",
    responses={
        200: {
            "description": "Logout successful",
            "model": MessageResponse
        },
        401: {
            "description": "Authentication required",
            "model": AuthErrorResponse
        }
    }
)
async def logout(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    logout_data: LogoutRequest = Body(default=LogoutRequest()),
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)] = None
) -> MessageResponse:
    """
    Logout user.
    
    Revokes the current session or all sessions based on the request.
    Requires valid authentication.
    """
    # Extract refresh token from request if available
    refresh_token = None
    if hasattr(logout_data, 'refresh_token'):
        refresh_token = logout_data.refresh_token
    
    try:
        await auth_service.logout_user(
            user_id=current_user_id,
            revoke_all_sessions=logout_data.revoke_all_sessions
        )
        
        message = "All sessions revoked" if logout_data.revoke_all_sessions else "Logged out successfully"
        return MessageResponse(message=message)
        
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Get detailed profile information for the authenticated user",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "model": UserProfileResponse
        },
        401: {
            "description": "Authentication required",
            "model": AuthErrorResponse
        },
        404: {
            "description": "User not found",
            "model": AuthErrorResponse
        }
    }
)
async def get_me(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> UserProfileResponse:
    """
    Get current user profile.
    
    Returns detailed profile information for the authenticated user,
    including session statistics.
    """
    profile = await auth_service.get_user_profile(current_user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return profile


@router.get(
    "/validate",
    response_model=UserResponse,
    summary="Validate access token",
    description="Validate the current access token and return user information",
    responses={
        200: {
            "description": "Token is valid",
            "model": UserResponse
        },
        401: {
            "description": "Invalid or expired token",
            "model": AuthErrorResponse
        }
    }
)
async def validate_token(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponse:
    """
    Validate access token.
    
    Validates the provided access token and returns basic user information.
    Useful for token verification without full profile data.
    """
    return UserResponse.model_validate(current_user)


# Health check endpoint for auth system
@router.get(
    "/health",
    response_model=MessageResponse,
    summary="Authentication health check",
    description="Check if authentication system is working properly",
    include_in_schema=False  # Hidden from API docs
)
async def auth_health() -> MessageResponse:
    """
    Authentication system health check.
    
    Simple endpoint to verify auth routes are working.
    """
    return MessageResponse(message="Authentication system is healthy")
