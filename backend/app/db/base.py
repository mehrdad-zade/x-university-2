"""
Database Base Configuration for X University API

This module provides the foundation for database operations using SQLAlchemy 2.0
with asynchronous support for PostgreSQL.

Key Components:
- Async SQLAlchemy engine and session factory
- Base model class with common fields (id, timestamps)
- Database session dependency for FastAPI
- Connection pool configuration for production scalability

Features:
- PostgreSQL with asyncpg driver for high performance
- Automatic timestamp tracking (created_at, updated_at)
- Connection pool management
- Transaction support with proper cleanup
- Debug logging in development mode

Database Architecture:
- All models inherit from Base class
- Primary keys are integers for compatibility
- Timezone-aware timestamps using UTC
- Automatic model registration for migrations

Usage:
- Use get_db_session() as a FastAPI dependency
- All models should inherit from Base
- Async/await pattern required for all database operations

Author: X University Development Team
Created: 2025
"""

from datetime import datetime
from typing import Any, AsyncGenerator

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import settings


# Create asynchronous database engine with optimized settings
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    echo_pool=settings.DEBUG,  # Log connection pool events in debug mode
    future=True,  # Use SQLAlchemy 2.0 style
    
    # Connection Pool Optimization
    pool_size=20,  # Base connection pool size (increased from 5)
    max_overflow=40,  # Additional connections beyond pool_size (increased from 10)
    pool_timeout=30,  # Timeout waiting for connection (seconds)
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Validate connections before use (prevents broken connections)
    
    # Connection Settings
    connect_args={
        "server_settings": {
            # PostgreSQL session optimization
            "application_name": "xu2_backend",
            "timezone": "UTC",
            # Performance settings (only session-level settings allowed here)
            "track_io_timing": "on",
            "track_functions": "pl",
            "log_statement": "all",  # Log all statements for this session
            "log_min_duration_statement": "1000",  # Log queries taking > 1 second
        },
        # AsyncPG-specific optimizations
        "command_timeout": 60,  # Query timeout (60 seconds)
        "statement_cache_size": 1024,  # Prepared statement cache
        "max_cached_statement_lifetime": 300,  # Cache lifetime (5 minutes)
        "max_cacheable_statement_size": 15360,  # Max statement size to cache (15KB)
    },
)

# Create async session factory for database operations
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects alive after commit
    autoflush=True,  # Automatically flush changes
    autocommit=False  # Explicit transaction control
)


class Base(DeclarativeBase):
    """
    Base class for all database models.
    
    Provides common fields and functionality that all models inherit:
    - id: Primary key (integer for compatibility with existing data)
    - created_at: Automatic timestamp when record is created
    - updated_at: Automatic timestamp when record is modified
    
    All models should inherit from this class to ensure consistency
    and provide audit trail capabilities.
    """
    
    # Primary key - using Integer for compatibility with existing database
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Primary key identifier"
    )
    
    # Audit timestamps - automatically managed by database
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Set by database on insert
        nullable=False,
        comment="Timestamp when record was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Set by database on insert
        onupdate=func.now(),  # Updated by database on update
        nullable=False,
        comment="Timestamp when record was last updated"
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to provide database sessions.
    
    This function creates a new database session for each request
    and ensures proper cleanup after the request completes.
    
    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db_session)):
            # Use db session here
            pass
    
    Yields:
        AsyncSession: Database session for the request
        
    Note:
        The session is automatically closed after the request,
        even if an exception occurs.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            # Rollback transaction on error
            await session.rollback()
            raise
        finally:
            # Ensure session is properly closed
            await session.close()


# Model Registration
# All models are imported in app/main.py to ensure they're registered
# with Base.metadata for Alembic migrations. This avoids circular imports
# while ensuring proper model discovery.
