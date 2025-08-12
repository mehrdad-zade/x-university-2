"""
Database base configuration.
SQLAlchemy 2.0 async setup with PostgreSQL.
"""
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, DateTime, func
from datetime import datetime
from typing import Any, AsyncGenerator

from app.core.config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Import all models here to ensure they're registered with Base.metadata
# This is required for Alembic autogenerate to work properly
# Import moved to avoid circular imports - will be imported during app startup
