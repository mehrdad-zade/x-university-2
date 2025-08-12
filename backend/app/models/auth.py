"""
Database models for authentication.
User and Session models with proper relationships.
"""
from datetime import datetime, timezone
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
    
    Based on existing database schema:
    - users(id integer pk, email unique not null, password_hash, role, full_name, created_at, updated_at)
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
    last_login: Mapped[Optional[datetime]] = mapped_column(
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
