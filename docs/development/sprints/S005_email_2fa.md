# Sprint 5 — Email Verification & 2FA

## Goals
Implement email verification for new registrations and 2-factor authentication (TOTP) for enhanced security.

## Phase 1: Email Verification

### Database Changes (Already exist)
- `users.email_verified` (boolean) - verification status
- `users.email_verification_token` (string) - verification token
- `users.email_verification_sent_at` (datetime) - when token was sent

### New Database Tables
```sql
-- TOTP secrets for 2FA
CREATE TABLE user_totp_secrets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    secret_key VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    backup_codes TEXT[], -- Array of backup codes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    activated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id)
);

-- 2FA recovery codes
CREATE TABLE user_recovery_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    code_hash VARCHAR(255) NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### API Endpoints

#### Email Verification
- POST `/auth/send-verification` - Send/resend verification email
- POST `/auth/verify-email` {token} - Verify email with token
- GET `/auth/verification-status` - Check verification status

#### 2FA Management  
- POST `/auth/2fa/setup` - Initialize TOTP setup (returns QR code)
- POST `/auth/2fa/verify-setup` {totp_code} - Complete TOTP setup
- POST `/auth/2fa/disable` {password, totp_code} - Disable 2FA
- GET `/auth/2fa/backup-codes` - Generate backup codes
- POST `/auth/2fa/use-backup` {backup_code} - Use backup code for login

#### Enhanced Login
- POST `/auth/login` - Modified to handle 2FA
- POST `/auth/login/2fa` {totp_code|backup_code} - Complete 2FA login

## Implementation Details

### 1. Email Service Setup

#### Dependencies
```bash
# Add to requirements.txt
sendgrid==6.10.0  # or
boto3==1.34.0     # for AWS SES
aiosmtplib==3.0.1 # for SMTP
jinja2==3.1.6     # for email templates
```

#### Email Configuration
```python
# app/core/config.py additions
EMAIL_BACKEND: str = "sendgrid"  # "sendgrid", "ses", "smtp"
SENDGRID_API_KEY: str = ""
SMTP_HOST: str = "smtp.gmail.com"
SMTP_PORT: int = 587
SMTP_USERNAME: str = ""
SMTP_PASSWORD: str = ""
FROM_EMAIL: str = "noreply@x-university.edu"
FRONTEND_URL: str = "http://localhost:5173"
```

#### Email Templates
```html
<!-- templates/email/verify_email.html -->
<h2>Verify Your Email Address</h2>
<p>Hi {{full_name}},</p>
<p>Please click the link below to verify your email address:</p>
<a href="{{verification_url}}">Verify Email</a>
<p>This link expires in 24 hours.</p>
```

### 2. Enhanced User Model

```python
# Add to user model
class User(Base):
    # ... existing fields ...
    
    # 2FA fields
    totp_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    backup_codes_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
```

### 3. Email Service

```python
# app/services/email_service.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader

class EmailBackend(ABC):
    @abstractmethod
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        pass

class SMTPEmailBackend(EmailBackend):
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        # SMTP implementation
        pass

class EmailService:
    def __init__(self, backend: EmailBackend):
        self.backend = backend
        self.template_env = Environment(loader=FileSystemLoader("templates/email"))
    
    async def send_verification_email(self, user: User, verification_token: str) -> bool:
        template = self.template_env.get_template("verify_email.html")
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        html_content = template.render(
            full_name=user.full_name,
            verification_url=verification_url
        )
        
        return await self.backend.send_email(
            to_email=user.email,
            subject="Verify your X-University account",
            html_content=html_content
        )
```

### 4. 2FA Service (TOTP)

```python
# app/services/two_factor_service.py
import pyotp
import qrcode
import io
import base64
from typing import Tuple, List
import secrets
from sqlalchemy.ext.asyncio import AsyncSession

