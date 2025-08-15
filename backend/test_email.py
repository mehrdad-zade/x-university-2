#!/usr/bin/env python3
"""
Quick test script to verify Gmail SMTP email configuration
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService
from app.core.config import settings

async def test_email_service():
    """Test email service with Gmail SMTP"""
    email_service = EmailService()
    
    print("Testing Gmail SMTP configuration...")
    print(f"SMTP Host: {settings.SMTP_HOST}")
    print(f"SMTP Port: {settings.SMTP_PORT}")
    print(f"From Email: {settings.FROM_EMAIL}")
    print(f"Using Backend: {settings.EMAIL_BACKEND}")
    
    # Create a mock user object for testing
    class MockUser:
        def __init__(self, email: str, full_name: str):
            self.email = email
            self.full_name = full_name
    
    test_user = MockUser("zade.mehrdad@gmail.com", "Test User")
    
    try:
        await email_service.send_verification_email(
            user=test_user,
            verification_token="test-token-123"
        )
        print(f"✅ Test email sent successfully to {test_user.email}")
        print("Check your inbox (and spam folder) for the verification email")
        
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        print("This could be due to:")
        print("1. Incorrect App Password")
        print("2. Network connectivity issues")
        print("3. Gmail security settings")

if __name__ == "__main__":
    asyncio.run(test_email_service())
