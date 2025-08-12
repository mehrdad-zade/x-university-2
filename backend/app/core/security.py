"""
Security utilities for X University API

This module provides comprehensive security functionality including:
- JWT token generation, validation, and management
- Password hashing and verification using bcrypt
- Custom authentication error handling
- Session ID generation for user session tracking

The security implementation follows industry best practices:
- Uses bcrypt for password hashing with proper salting
- JWT tokens with configurable expiration times
- Separate access and refresh token mechanisms
- Cryptographically secure random session ID generation

Security considerations:
- All passwords are hashed using bcrypt before storage
- JWT tokens include user ID and role information
- Access tokens have short expiration times (30 minutes default)
- Refresh tokens have longer expiration times (7 days default)
- Session IDs are generated using cryptographically secure random bytes

Author: X University Development Team
Created: 2025
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

import bcrypt
import jwt
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import settings


class AuthError(HTTPException):
    """
    Custom authentication error exception.
    
    This exception is raised when authentication or authorization fails,
    providing consistent error responses across the API.
    
    Inherits from FastAPI's HTTPException to integrate seamlessly with
    the framework's error handling system.
    """
    
    def __init__(self, detail: str = "Authentication failed", status_code: int = status.HTTP_401_UNAUTHORIZED):
        """
        Initialize authentication error.
        
        Args:
            detail: Human-readable error description
            status_code: HTTP status code (default: 401 Unauthorized)
        """
        super().__init__(status_code=status_code, detail=detail)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        subject: The subject (usually user ID) for the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MINUTES)
    
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(subject),
        "type": "access"
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(subject: Union[str, Any], jti: Optional[str] = None) -> str:
    """
    Create JWT refresh token.
    
    Args:
        subject: The subject (usually user ID) for the token
        jti: Optional JWT ID. If not provided, a random one is generated
        
    Returns:
        Encoded JWT token string
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)
    
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(subject),
        "type": "refresh",
        "jti": jti or secrets.token_urlsafe(32)  # Use provided JTI or generate one
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate JWT token.
    
    Args:
        token: The JWT token string
        
    Returns:
        Token payload dictionary
        
    Raises:
        AuthError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.PyJWTError:
        raise AuthError("Invalid token")


def verify_token_type(payload: dict[str, Any], expected_type: str) -> None:
    """
    Verify token type matches expected type.
    
    Args:
        payload: Token payload
        expected_type: Expected token type ("access" or "refresh")
        
    Raises:
        AuthError: If token type doesn't match
    """
    token_type = payload.get("type")
    if token_type != expected_type:
        raise AuthError(f"Invalid token type. Expected {expected_type}, got {token_type}")


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        password: Plain text password
        hashed_password: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def generate_session_id() -> str:
    """Generate secure random session ID."""
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    """
    Hash refresh token for secure storage.
    
    Args:
        token: Refresh token string
        
    Returns:
        Hashed token for database storage
    """
    return hash_password(token)


def verify_refresh_token(token: str, hashed_token: str) -> bool:
    """
    Verify refresh token against hash.
    
    Args:
        token: Plain refresh token
        hashed_token: Stored token hash
        
    Returns:
        True if token matches, False otherwise
    """
    return verify_password(token, hashed_token)
