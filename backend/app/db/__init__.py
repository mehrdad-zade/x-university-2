"""
Database Configuration and Models Package

This package manages all database-related functionality for the X University backend,
including connection management, model definitions, and database operations.

Components:
- base.py: Core database configuration, engine setup, and session management

Features:
- Asynchronous database operations using SQLAlchemy 2.0 and asyncpg
- PostgreSQL connection with optimized connection pooling
- Base model class with automatic timestamp tracking
- Database session dependency injection for FastAPI
- Proper transaction management and cleanup
- Migration support through Alembic integration

The database architecture uses:
- SQLAlchemy 2.0 with async/await support
- PostgreSQL as the primary database
- Connection pooling for scalability
- Automatic created_at/updated_at timestamps
- Integer primary keys for compatibility

All models inherit from the Base class to ensure consistent behavior
and automatic audit trail capabilities.

Version: 0.1.0
"""
