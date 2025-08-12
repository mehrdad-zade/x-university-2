"""
Authentication tests for X University API.
Tests all authentication endpoints: register, login, refresh, logout, me.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import User, UserRole


class TestAuthRegistration:
    """Test user registration functionality."""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        register_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Registration successful"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["full_name"] == "New User"
        assert data["user"]["role"] == "student"
        assert data["user"]["is_active"] is True
        assert data["user"]["email_verified"] is False
        assert "id" in data["user"]
        assert "created_at" in data["user"]
    
    async def test_register_duplicate_email(self, client: AsyncClient, sample_user: User):
        """Test registration with duplicate email fails."""
        register_data = {
            "email": sample_user.email,
            "password": "password123",
            "full_name": "Another User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        register_data = {
            "email": "invalid-email",
            "password": "password123",
            "full_name": "Test User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 422  # Pydantic validation error
    
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password fails."""
        register_data = {
            "email": "test@example.com",
            "password": "123",  # Too short
            "full_name": "Test User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 422  # Pydantic validation error
    
    async def test_register_email_normalization(self, client: AsyncClient):
        """Test that email is normalized to lowercase."""
        register_data = {
            "email": "TEST@EXAMPLE.COM",
            "password": "password123",
            "full_name": "Test User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "test@example.com"


class TestAuthLogin:
    """Test user login functionality."""

    async def test_login_success(self, client: AsyncClient, sample_user: User):
        """Test successful user login."""
        login_data = {
            "email": sample_user.email,
            "password": "password123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800  # 30 minutes in seconds
        assert len(data["access_token"]) > 50  # JWT tokens are long
        assert len(data["refresh_token"]) > 50
    
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    async def test_login_wrong_password(self, client: AsyncClient, sample_user: User):
        """Test login with incorrect password."""
        login_data = {
            "email": sample_user.email,
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    async def test_login_email_case_insensitive(self, client: AsyncClient, sample_user: User):
        """Test login with different email case."""
        login_data = {
            "email": sample_user.email.upper(),
            "password": "password123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200


class TestAuthRefresh:
    """Test token refresh functionality."""

    async def test_refresh_success(self, client: AsyncClient, sample_user: User):
        """Test successful token refresh."""
        # First login to get refresh token
        login_response = await client.post("/api/v1/auth/login", json={
            "email": sample_user.email,
            "password": "password123"
        })
        
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]
        
        # Wait a moment to ensure different timestamp
        import asyncio
        await asyncio.sleep(1.1)
        
        # Now refresh the token
        refresh_response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        assert "access_token" in refresh_data
        assert refresh_data["token_type"] == "bearer"
        assert refresh_data["expires_in"] == 1800
        
        # New access token should be different
        assert refresh_data["access_token"] != login_data["access_token"]
    
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token."""
        refresh_response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid-token"
        })
        
        assert refresh_response.status_code == 401
    
    async def test_refresh_expired_token(self, client: AsyncClient):
        """Test refresh with expired token."""
        # This would require mocking time or using a very short expiry
        # For now, we'll test with a malformed token
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDk0NTkxOTksInN1YiI6InRlc3QifQ.invalid"
        
        refresh_response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": expired_token
        })
        
        assert refresh_response.status_code == 401


class TestAuthLogout:
    """Test user logout functionality."""

    async def test_logout_success(self, client: AsyncClient, auth_headers_student: dict):
        """Test successful logout."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers_student,
            json={"revoke_all_sessions": False}
        )
        
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()
    
    async def test_logout_all_sessions(self, client: AsyncClient, auth_headers_student: dict):
        """Test logout with revoke all sessions."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers_student,
            json={"revoke_all_sessions": True}
        )
        
        assert response.status_code == 200
        assert "all sessions" in response.json()["message"].lower()
    
    async def test_logout_without_auth(self, client: AsyncClient):
        """Test logout without authentication."""
        response = await client.post("/api/v1/auth/logout", json={})
        
        assert response.status_code == 401


class TestAuthMe:
    """Test user profile endpoint functionality."""

    async def test_get_me_success(self, client: AsyncClient, auth_headers_student: dict):
        """Test successful profile retrieval."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers_student)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "student@example.com"
        assert data["full_name"] == "Test Student"
        assert data["role"] == "student"
        assert "id" in data
        assert "created_at" in data
        assert "total_sessions" in data
    
    async def test_get_me_without_auth(self, client: AsyncClient):
        """Test profile retrieval without authentication."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test profile retrieval with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401


class TestAuthValidate:
    """Test token validation endpoint."""

    async def test_validate_token_success(self, client: AsyncClient, auth_headers_student: dict):
        """Test successful token validation."""
        response = await client.get("/api/v1/auth/validate", headers=auth_headers_student)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "student@example.com"
        assert data["role"] == "student"
    
    async def test_validate_token_invalid(self, client: AsyncClient):
        """Test validation with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await client.get("/api/v1/auth/validate", headers=headers)
        
        assert response.status_code == 401


class TestAuthIntegration:
    """Integration tests for complete auth flows."""

    async def test_complete_auth_flow(self, client: AsyncClient):
        """Test complete registration -> login -> access -> logout flow."""
        # 1. Register
        register_data = {
            "email": "integration@example.com",
            "password": "password123",
            "full_name": "Integration Test",
            "role": "student"
        }
        
        register_response = await client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        # 2. Login
        login_data = {
            "email": "integration@example.com",
            "password": "password123"
        }
        
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        tokens = login_response.json()
        
        # 3. Access protected endpoint
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        # 4. Refresh token
        refresh_response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        
        # 5. Use new access token
        new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        validate_response = await client.get("/api/v1/auth/validate", headers=new_headers)
        assert validate_response.status_code == 200
        
        # 6. Logout
        logout_response = await client.post("/api/v1/auth/logout", headers=new_headers)
        assert logout_response.status_code == 200


class TestAuthSecurity:
    """Test security aspects of authentication."""

    async def test_password_hashing(self, db_session: AsyncSession, sample_user: User):
        """Test that passwords are properly hashed."""
        assert sample_user.password_hash != "password123"
        assert len(sample_user.password_hash) > 50  # bcrypt hashes are long
        assert sample_user.password_hash.startswith("$2b$")  # bcrypt prefix
    
    async def test_jwt_token_structure(self, client: AsyncClient, sample_user: User):
        """Test JWT token structure."""
        login_response = await client.post("/api/v1/auth/login", json={
            "email": sample_user.email,
            "password": "password123"
        })
        
        tokens = login_response.json()
        access_token = tokens["access_token"]
        
        # JWT tokens have three parts separated by dots
        token_parts = access_token.split(".")
        assert len(token_parts) == 3
        
        # Each part should be base64 encoded
        for part in token_parts:
            assert len(part) > 0
