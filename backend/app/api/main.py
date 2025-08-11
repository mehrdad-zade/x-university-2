"""
API router configuration.
Combines all API endpoints under /api/v1 prefix.
"""
from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/")
async def api_root() -> dict[str, str]:
    """API root endpoint."""
    return {"message": "X University API v1"}

# TODO: Add route imports when implemented
# from app.api.routes import auth, courses, users, payments
# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
