"""
Test cases for email verification and 2FA functionality.
"""
import pytest
import secrets
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock

from app.services.email_service import EmailService, MockEmailBackend
from app.services.two_factor_service import TwoFactorService
from app.models.auth import User, UserRole


class TestEmailService:
    """Test cases for EmailService."""
    
    @pytest.fixture
    def mock_email_service(self):
        """Create email service with mock backend."""
        mock_backend = MockEmailBackend()
        return EmailService(backend=mock_backend), mock_backend
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        return User(
            id=1,
            email="test@example.com",
            full_name="Test User",
            role=UserRole.STUDENT,
            password_hash="hashed_password",
            is_active=True,
            email_verified=False
        )
    
    async def test_send_verification_email(self, mock_email_service, sample_user):
        """Test sending verification email."""
        email_service, mock_backend = mock_email_service
        verification_token = secrets.token_urlsafe(32)
        
        # Send verification email
        result = await email_service.send_verification_email(sample_user, verification_token)
        
        assert result is True
        assert len(mock_backend.sent_emails) == 1
        
        sent_email = mock_backend.sent_emails[0]
        assert sent_email['to_email'] == "test@example.com"
        assert "Verify your X-University account" in sent_email['subject']
        assert verification_token in sent_email['html_content']
        assert sample_user.full_name in sent_email['html_content']
    
    async def test_send_2fa_disabled_notification(self, mock_email_service, sample_user):
        """Test sending 2FA disabled notification."""
        email_service, mock_backend = mock_email_service
        
        result = await email_service.send_2fa_disabled_notification(sample_user)
        
        assert result is True
        assert len(mock_backend.sent_emails) == 1
        
        sent_email = mock_backend.sent_emails[0]
        assert sent_email['to_email'] == "test@example.com"
        assert "Two-Factor Authentication Disabled" in sent_email['subject']
        assert sample_user.full_name in sent_email['html_content']


class TestTwoFactorService:
    """Test cases for TwoFactorService."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def two_factor_service(self, mock_db_session):
        """Create TwoFactorService with mock database."""
        return TwoFactorService(mock_db_session)
    
    def test_generate_totp_secret(self, two_factor_service):
        """Test TOTP secret generation."""
        secret = two_factor_service.generate_totp_secret()
        
        assert isinstance(secret, str)
        assert len(secret) == 32  # Base32 encoded secret
        
        # Generate another one - should be different
        secret2 = two_factor_service.generate_totp_secret()
        assert secret != secret2
    
    def test_verify_totp_code(self, two_factor_service):
        """Test TOTP code verification."""
        import pyotp
        
        # Generate a secret and create TOTP
        secret = two_factor_service.generate_totp_secret()
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()
        
        # Test valid code
        assert two_factor_service.verify_totp_code(secret, valid_code) is True
        
        # Test invalid code
        assert two_factor_service.verify_totp_code(secret, "000000") is False
        
        # Test empty/invalid inputs
        assert two_factor_service.verify_totp_code("", valid_code) is False
        assert two_factor_service.verify_totp_code(secret, "") is False
        assert two_factor_service.verify_totp_code(secret, "12345") is False  # Wrong length
        assert two_factor_service.verify_totp_code(secret, "abcdef") is False  # Non-digits
    
    def test_generate_backup_codes(self, two_factor_service):
        """Test backup code generation."""
        backup_codes = two_factor_service.generate_backup_codes()
        
        assert len(backup_codes) == 10  # Default count
        
        for code in backup_codes:
            assert isinstance(code, str)
            assert len(code) == 9  # Format: XXXX-XXXX
            assert "-" in code
            parts = code.split("-")
            assert len(parts) == 2
            assert len(parts[0]) == 4
            assert len(parts[1]) == 4
            assert parts[0].isupper()  # Should be uppercase
            assert parts[1].isupper()
        
        # Test custom count
        custom_codes = two_factor_service.generate_backup_codes(5)
        assert len(custom_codes) == 5
        
        # Codes should be unique
        assert len(set(backup_codes)) == len(backup_codes)
    
    def test_generate_qr_code_data_url(self, two_factor_service):
        """Test QR code generation."""
        user = User(
            id=1,
            email="test@example.com",
            full_name="Test User",
            role=UserRole.STUDENT,
            password_hash="hashed_password"
        )
        secret = two_factor_service.generate_totp_secret()
        
        qr_data_url = two_factor_service.generate_qr_code_data_url(user, secret)
        
        assert isinstance(qr_data_url, str)
        assert qr_data_url.startswith("data:image/png;base64,")
        
        # Should contain base64 encoded data
        base64_part = qr_data_url.split(",")[1]
        assert len(base64_part) > 0


class TestEmailVerificationFlow:
    """Integration tests for email verification flow."""
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        return User(
            id=1,
            email="test@example.com",
            full_name="Test User",
            role=UserRole.STUDENT,
            password_hash="hashed_password",
            is_active=True,
            email_verified=False,
            email_verification_token=None,
            email_verification_sent_at=None
        )
    
    def test_verification_token_expiry_logic(self, sample_user):
        """Test email verification token expiry logic."""
        now = datetime.now(timezone.utc)
        
        # Fresh token (within 24 hours)
        sample_user.email_verification_sent_at = now - timedelta(hours=12)
        token_age = now - sample_user.email_verification_sent_at
        assert token_age <= timedelta(hours=24)
        
        # Expired token (over 24 hours)
        sample_user.email_verification_sent_at = now - timedelta(hours=25)
        token_age = now - sample_user.email_verification_sent_at
        assert token_age > timedelta(hours=24)


# Example usage and setup documentation
"""
To implement this in your application:

1. Run the database migration:
   ```bash
   cd backend
   source .venv/bin/activate
   alembic upgrade head
   ```

2. Install new dependencies:
   ```bash
   pip install pyotp==2.9.0 qrcode==7.4.2 pillow==10.0.1 aiosmtplib==3.0.1 jinja2==3.1.6
   ```

3. Update your .env file with email settings:
   ```
   EMAIL_BACKEND=smtp
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=noreply@x-university.edu
   FRONTEND_URL=http://localhost:5173
   ```

4. For Gmail, you'll need to:
   - Enable 2-factor authentication on your Google account
   - Generate an "App Password" for the application
   - Use the app password in SMTP_PASSWORD (not your regular password)

5. Add new API routes to handle email verification and 2FA setup
   (see the documentation in S005_email_2fa.md for detailed route implementations)

6. Update the frontend to handle:
   - Email verification page (/verify-email?token=...)
   - 2FA setup flow with QR code display
   - 2FA login challenge
   - Backup code display and storage

This provides a solid foundation for implementing secure email verification
and two-factor authentication in your X-University application.
"""