class TwoFactorService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret."""
        return pyotp.random_base32()
    
    def generate_qr_code(self, user: User, secret: str) -> str:
        """Generate QR code for TOTP setup."""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="X-University"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{qr_base64}"
    
    def verify_totp_code(self, secret: str, code: str) -> bool:
        """Verify TOTP code."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Allow 1 window of tolerance
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for 2FA recovery."""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    async def setup_2fa(self, user_id: int) -> Tuple[str, str]:
        """
        Initialize 2FA setup for user.
        Returns: (secret, qr_code_base64)
        """
        user = await self.db.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        
        secret = self.generate_totp_secret()
        qr_code = self.generate_qr_code(user, secret)
        
        # Store secret temporarily (not activated until verified)
        user.totp_secret = secret
        await self.db.commit()
        
        return secret, qr_code
    
    async def activate_2fa(self, user_id: int, totp_code: str) -> List[str]:
        """
        Activate 2FA after verifying setup code.
        Returns: backup_codes
        """
        user = await self.db.get(User, user_id)
        if not user or not user.totp_secret:
            raise ValueError("2FA setup not initialized")
        
        if not self.verify_totp_code(user.totp_secret, totp_code):
            raise ValueError("Invalid TOTP code")
        
        # Activate 2FA
        user.two_factor_enabled = True
        user.backup_codes_generated_at = datetime.now(timezone.utc)
        
        # Generate backup codes
        backup_codes = self.generate_backup_codes()
        
        # Store hashed backup codes
        for code in backup_codes:
            recovery_code = UserRecoveryCode(
                user_id=user_id,
                code_hash=hash_password(code)
            )
            self.db.add(recovery_code)
        
        await self.db.commit()
        return backup_codes
```

### 5. Enhanced Auth Service

```python
# Modifications to app/services/auth_service.py

class AuthService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.email_service = EmailService(SMTPEmailBackend())
        self.two_factor_service = TwoFactorService(db_session)
    
    async def register_user(self, user_data: UserRegisterRequest, **kwargs) -> Tuple[UserResponse, TokenResponse]:
        """Modified to send verification email."""
        user_response, token_response = await self._original_register_user(user_data, **kwargs)
        
        # Send verification email
        verification_token = secrets.token_urlsafe(32)
        user = await self.get_user_by_email(user_data.email)
        user.email_verification_token = verification_token
        user.email_verification_sent_at = datetime.now(timezone.utc)
        user.email_verified = False  # Require verification
        
        await self.db.commit()
        await self.email_service.send_verification_email(user, verification_token)
        
        return user_response, token_response
    
    async def verify_email(self, token: str) -> bool:
        """Verify email with token."""
        user_query = select(User).where(User.email_verification_token == token)
        user = await self.db.scalar(user_query)
        
        if not user:
            return False
        
        # Check token expiry (24 hours)
        if user.email_verification_sent_at:
            token_age = datetime.now(timezone.utc) - user.email_verification_sent_at
            if token_age > timedelta(hours=24):
                return False
        
        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_sent_at = None
        
        await self.db.commit()
        return True
    
    async def login_user_with_2fa(self, login_data: UserLoginRequest, **kwargs) -> Dict[str, Any]:
        """Modified login to handle 2FA."""
        user = await self.get_user_by_email(login_data.email)
        if not user:
            raise AuthError("Invalid credentials")
        
        # Verify password first
        if not verify_password(login_data.password, user.password_hash):
            user.increment_failed_login_attempts()
            await self.db.commit()
            raise AuthError("Invalid credentials")
        
        # Check if 2FA is enabled
        if user.two_factor_enabled:
            # Create temporary session for 2FA
            temp_token = create_access_token(str(user.id), expires_minutes=10)
            return {
                "requires_2fa": True,
                "temp_token": temp_token,
                "backup_codes_available": await self._has_backup_codes(user.id)
            }
        
        # Regular login flow
        user_response, token_response = await self._complete_login(user, **kwargs)
        return {
            "requires_2fa": False,
            "user": user_response,
            "tokens": token_response
        }
    
    async def complete_2fa_login(self, temp_token: str, totp_code: str = None, backup_code: str = None, **kwargs) -> Tuple[UserResponse, TokenResponse]:
        """Complete login after 2FA verification."""
        # Verify temp token
        payload = decode_token(temp_token)
        user_id = int(payload["sub"])
        user = await self.get_user_by_id(user_id)
        
        if not user:
            raise AuthError("Invalid session")
        
        verified = False
        
        if totp_code:
            verified = self.two_factor_service.verify_totp_code(user.totp_secret, totp_code)
        elif backup_code:
            verified = await self._verify_backup_code(user_id, backup_code)
        
        if not verified:
            raise AuthError("Invalid 2FA code")
        
        return await self._complete_login(user, **kwargs)
```

### 6. Frontend Integration

#### Registration Flow
```typescript
// src/services/auth.ts
export const registerUser = async (userData: RegisterData) => {
  const response = await api.post('/auth/register', userData);
  // Show message: "Please check your email to verify your account"
  return response.data;
};

export const verifyEmail = async (token: string) => {
  const response = await api.post('/auth/verify-email', { token });
  return response.data;
};
```

#### 2FA Setup
```tsx
// src/components/TwoFactorSetup.tsx
import { QRCodeSVG } from 'qrcode.react';

const TwoFactorSetup = () => {
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  
  const initializeSetup = async () => {
    const response = await api.post('/auth/2fa/setup');
    setQrCode(response.data.qr_code);
    setSecret(response.data.secret);
  };
  
  const completeSetup = async () => {
    const response = await api.post('/auth/2fa/verify-setup', {
      totp_code: verificationCode
    });
    setBackupCodes(response.data.backup_codes);
  };
  
  return (
    <div>
      <h3>Setup Two-Factor Authentication</h3>
      {qrCode && (
        <div>
          <p>Scan this QR code with your authenticator app:</p>
          <img src={qrCode} alt="2FA QR Code" />
          <p>Or enter this secret manually: <code>{secret}</code></p>
        </div>
      )}
      
      <input
        type="text"
        value={verificationCode}
        onChange={(e) => setVerificationCode(e.target.value)}
        placeholder="Enter verification code"
      />
      <button onClick={completeSetup}>Complete Setup</button>
      
      {backupCodes.length > 0 && (
        <div>
          <h4>Backup Codes</h4>
          <p>Save these codes safely. Each can only be used once:</p>
          <ul>
            {backupCodes.map((code, i) => <li key={i}>{code}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
};
```

### 7. Testing Strategy

#### Email Verification Tests
```python
# tests/test_email_verification.py
async def test_email_verification_flow():
    # Register user
    user_data = {"email": "test@example.com", "password": "StrongSecret123!", "full_name": "Test User"}
    response = await client.post("/auth/register", json=user_data)
    
    # User should not be verified initially
    assert response.json()["user"]["email_verified"] is False
    
    # Get verification token from database
    user = await get_user_by_email("test@example.com")
    token = user.email_verification_token
    
    # Verify email
    verify_response = await client.post("/auth/verify-email", json={"token": token})
    assert verify_response.status_code == 200
    
    # User should now be verified
    user = await get_user_by_email("test@example.com")
    assert user.email_verified is True
```

#### 2FA Tests
```python
# tests/test_two_factor.py
async def test_2fa_setup_flow():
    # Login user
    login_response = await client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Initialize 2FA setup
    setup_response = await client.post("/auth/2fa/setup", headers={"Authorization": f"Bearer {token}"})
    secret = setup_response.json()["secret"]
    
    # Generate TOTP code
    totp = pyotp.TOTP(secret)
    code = totp.now()
    
    # Complete setup
    activate_response = await client.post("/auth/2fa/verify-setup", 
                                        json={"totp_code": code},
                                        headers={"Authorization": f"Bearer {token}"})
    
    assert activate_response.status_code == 200
    assert "backup_codes" in activate_response.json()
```

## Migration Plan

1. **Add new database tables** via Alembic migration
2. **Update User model** with 2FA fields
3. **Implement email service** with configurable backends
4. **Add 2FA service** with TOTP support
5. **Modify auth endpoints** to support new flows
6. **Update frontend** with new components
7. **Add comprehensive tests**

## Security Considerations

- Email verification tokens expire in 24 hours
- TOTP codes have 30-second windows with 1-window tolerance
- Backup codes are single-use and hashed
- Rate limiting on verification attempts
- Secure secret storage (consider encryption at rest)
- Audit logging for 2FA events

## Dependencies to Add

```bash
# Backend
pip install pyotp==2.9.0 qrcode==7.4.2 pillow==10.0.1 sendgrid==6.10.0

# Frontend  
npm install qrcode.react @types/qrcode.react
```
