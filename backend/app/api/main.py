"""
API router configuration.
Combines all API endpoints under /api/v1 prefix.
"""
from fastapi import APIRouter

from app.api.routes import auth, users, monitor

api_router = APIRouter()

@api_router.get("/")
async def api_root() -> dict[str, str]:
    """API root endpoint."""
    return {"message": "X University API v1"}

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
