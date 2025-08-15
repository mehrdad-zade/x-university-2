"""
Authentication tests for X University API.
Tests all authentication endpoints: register, login, refresh, logout, me.
"""
import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import User, UserRole


class TestAuthRegistration:
    """Test user registration functionality."""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration with token response."""
        register_data = {
            "email": "newuser@example.com",
            "password": "StrongSecret123!",
            "full_name": "New User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 201
        data = response.json()
        # Registration now returns tokens directly
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
        assert len(data["access_token"]) > 50
        assert len(data["refresh_token"]) > 50
    
    async def test_register_with_profile_verification(self, client: AsyncClient):
        """Test registration creates user with proper profile data."""
        register_data = {
            "email": "profiletest@example.com",
            "password": "SecurePass123!",
            "full_name": "Profile Test User",
            "role": "instructor"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        # Use the returned token to get profile
        tokens = response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        profile_response = await client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
        
        profile = profile_response.json()
        assert profile["email"] == "profiletest@example.com"
        assert profile["full_name"] == "Profile Test User"
        assert profile["role"] == "instructor"
        assert profile["is_active"] is True
        assert profile["email_verified"] is False
        assert profile["total_sessions"] == 1
    
    async def test_register_duplicate_email(self, client: AsyncClient, sample_user: User):
        """Test registration with duplicate email fails."""
        register_data = {
            "email": sample_user.email,
            "password": "StrongSecret123!",
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
            "password": "StrongSecret123!",
            "full_name": "Test User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 422  # Pydantic validation error
    
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password fails."""
        weak_passwords = [
            "123",  # Too short
            "simple",  # No numbers or special chars
            "Strong123",  # No special chars
            "STRONG123!",  # No lowercase
            "strong123!",  # No uppercase
        ]
        
        for weak_password in weak_passwords:
            register_data = {
                "email": f"test{len(weak_password)}@example.com",
                "password": weak_password,
                "full_name": "Test User",
                "role": "student"
            }
            
            response = await client.post("/api/v1/auth/register", json=register_data)
            assert response.status_code == 422, f"Weak password '{weak_password}' was accepted"
    
    async def test_register_password_strength_validation(self, client: AsyncClient):
        """Test that strong passwords are accepted."""
        strong_passwords = [
            "StrongSecret123!",
            "MySecure123@",
            "Complex1Key#",
            "Unbreakable456$"
        ]
        
        for i, strong_password in enumerate(strong_passwords):
            register_data = {
                "email": f"strong{i}@example.com",
                "password": strong_password,
                "full_name": f"Strong User {i}",
                "role": "student"
            }
            
            response = await client.post("/api/v1/auth/register", json=register_data)
            assert response.status_code == 201, f"Strong password '{strong_password}' was rejected"
    
    async def test_register_email_normalization(self, client: AsyncClient):
        """Test that email is normalized to lowercase."""
        register_data = {
            "email": "TEST@EXAMPLE.COM",
            "password": "StrongSecret123!",
            "full_name": "Test User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        # Verify email is normalized in profile
        tokens = response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        profile_response = await client.get("/api/v1/auth/me", headers=headers)
        profile = profile_response.json()
        assert profile["email"] == "test@example.com"
    
    async def test_register_role_validation(self, client: AsyncClient):
        """Test role validation in registration."""
        valid_roles = ["student", "instructor"]
        
        for role in valid_roles:
            register_data = {
                "email": f"{role}@example.com",
                "password": "StrongSecret123!",
                "full_name": f"Test {role.capitalize()}",
                "role": role
            }
            
            response = await client.post("/api/v1/auth/register", json=register_data)
            assert response.status_code == 201
        
        # Test invalid role
        register_data = {
            "email": "invalid@example.com",
            "password": "StrongSecret123!",
            "full_name": "Invalid Role",
            "role": "invalid_role"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 422


class TestAuthLogin:
    """Test user login functionality."""

    async def test_login_success(self, client: AsyncClient, sample_user: User):
        """Test successful user login."""
        login_data = {
            "email": sample_user.email,
            "password": "DevSecret123!"
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
            "password": "DevSecret123!"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    async def test_login_wrong_password(self, client: AsyncClient, sample_user: User):
        """Test login with incorrect password."""
        login_data = {
            "email": sample_user.email,
            "password": "wrongsecret"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    async def test_login_email_case_insensitive(self, client: AsyncClient, sample_user: User):
        """Test login with different email case."""
        login_data = {
            "email": sample_user.email.upper(),
            "password": "DevSecret123!"
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
            "password": "DevSecret123!"
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
            "password": "Integration123!",
            "full_name": "Integration Test",
            "role": "student"
        }
        
        register_response = await client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        # 2. Login
        login_data = {
            "email": "integration@example.com",
            "password": "Integration123!"
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
        assert sample_user.password_hash != "DevSecret123!"
        assert len(sample_user.password_hash) > 50  # bcrypt hashes are long
        assert sample_user.password_hash.startswith("$2b$")  # bcrypt prefix
    
    async def test_failed_login_attempts_tracking(self, client: AsyncClient, sample_user: User):
        """Test that failed login attempts are tracked."""
        login_data = {
            "email": sample_user.email,
            "password": "wrongpassword"
        }
        
        # Make several failed attempts
        for i in range(3):
            response = await client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == 401
        
        # Check that user still exists and can login with correct password
        correct_login_data = {
            "email": sample_user.email,
            "password": "DevSecret123!"
        }
        
        response = await client.post("/api/v1/auth/login", json=correct_login_data)
        assert response.status_code == 200
    
    async def test_account_locking_after_failed_attempts(self, client: AsyncClient, db_session: AsyncSession):
        """Test account locking after too many failed attempts."""
        # Create a test user
        register_data = {
            "email": "locktest@example.com",
            "password": "StrongSecret123!",
            "full_name": "Lock Test User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        # Make 5 failed login attempts
        login_data = {
            "email": "locktest@example.com",
            "password": "wrongsecret"
        }
        
        for i in range(5):
            response = await client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == 401
        
        # 6th attempt should show account is locked
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "locked" in response.json()["detail"].lower()
        
        # Even correct password should fail when locked
        correct_login_data = {
            "email": "locktest@example.com",
            "password": "StrongSecret123!"
        }
        
        response = await client.post("/api/v1/auth/login", json=correct_login_data)
        assert response.status_code == 401
        assert "locked" in response.json()["detail"].lower()
    
    async def test_security_fields_populated_on_registration(self, client: AsyncClient, db_session: AsyncSession):
        """Test that security fields are properly populated on user registration."""
        from sqlalchemy import select
        
        register_data = {
            "email": "securitytest@example.com",
            "password": "StrongSecret123!",
            "full_name": "Security Test User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        # Query the user directly from database to check security fields
        result = await db_session.execute(
            select(User).where(User.email == "securitytest@example.com")
        )
        user = result.scalar_one()
        
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.terms_accepted is True
        assert user.terms_accepted_at is not None
        assert user.privacy_policy_accepted is True
        assert user.profile_completed is True
        assert user.password_changed_at is not None
        assert user.email_verified is False
        assert user.is_active is True
    
    async def test_jwt_token_structure(self, client: AsyncClient, sample_user: User):
        """Test JWT token structure."""
        login_response = await client.post("/api/v1/auth/login", json={
            "email": sample_user.email,
            "password": "DevSecret123!"
        })
        
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # JWT tokens have three parts separated by dots
        access_parts = access_token.split(".")
        refresh_parts = refresh_token.split(".")
        
        assert len(access_parts) == 3
        assert len(refresh_parts) == 3
        
        # Each part should be base64 encoded
        for part in access_parts + refresh_parts:
            assert len(part) > 0
    
    async def test_session_tracking(self, client: AsyncClient, sample_user: User):
        """Test that user sessions are properly tracked."""
        # Login to create a session
        login_response = await client.post("/api/v1/auth/login", json={
            "email": sample_user.email,
            "password": "DevSecret123!"
        })
        
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Get user profile to check session count
        profile_response = await client.get("/api/v1/auth/me", headers=headers)
        profile = profile_response.json()
        
        # Should have at least 1 session from login
        assert profile["total_sessions"] >= 1
    
    async def test_password_requirements_enforcement(self, client: AsyncClient):
        """Test that password requirements are strictly enforced."""
        test_cases = [
            ("short", "Abc1!"),  # Too short
            ("no_uppercase", "abcd1234!"),  # No uppercase
            ("no_lowercase", "ABCD1234!"),  # No lowercase
            ("no_numbers", "Abcdefgh!"),  # No numbers
            ("no_special", "Abcd1234"),  # No special chars
            ("common_word", "MyAdmin123!"),  # Contains "admin"
            ("repeated_chars", "Aaaaa123!"),  # Too many repeated chars
        ]
        
        for test_name, weak_password in test_cases:
            register_data = {
                "email": f"{test_name}@example.com",
                "password": weak_password,
                "full_name": f"Test {test_name}",
                "role": "student"
            }
            
            response = await client.post("/api/v1/auth/register", json=register_data)
            assert response.status_code == 422, f"Weak password test '{test_name}' failed"
    
    async def test_email_verification_token_generation(self, client: AsyncClient, db_session: AsyncSession):
        """Test that email verification tokens can be generated."""
        from sqlalchemy import select
        
        # Register user
        register_data = {
            "email": "emailverify@example.com",
            "password": "StrongSecret123!",
            "full_name": "Email Verify User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        # Check user has email verification fields ready
        result = await db_session.execute(
            select(User).where(User.email == "emailverify@example.com")
        )
        user = result.scalar_one()
        
        assert user.email_verified is False
        # Email verification token should be None initially (to be set when verification is requested)
        assert user.email_verification_token is None
        assert user.email_verification_sent_at is None


class TestUserModel:
    """Test the User model and its methods."""
    
    async def test_user_creation_with_security_fields(self, db_session: AsyncSession):
        """Test user creation with all security fields properly initialized."""
        user_data = {
            "email": "model_test@example.com",
            "full_name": "Model Test User",
            "password_hash": "hashed_password",
            "role": UserRole.STUDENT,
            "is_active": True,
            "failed_login_attempts": 0,
            "terms_accepted": True,
            "terms_accepted_at": datetime.now(timezone.utc),
            "privacy_policy_accepted": True,
            "profile_completed": True,
            "password_changed_at": datetime.now(timezone.utc),
            "email_verified": False
        }
        
        user = User(**user_data)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "model_test@example.com"
        assert user.failed_login_attempts == 0
        assert user.is_locked is False
        assert user.should_force_password_change is False
    
    async def test_is_locked_method(self, sample_user: User):
        """Test the is_locked method under various conditions."""
        # User should not be locked initially
        assert sample_user.is_locked is False
        
        # Lock the user until future
        sample_user.locked_until = datetime.now(timezone.utc) + timedelta(hours=1)
        assert sample_user.is_locked is True
        
        # Lock expired
        sample_user.locked_until = datetime.now(timezone.utc) - timedelta(hours=1)
        assert sample_user.is_locked is False
    
    async def test_increment_failed_login_attempts(self, sample_user: User, db_session: AsyncSession):
        """Test incrementing failed login attempts."""
        initial_attempts = sample_user.failed_login_attempts
        
        sample_user.increment_failed_login_attempts()
        await db_session.commit()
        
        assert sample_user.failed_login_attempts == initial_attempts + 1
        
        # Test locking after 5 attempts
        sample_user.failed_login_attempts = 4
        sample_user.increment_failed_login_attempts()
        await db_session.commit()
        
        assert sample_user.failed_login_attempts == 5
        assert sample_user.is_locked is True
        assert sample_user.locked_until is not None
    
    async def test_reset_failed_attempts(self, sample_user: User, db_session: AsyncSession):
        """Test resetting failed login attempts."""
        sample_user.failed_login_attempts = 3
        sample_user.locked_until = datetime.now(timezone.utc) + timedelta(hours=1)
        
        sample_user.reset_failed_login_attempts()
        await db_session.commit()
        
        assert sample_user.failed_login_attempts == 0
        assert sample_user.locked_until is None
    
    async def test_should_force_password_change(self, sample_user: User):
        """Test password change requirement logic."""
        # New user should not need password change
        assert sample_user.should_force_password_change is False
        
        # User with old password should need change
        sample_user.password_changed_at = datetime.now(timezone.utc) - timedelta(days=100)
        assert sample_user.should_force_password_change is True
        
        # Recent password change
        sample_user.password_changed_at = datetime.now(timezone.utc) - timedelta(days=30)
        assert sample_user.should_force_password_change is False
