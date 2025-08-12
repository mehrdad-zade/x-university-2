"""
Main API Router for X University Backend

This module defines the main API router that aggregates all route modules
and provides the central entry point for API endpoints.

The router includes:
- Authentication and user management routes
- System monitoring and health check routes  
- Versioned API structure (/api/v1)
- Automatic OpenAPI documentation generation

Route Organization:
- /auth/* - Authentication and user management
- /users/* - User profile and management
- /monitor - System monitoring endpoints
- Additional routes will be added as features are implemented

All routes are properly documented with OpenAPI schemas and include
appropriate authentication and authorization middleware.

Author: X University Development Team
Created: 2025
"""

from fastapi import APIRouter

# Import route modules
from app.api.routes import auth, users, monitor

# Create the main API router with v1 prefix
api_router = APIRouter(
    prefix="",  # No additional prefix here since it's added in main.py
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"}, 
        404: {"description": "Not Found"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"}
    }
)

@api_router.get("/")
async def api_root() -> dict[str, str]:
    """
    API root endpoint providing basic information.
    
    Returns basic API information and status. This endpoint
    can be used to verify API availability and version.
    
    Returns:
        dict: API information including version and status
    """
    return {
        "message": "X University API v1",
        "version": "0.1.0",
        "status": "active",
        "documentation": "/docs"
    }

# Include route modules
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Authentication failed"},
        403: {"description": "Access forbidden"}
    }
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"}
    }
)

# Public monitoring endpoints (no authentication required)
api_router.include_router(
    monitor.router,
    tags=["Monitoring"],
    responses={
        500: {"description": "Internal server error"}
    }
)

# TODO: Add additional route imports when implemented
# from app.api.routes import courses, payments, ai
# api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
# api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
# api_router.include_router(ai.router, prefix="/ai", tags=["AI Content Generation"])
