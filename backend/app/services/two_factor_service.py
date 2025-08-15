"""
Two-factor authentication service using TOTP (Time-based One-Time Password).
Handles TOTP secret generation, QR codes, backup codes, and verification.
"""
import io
import base64
import secrets
import logging
from typing import List, Tuple, Optional
from datetime import datetime, timezone

import pyotp
import qrcode
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.auth import User

logger = logging.getLogger(__name__)


class UserRecoveryCode:
    """Temporary model for recovery codes - will be added to models/auth.py later."""
    def __init__(self, user_id: int, code_hash: str):
        self.user_id = user_id
        self.code_hash = code_hash
        self.used_at = None
        self.created_at = datetime.now(timezone.utc)


class TwoFactorService:
    """Service for managing two-factor authentication."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret (base32 encoded)."""
        return pyotp.random_base32()
    
    def generate_qr_code_data_url(self, user: User, secret: str) -> str:
        """
        Generate QR code as base64 data URL for TOTP setup.
        
        Args:
            user: User object
            secret: TOTP secret
            
        Returns:
            Base64 data URL for QR code image
        """
        try:
            # Create provisioning URI
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user.email,
                issuer_name="X-University"
            )
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 data URL
            buffer = io.BytesIO()
            qr_image.save(buffer, format='PNG')
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{qr_base64}"
            
        except Exception as e:
            logger.error(f"Failed to generate QR code for user {user.id}: {str(e)}")
            raise ValueError("Failed to generate QR code")
    
    def verify_totp_code(self, secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Verify TOTP code against secret.
        
        Args:
            secret: TOTP secret
            code: 6-digit TOTP code
            valid_window: Number of time windows to check (allows for clock drift)
            
        Returns:
            True if code is valid
        """
        try:
            if not secret or not code:
                return False
            
            # Remove any spaces or formatting from code
            code = code.replace(' ', '').replace('-', '')
            
            # Verify code length
            if len(code) != 6 or not code.isdigit():
                return False
            
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=valid_window)
            
        except Exception as e:
            logger.error(f"TOTP verification error: {str(e)}")
            return False
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Generate backup codes for 2FA recovery.
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            List of backup codes (formatted as XXXX-XXXX)
        """
        backup_codes = []
        for _ in range(count):
            # Generate 8-character hex code and format as XXXX-XXXX
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            backup_codes.append(formatted_code)
        
        return backup_codes
    
    async def initialize_2fa_setup(self, user_id: int) -> Tuple[str, str]:
        """
        Initialize 2FA setup for a user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Tuple of (secret, qr_code_data_url)
            
        Raises:
            ValueError: If user not found
        """
        try:
            # Get user
            user_query = select(User).where(User.id == user_id)
            user = await self.db.scalar(user_query)
            
            if not user:
                raise ValueError("User not found")
            
            if user.two_factor_enabled:
                raise ValueError("2FA is already enabled for this user")
            
            # Generate new secret
            secret = self.generate_totp_secret()
            
            # Store secret temporarily (not activated until verified)
            user.totp_secret = secret
            
            # Generate QR code
            qr_code_data_url = self.generate_qr_code_data_url(user, secret)
            
            # Commit the secret
            await self.db.commit()
            
            logger.info(f"2FA setup initialized for user {user_id}")
            return secret, qr_code_data_url
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to initialize 2FA setup for user {user_id}: {str(e)}")
            raise
    
    async def complete_2fa_setup(self, user_id: int, totp_code: str) -> List[str]:
        """
        Complete 2FA setup by verifying the setup code and generating backup codes.
        
        Args:
            user_id: User's ID
            totp_code: 6-digit TOTP code from authenticator app
            
        Returns:
            List of backup codes
            
        Raises:
            ValueError: If verification fails
        """
        try:
            # Get user
            user_query = select(User).where(User.id == user_id)
            user = await self.db.scalar(user_query)
            
            if not user:
                raise ValueError("User not found")
            
            if not user.totp_secret:
                raise ValueError("2FA setup not initialized. Please start setup first.")
            
            if user.two_factor_enabled:
                raise ValueError("2FA is already enabled for this user")
            
            # Verify TOTP code
            if not self.verify_totp_code(user.totp_secret, totp_code):
                raise ValueError("Invalid TOTP code. Please check your authenticator app.")
            
            # Enable 2FA
            user.two_factor_enabled = True
            user.backup_codes_generated_at = datetime.now(timezone.utc)
            
            # Generate and store backup codes
            backup_codes = self.generate_backup_codes()
            
            # TODO: Store backup codes in database when UserRecoveryCode model is added
            # For now, just return them - they should be stored by the calling code
            
            await self.db.commit()
            
            logger.info(f"2FA setup completed for user {user_id}")
            return backup_codes
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to complete 2FA setup for user {user_id}: {str(e)}")
            raise
    
    async def disable_2fa(self, user_id: int, current_password: str, totp_code: str = None) -> bool:
        """
        Disable 2FA for a user.
        
        Args:
            user_id: User's ID
            current_password: User's current password for verification
            totp_code: Current TOTP code (optional if using backup code)
            
        Returns:
            True if 2FA was disabled successfully
            
        Raises:
            ValueError: If verification fails
        """
        try:
            # Get user
            user_query = select(User).where(User.id == user_id)
            user = await self.db.scalar(user_query)
            
            if not user:
                raise ValueError("User not found")
            
            if not user.two_factor_enabled:
                raise ValueError("2FA is not enabled for this user")
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                raise ValueError("Invalid password")
            
            # Verify TOTP code if provided
            if totp_code and not self.verify_totp_code(user.totp_secret, totp_code):
                raise ValueError("Invalid TOTP code")
            
            # Disable 2FA
            user.two_factor_enabled = False
            user.totp_secret = None
            user.backup_codes_generated_at = None
            
            # TODO: Delete backup codes from database when model is added
            
            await self.db.commit()
            
            logger.info(f"2FA disabled for user {user_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to disable 2FA for user {user_id}: {str(e)}")
            raise
    
    async def verify_backup_code(self, user_id: int, backup_code: str) -> bool:
        """
        Verify and mark a backup code as used.
        
        Args:
            user_id: User's ID
            backup_code: Backup code to verify
            
        Returns:
            True if backup code is valid and unused
        """
        try:
            # TODO: Implement backup code verification when UserRecoveryCode model is added
            # For now, return False as backup codes aren't stored yet
            logger.warning(f"Backup code verification not implemented yet for user {user_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to verify backup code for user {user_id}: {str(e)}")
            return False
    
    async def regenerate_backup_codes(self, user_id: int, current_password: str) -> List[str]:
        """
        Regenerate backup codes for a user.
        
        Args:
            user_id: User's ID
            current_password: User's current password for verification
            
        Returns:
            New list of backup codes
            
        Raises:
            ValueError: If verification fails
        """
        try:
            # Get user
            user_query = select(User).where(User.id == user_id)
            user = await self.db.scalar(user_query)
            
            if not user:
                raise ValueError("User not found")
            
            if not user.two_factor_enabled:
                raise ValueError("2FA is not enabled for this user")
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                raise ValueError("Invalid password")
            
            # TODO: Delete existing backup codes and create new ones when model is added
            
            # Generate new backup codes
            backup_codes = self.generate_backup_codes()
            user.backup_codes_generated_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            
            logger.info(f"Backup codes regenerated for user {user_id}")
            return backup_codes
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to regenerate backup codes for user {user_id}: {str(e)}")
            raise


# Convenience function for dependency injection
def get_two_factor_service(db_session: AsyncSession) -> TwoFactorService:
    """Get TwoFactorService instance."""
    return TwoFactorService(db_session)
