"""
Pydantic schemas for authentication endpoints.
Request and response models for all auth operations.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from app.models.auth import UserRole


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.STUDENT


class SessionBase(BaseModel):
    """Base session schema."""
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


# Request schemas
class UserRegisterRequest(UserBase):
    """User registration request schema."""
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength with comprehensive requirements."""
        # Length check
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Character type checks
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(not c.isalnum() for c in v)
        
        if not has_upper:
            raise ValueError('Password must contain at least one uppercase letter')
        if not has_lower:
            raise ValueError('Password must contain at least one lowercase letter')
        if not has_digit:
            raise ValueError('Password must contain at least one number')
        if not has_special:
            raise ValueError('Password must contain at least one special character')
        
        # Check for common words (substring matches for common terms)
        password_lower = v.lower()
        common_substrings = ['password', 'admin', 'user', 'login', 'qwerty']
        for word in common_substrings:
            if word in password_lower:
                raise ValueError(f'Password cannot contain common word: {word}')
        
        # Check for exact matches to very common passwords
        common_passwords = ['123456789', '12345678', '1234567', '123456']
        if password_lower in common_passwords:
            raise ValueError('Password is too common')
        
        # Check for repeated characters (more than 3 consecutive)
        for i in range(len(v) - 3):
            if len(set(v[i:i+4])) == 1:
                raise ValueError('Password cannot contain more than 3 consecutive identical characters')
            
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        return v.lower().strip()


class UserLoginRequest(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=1)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        return v.lower().strip()


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., min_length=1)


class LogoutRequest(BaseModel):
    """Logout request schema (optional body)."""
    revoke_all_sessions: bool = False


# Response schemas
class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Access token expiration in seconds
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    )


class AccessTokenResponse(BaseModel):
    """Access token only response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserResponse):
    """Extended user profile response."""
    total_sessions: int = 0
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "student@example.com",
                "full_name": "John Doe",
                "role": "student",
                "is_active": True,
                "email_verified": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "last_login": "2024-01-01T12:00:00Z",
                "total_sessions": 1
            }
        }
    )


class SessionResponse(BaseModel):
    """Session response schema."""
    id: int
    user_agent: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    expires_at: datetime
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


# Success response schemas
class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operation completed successfully"
            }
        }
    )


class AuthSuccessResponse(MessageResponse):
    """Authentication success response."""
    user: UserResponse
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Registration successful",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "student@example.com",
                    "full_name": "John Doe",
                    "role": "student",
                    "is_active": True,
                    "email_verified": False,
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_login": None
                }
            }
        }
    )


# Error response schemas
class AuthErrorResponse(BaseModel):
    """Authentication error response."""
    detail: str
    error_code: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Invalid credentials",
                "error_code": "AUTH_INVALID_CREDENTIALS"
            }
        }
    )


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    detail: str
    errors: list[dict] = []
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Validation error",
                "errors": [
                    {
                        "field": "email",
                        "message": "Invalid email format"
                    }
                ]
            }
        }
    )
