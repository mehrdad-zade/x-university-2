"""
X University Backend API

This module serves as the main entry point for the X University FastAPI application.
It provides a comprehensive learning management system with:
- JWT-based authentication and authorization
- User management with role-based access control
- Course management and progress tracking
- RESTful API endpoints with automatic documentation

The application uses:
- FastAPI for the web framework
- SQLAlchemy 2.0 for database ORM
- PostgreSQL for data persistence
- Structured logging for observability
- CORS middleware for frontend integration

Author: X University Development Team
Created: 2025
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.core.config import settings
from app.api.main import api_router
from app.models import auth  # Import models to register with SQLAlchemy

# Configure structured logging for production-ready observability
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan events manager.
    
    Handles startup and shutdown events for the FastAPI application.
    This is the recommended way to handle lifespan events in FastAPI.
    
    Args:
        app: The FastAPI application instance
        
    Yields:
        None: Control flow during application lifetime
    """
    # Startup events
    logger.info(
        "X University API starting up", 
        version="0.1.0",
        debug=settings.DEBUG,
        database_url=settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else "hidden"
    )
    
    yield  # Application is running
    
    # Shutdown events
    logger.info("X University API shutting down gracefully")

# Create the FastAPI application instance with comprehensive configuration
app = FastAPI(
    title="X University API",
    description="Backend API for X University learning platform with JWT authentication, course management, and learning analytics",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,  # Only show docs in development
    redoc_url="/redoc" if settings.DEBUG else None,  # Only show redoc in development
    lifespan=lifespan,
    contact={
        "name": "X University Development Team",
        "email": "dev@x-university.edu",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configure Cross-Origin Resource Sharing (CORS) for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Allow specific origins from settings
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # Specific HTTP methods
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],  # Specific headers
)

# Include all API routes with versioning prefix
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for application monitoring.
    
    This endpoint provides a simple way to verify that the API is running
    and can be used by load balancers, monitoring systems, and deployment
    pipelines to check application health.
    
    Returns:
        dict: Status information including health status
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "x-university-api",
        "version": "0.1.0"
    }
