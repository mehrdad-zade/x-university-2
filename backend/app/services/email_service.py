"""
Email service for sending verification and notification emails.
Supports multiple backends: SMTP, SendGrid, AWS SES.
"""
import aiosmtplib
import logging
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from app.core.config import settings
from app.models.auth import User

logger = logging.getLogger(__name__)

# Optional SendGrid import
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False


class EmailBackend(ABC):
    """Abstract base class for email backends."""
    
    @abstractmethod
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = "") -> bool:
        """Send an email."""
        pass


class SendGridEmailBackend(EmailBackend):
    """SendGrid email backend using SendGrid API."""
    
    def __init__(self):
        if not SENDGRID_AVAILABLE:
            raise ImportError("SendGrid package not installed. Run: pip install sendgrid")
        
        self.api_key = settings.SENDGRID_API_KEY
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY not configured")
        
        self.from_email = settings.FROM_EMAIL
        self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = "") -> bool:
        """Send email via SendGrid API."""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            if text_content:
                message.content = text_content
            
            response = self.sg.send(message)
            
            if response.status_code in (200, 201, 202):
                logger.info(f"Email sent successfully via SendGrid to {to_email}")
                return True
            else:
                logger.error(f"SendGrid API error: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid to {to_email}: {str(e)}")
            return False


class SMTPEmailBackend(EmailBackend):
    """SMTP email backend using aiosmtplib."""
    
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = "") -> bool:
        """Send email via SMTP."""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.from_email
            message['To'] = to_email
            
            # Add text part if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                message.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email
            if self.password:
                await aiosmtplib.send(
                    message,
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    start_tls=True,
                    use_tls=False
                )
            else:
                # For development - no auth SMTP
                await aiosmtplib.send(
                    message,
                    hostname=self.host,
                    port=self.port
                )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False


class MockEmailBackend(EmailBackend):
    """Mock email backend for testing."""
    
    def __init__(self):
        self.sent_emails = []
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = "") -> bool:
        """Mock email sending - just log and store."""
        email_data = {
            'to_email': to_email,
            'subject': subject,
            'html_content': html_content,
            'text_content': text_content
        }
        self.sent_emails.append(email_data)
        logger.info(f"Mock email sent to {to_email}: {subject}")
        return True


class EmailService:
    """Email service with template rendering."""
    
    def __init__(self, backend: EmailBackend = None):
        self.backend = backend or self._get_default_backend()
        
        # Setup Jinja2 templates
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def _get_default_backend(self) -> EmailBackend:
        """Get default email backend based on configuration."""
        email_backend = getattr(settings, 'EMAIL_BACKEND', 'mock')
        
        if email_backend == 'smtp':
            return SMTPEmailBackend()
        elif email_backend == 'sendgrid':
            return SendGridEmailBackend()
        elif email_backend == 'mock':
            return MockEmailBackend()
        else:
            logger.warning(f"Unknown email backend: {email_backend}, using mock")
            return MockEmailBackend()
    
    async def send_verification_email(self, user: User, verification_token: str) -> bool:
        """Send email verification email to user."""
        try:
            # Create verification URL
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
            
            # Render email template
            try:
                template = self.template_env.get_template("verify_email.html")
                html_content = template.render(
                    user=user,
                    full_name=user.full_name,
                    verification_url=verification_url,
                    app_name="X-University",
                    frontend_url=settings.FRONTEND_URL
                )
            except Exception as e:
                logger.warning(f"Template rendering failed, using fallback: {e}")
                html_content = self._get_verification_email_fallback(user.full_name, verification_url)
            
            # Send email
            return await self.backend.send_email(
                to_email=user.email,
                subject="Verify your X-University account",
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
            return False
    
    async def send_2fa_disabled_notification(self, user: User) -> bool:
        """Send notification when 2FA is disabled."""
        try:
            html_content = f"""
            <h2>Two-Factor Authentication Disabled</h2>
            <p>Hi {user.full_name},</p>
            <p>Two-factor authentication has been disabled for your X-University account.</p>
            <p>If you didn't make this change, please contact support immediately.</p>
            <p>Best regards,<br>X-University Team</p>
            """
            
            return await self.backend.send_email(
                to_email=user.email,
                subject="Two-Factor Authentication Disabled",
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send 2FA disabled notification to {user.email}: {str(e)}")
            return False
    
    async def send_password_changed_notification(self, user: User) -> bool:
        """Send notification when password is changed."""
        try:
            html_content = f"""
            <h2>Password Changed</h2>
            <p>Hi {user.full_name},</p>
            <p>Your password has been successfully changed for your X-University account.</p>
            <p>If you didn't make this change, please contact support immediately.</p>
            <p>Best regards,<br>X-University Team</p>
            """
            
            return await self.backend.send_email(
                to_email=user.email,
                subject="Password Changed",
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send password changed notification to {user.email}: {str(e)}")
            return False
    
    def _get_verification_email_fallback(self, full_name: str, verification_url: str) -> str:
        """Fallback email template when Jinja2 template is not available."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Verify Your Email</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">Verify Your Email Address</h2>
            <p>Hi {full_name},</p>
            <p>Thank you for registering with X-University! Please click the button below to verify your email address:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                   Verify Email Address
                </a>
            </div>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #6b7280;">{verification_url}</p>
            
            <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
                This verification link will expire in 24 hours. If you didn't create an account with X-University, 
                you can safely ignore this email.
            </p>
            
            <p style="margin-top: 20px;">
                Best regards,<br>
                The X-University Team
            </p>
        </body>
        </html>
        """


# Global email service instance
email_service = EmailService()
