"""
Dependency injection for FastAPI routes.
Authentication and authorization dependencies.
"""
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db_session
from app.services.auth_service import AuthService
from app.models.auth import User, UserRole
from app.core.security import AuthError


# Security scheme for JWT bearer tokens
security = HTTPBearer(
    scheme_name="JWT",
    description="JWT Bearer token authentication",
    auto_error=False
)


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db_session)]
) -> AuthService:
    """Dependency to get authentication service."""
    return AuthService(db)


async def get_current_user_id(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> int:
    """
    Dependency to get current user ID from JWT token.
    
    Args:
        credentials: JWT bearer token credentials
        auth_service: Authentication service instance
        
    Returns:
        Current user ID
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = await auth_service.verify_access_token(credentials.credentials)
        return user_id
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    user_id: Annotated[int, Depends(get_current_user_id)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> User:
    """
    Dependency to get current user object.
    
    Args:
        user_id: Current user ID from token
        auth_service: Authentication service instance
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If user not found
    """
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


async def get_optional_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Optional[User]:
    """
    Optional dependency to get current user (doesn't raise if no auth).
    
    Args:
        credentials: JWT bearer token credentials (optional)
        auth_service: Authentication service instance
        
    Returns:
        Current user object or None if not authenticated
    """
    if not credentials:
        return None
    
    try:
        user_id = await auth_service.verify_access_token(credentials.credentials)
        return await auth_service.get_user_by_id(user_id)
    except AuthError:
        return None


class RequireRole:
    """Dependency class to require specific user roles."""
    
    def __init__(self, *allowed_roles: UserRole):
        self.allowed_roles = allowed_roles
    
    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        """
        Check if current user has required role.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Current user if role is allowed
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in self.allowed_roles]}"
            )
        return current_user


# Common role dependencies
require_admin = RequireRole(UserRole.ADMIN)
require_instructor = RequireRole(UserRole.INSTRUCTOR, UserRole.ADMIN)
require_student = RequireRole(UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ADMIN)


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """
    Extract client information from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Tuple of (user_agent, ip_address)
    """
    user_agent = request.headers.get("user-agent")
    
    # Try to get real IP from various headers (handle proxies)
    ip_address = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip() or
        request.headers.get("x-real-ip") or
        request.headers.get("x-client-ip") or
        request.client.host if request.client else None
    )
    
    return user_agent, ip_address


async def get_auth_service_with_client_info(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)]
) -> tuple[AuthService, str, str]:
    """
    Dependency to get auth service with client information.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Tuple of (auth_service, user_agent, ip_address)
    """
    auth_service = AuthService(db)
    user_agent, ip_address = get_client_info(request)
    return auth_service, user_agent or "", ip_address or ""
