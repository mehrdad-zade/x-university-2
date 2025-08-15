"""
Database models for authentication.
Enhanced User and Session models with proper security practices and relationships.
"""
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, Enum):
    """User role enumeration."""
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(Base):
    """
    User model for authentication and profile management.
    
    Enhanced with security best practices:
    - Email verification tracking
    - Account locking for security
    - Failed login attempt tracking
    - Profile completion status
    - Terms acceptance tracking
    """
    __tablename__ = "users"
    
    # Primary key - integer to match existing database
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )
    
    # Core user fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        String(20),
        default=UserRole.STUDENT,
        nullable=False
    )
    
    # User status and metadata
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    email_verification_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )
    email_verification_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Security fields
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    password_reset_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )
    password_reset_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Profile and preferences
    profile_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    terms_accepted: Mapped[bool] = mapped_column(
        Boolean,
        default=True,  # Assumed accepted on registration
        nullable=False
    )
    terms_accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    privacy_policy_accepted: Mapped[bool] = mapped_column(
        Boolean,
        default=True,  # Assumed accepted on registration
        nullable=False
    )
    
    # Activity tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_password_change: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def is_locked(self) -> bool:
        """Check if account is currently locked due to failed login attempts."""
        if self.locked_until:
            return datetime.now(timezone.utc) < self.locked_until
        return False
    
    @property
    def should_force_password_change(self) -> bool:
        """Check if user should be forced to change password (e.g., after 90 days)."""
        # Check password_changed_at first (for new users), then last_password_change
        reference_date = self.password_changed_at or self.last_password_change
        if not reference_date:
            return False
        
        # Force password change after 90 days
        password_max_age = timedelta(days=90)
        return datetime.now(timezone.utc) - reference_date > password_max_age
    
    def increment_failed_login_attempts(self) -> None:
        """Increment failed login attempts and lock account if threshold reached."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    def reset_failed_login_attempts(self) -> None:
        """Reset failed login attempts after successful login."""
        self.failed_login_attempts = 0
        self.locked_until = None


class Session(Base):
    """
    Session model for refresh token management.
    
    Based on existing database schema:
    - sessions(id integer pk, user_id fk, refresh_token_hash, user_agent, ip, expires_at, created_at)
    """
    __tablename__ = "sessions"
    
    # Primary key - integer to match existing database
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )
    
    # Foreign key to user - integer to match existing database
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Session data
    refresh_token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True  # For efficient lookups
    )
    
    # Session metadata
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True  # For cleanup queries
    )
    
    # Security tracking
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    user: Mapped[User] = relationship(
        "User",
        back_populates="sessions"
    )
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if session is valid (active and not expired)."""
        return self.is_active and not self.is_expired and not self.revoked_at
