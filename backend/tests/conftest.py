"""
Test configuration and fixtures for X University API tests.
"""
import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.config import settings
from app.db.base import Base, get_db_session
from app.models.auth import User, UserRole
from app.core.security import hash_password


# Test database URL - use separate test database
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/xu2", "/xu2_test")

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL.replace("postgresql+psycopg://", "postgresql+asyncpg://"),
    poolclass=NullPool,  # Disable connection pooling for tests
    echo=False
)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestAsyncSessionLocal() as session:
        yield session
    
    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with test database session."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"}
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        full_name="Test User",
        role=UserRole.STUDENT,
        is_active=True,
        email_verified=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user for testing."""
    user = User(
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        email_verified=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def instructor_user(db_session: AsyncSession) -> User:
    """Create an instructor user for testing."""
    user = User(
        email="instructor@example.com",
        password_hash=hash_password("instructor123"),
        full_name="Instructor User",
        role=UserRole.INSTRUCTOR,
        is_active=True,
        email_verified=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def auth_headers_student(client: AsyncClient) -> dict[str, str]:
    """Get authentication headers for a student user."""
    # Register and login a student user
    register_data = {
        "email": "student@example.com",
        "password": "password123",
        "full_name": "Test Student",
        "role": "student"
    }
    
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    assert register_response.status_code == 201
    
    login_data = {
        "email": "student@example.com",
        "password": "password123"
    }
    
    login_response = await client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token_data = login_response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest_asyncio.fixture
async def auth_headers_admin(client: AsyncClient) -> dict[str, str]:
    """Get authentication headers for an admin user."""
    # Register and login an admin user
    register_data = {
        "email": "testadmin@example.com",
        "password": "admin123",
        "full_name": "Test Admin",
        "role": "admin"
    }
    
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    assert register_response.status_code == 201
    
    login_data = {
        "email": "testadmin@example.com",
        "password": "admin123"
    }
    
    login_response = await client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token_data = login_response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}
