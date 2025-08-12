"""
X University Backend Application

This package contains the complete backend API for the X University learning platform.
Built with FastAPI, SQLAlchemy, and PostgreSQL for a modern, scalable architecture.

Package Structure:
- api/: FastAPI routes and API endpoints
- core/: Core configuration, security, and shared utilities  
- db/: Database models, migrations, and connection management
- models/: SQLAlchemy database models
- schemas/: Pydantic request/response schemas
- services/: Business logic and service layer
- workers/: Background task processing (future implementation)

Key Features:
- JWT-based authentication and authorization
- Role-based access control (Admin, Instructor, Student)
- RESTful API design with OpenAPI documentation
- Async database operations with PostgreSQL
- Comprehensive error handling and validation
- Structured logging for observability
- Type hints throughout for development safety

The application follows clean architecture principles with clear separation
of concerns between API, business logic, and data persistence layers.

Author: X University Development Team
Created: 2025
Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "X University Development Team"
