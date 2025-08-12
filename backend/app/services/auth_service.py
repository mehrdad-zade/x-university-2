"""
Authentication service for X University API.
Handles user registration, login, token management, and session handling.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple

import bcrypt
import jwt
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
    hash_refresh_token,
    verify_refresh_token,
    AuthError
)
from app.core.config import settings
from app.models.auth import User, Session, UserRole
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    AccessTokenResponse,
    UserResponse,
    UserProfileResponse
)


class AuthService:
    """Authentication service handling all auth operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def register_user(
        self,
        user_data: UserRegisterRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[UserResponse, TokenResponse]:
        """
        Register a new user and create initial session.
        
        Args:
            user_data: User registration data
            user_agent: User's browser/client info
            ip_address: User's IP address
            
        Returns:
            Tuple of user response and token response
            
        Raises:
            AuthError: If email already exists or registration fails
        """
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise AuthError("Email already registered")
            
            # Hash password
            password_hash = hash_password(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email,
                password_hash=password_hash,
                full_name=user_data.full_name,
                role=user_data.role
            )
            
            self.db.add(user)
            await self.db.flush()  # Get user ID
            await self.db.refresh(user)
            
            # Create initial session
            session, refresh_token = await self.create_session(
                user_id=user.id,
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            # Commit all changes first
            await self.db.commit()
            
            # Refresh objects to ensure they're up to date
            await self.db.refresh(user)
            await self.db.refresh(session)
            
            # Create tokens
            access_token = create_access_token(str(user.id))
            # Use refresh token from session creation
            
            # Create response objects after commit and refresh
            user_response = UserResponse.model_validate(user)
            token_response = TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRES_MINUTES * 60
            )
            
            return user_response, token_response
            
        except IntegrityError:
            await self.db.rollback()
            raise AuthError("Email already registered")
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, AuthError):
                raise
            raise AuthError("Registration failed")
    
    async def login_user(
        self,
        login_data: UserLoginRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[UserResponse, TokenResponse]:
        """
        Authenticate user and create new session.
        
        Args:
            login_data: User login credentials
            user_agent: User's browser/client info
            ip_address: User's IP address
            
        Returns:
            Tuple of user response and token response
            
        Raises:
            AuthError: If credentials are invalid or user is inactive
        """
        try:
            # Get user by email
            user = await self.get_user_by_email(login_data.email)
            if not user:
                raise AuthError("Invalid credentials")
            
            # Verify password
            if not verify_password(login_data.password, user.password_hash):
                raise AuthError("Invalid credentials")
            
            # Check if user is active
            if not user.is_active:
                raise AuthError("Account is deactivated")
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            
            # Create new session
            session, refresh_token = await self.create_session(
                user_id=user.id,
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            # Commit all changes first
            await self.db.commit()
            
            # Refresh objects to ensure they're up to date
            await self.db.refresh(user)
            await self.db.refresh(session)
            
            # Create tokens
            access_token = create_access_token(str(user.id))
            # Use refresh token from session creation
            
            # Create response objects after commit and refresh
            user_response = UserResponse.model_validate(user)
            token_response = TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRES_MINUTES * 60
            )
            
            return user_response, token_response
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, AuthError):
                raise
            raise AuthError("Login failed")
    
    async def refresh_access_token(
        self,
        refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AccessTokenResponse:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            user_agent: User's browser/client info  
            ip_address: User's IP address
            
        Returns:
            New access token response
            
        Raises:
            AuthError: If refresh token is invalid or expired
        """
        try:
            # Decode and verify refresh token
            payload = decode_token(refresh_token)
            verify_token_type(payload, "refresh")
            
            user_id = int(payload["sub"])
            jti = payload.get("jti")  # Token ID
            
            # Find active session with matching refresh token
            session_query = select(Session).where(
                Session.user_id == user_id,
                Session.id == int(jti) if jti else None,
                Session.is_active == True
            )
            
            session = await self.db.scalar(session_query)
            if not session or session.is_expired:
                raise AuthError("Invalid refresh token")
            
            # Verify refresh token hash
            if not verify_refresh_token(refresh_token, session.refresh_token_hash):
                raise AuthError("Invalid refresh token")
            
            # Verify user still exists and is active
            user = await self.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise AuthError("User not found or inactive")
            
            # Update session metadata if provided
            if user_agent is not None:
                session.user_agent = user_agent
            if ip_address is not None:
                session.ip_address = ip_address
            
            await self.db.commit()
            
            # Create new access token
            access_token = create_access_token(str(user_id))
            
            return AccessTokenResponse(
                access_token=access_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRES_MINUTES * 60
            )
            
        except Exception as e:
            if isinstance(e, AuthError):
                raise
            raise AuthError("Token refresh failed")
    
    async def create_session(
        self,
        user_id: int,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> tuple[Session, str]:
        """
        Create a new user session.
        
        Args:
            user_id: User's ID
            user_agent: User's browser/client info
            ip_address: User's IP address
            
        Returns:
            Tuple of (created session object, refresh token)
        """
        # Create session with temporary refresh token
        session = Session(
            user_id=user_id,
            refresh_token_hash="temp",  # Will be updated below
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)
        )
        
        self.db.add(session)
        await self.db.flush()  # Get session ID
        
        # Generate refresh token with session ID as JTI
        refresh_token = create_refresh_token(str(user_id), jti=str(session.id))
        session.refresh_token_hash = hash_refresh_token(refresh_token)
        
        return session, refresh_token
    
    async def logout_user(
        self,
        user_id: int,
        revoke_all_sessions: bool = False
    ) -> bool:
        """
        Logout user by revoking sessions.
        
        Args:
            user_id: User's ID
            revoke_all_sessions: Whether to revoke all user sessions
            
        Returns:
            True if logout successful
        """
        try:
            if revoke_all_sessions:
                # Revoke all user sessions
                update_query = (
                    select(Session)
                    .where(Session.user_id == user_id, Session.is_active == True)
                )
                sessions = await self.db.scalars(update_query)
                
                for session in sessions:
                    session.is_active = False
                    session.revoked_at = datetime.now(timezone.utc)
            else:
                # For single session logout, we'd need the session ID
                # This is a simplified version that revokes all sessions
                # In practice, you'd pass the specific session ID
                await self.logout_user(user_id, revoke_all_sessions=True)
            
            await self.db.commit()
            return True
            
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        query = select(User).where(User.email == email.lower())
        return await self.db.scalar(query)
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        query = select(User).where(User.id == user_id)
        return await self.db.scalar(query)
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfileResponse]:
        """
        Get user profile with additional metadata.
        
        Args:
            user_id: User's ID
            
        Returns:
            User profile response with session count
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Count active sessions
        session_count_query = select(func.count()).select_from(Session).where(
            Session.user_id == user_id,
            Session.is_active == True,
            Session.expires_at > datetime.now(timezone.utc)
        )
        
        total_sessions = await self.db.scalar(session_count_query) or 0
        
        # Create profile response
        profile = UserProfileResponse.model_validate(user)
        profile.total_sessions = total_sessions
        
        return profile
    
    async def verify_access_token(self, token: str) -> int:
        """
        Verify access token and return user ID.
        
        Args:
            token: JWT access token
            
        Returns:
            User ID if token is valid
            
        Raises:
            AuthError: If token is invalid or user is inactive
        """
        try:
            # Decode and verify token
            payload = decode_token(token)
            verify_token_type(payload, "access")
            
            user_id = int(payload["sub"])
            
            # Verify user still exists and is active
            user = await self.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise AuthError("User not found or inactive")
            
            return user_id
            
        except Exception as e:
            if isinstance(e, AuthError):
                raise
            raise AuthError("Invalid access token")
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            # Delete expired sessions
            delete_query = delete(Session).where(
                Session.expires_at <= datetime.now(timezone.utc)
            )
            
            result = await self.db.execute(delete_query)
            await self.db.commit()
            
            return result.rowcount
            
        except Exception:
            await self.db.rollback()
            return 0
    
    async def revoke_session(
        self,
        user_id: int,
        session_id: int
    ) -> bool:
        """
        Revoke a specific user session.
        
        Args:
            user_id: User's ID
            session_id: Session ID to revoke
            
        Returns:
            True if session was revoked
        """
        try:
            session_query = select(Session).where(
                Session.id == session_id,
                Session.user_id == user_id,
                Session.is_active == True
            )
            
            session = await self.db.scalar(session_query)
            if session:
                session.is_active = False
                session.revoked_at = datetime.now(timezone.utc)
                await self.db.commit()
                return True
            
            return False
            
        except Exception:
            await self.db.rollback()
            return False
