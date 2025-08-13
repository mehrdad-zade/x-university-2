#!/usr/bin/env python3
"""
Database initialization script.
Creates default users for testing and development.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import AsyncSessionLocal
from app.models.auth import User, UserRole
from app.core.security import hash_password
from constants import DevCredentials, Messages


async def create_default_users():
    """Create default users for development and testing."""
    async with AsyncSessionLocal() as db:
        try:
            # Check if users already exist
            result = await db.execute(select(User))
            existing_users = result.scalars().all()
            
            if existing_users:
                print(f"{Messages.DB_USERS_EXIST}")
                return
            
            # Create default users using centralized constants
            default_users = [
                {
                    "email": DevCredentials.ADMIN_EMAIL,
                    "password": DevCredentials.PASSWORD,
                    "full_name": DevCredentials.ADMIN_NAME,
                    "role": UserRole.ADMIN,
                },
                {
                    "email": DevCredentials.INSTRUCTOR_EMAIL,
                    "password": DevCredentials.PASSWORD,
                    "full_name": DevCredentials.INSTRUCTOR_NAME,
                    "role": UserRole.INSTRUCTOR,
                },
                {
                    "email": DevCredentials.STUDENT_EMAIL,
                    "password": DevCredentials.PASSWORD,
                    "full_name": DevCredentials.STUDENT_NAME,
                    "role": UserRole.STUDENT,
                }
            ]
            
            for user_data in default_users:
                # Create user instance
                user = User(
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    email_verified=True  # Pre-verify default users
                )
                
                db.add(user)
                print(f"Created user: {user_data['email']} ({user_data['role']})")
            
            # Commit all users
            await db.commit()
            print(f"\n{Messages.DB_USERS_CREATED}")
            print(f"\n{Messages.LOGIN_CREDENTIALS_INFO}")
            print(f"  Admin:      {DevCredentials.ADMIN_EMAIL} / {DevCredentials.PASSWORD}")
            print(f"  Instructor: {DevCredentials.INSTRUCTOR_EMAIL} / {DevCredentials.PASSWORD}")
            print(f"  Student:    {DevCredentials.STUDENT_EMAIL} / {DevCredentials.PASSWORD}")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating default users: {e}")
            raise
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating default users: {e}")
            raise


async def main():
    """Main initialization function."""
    print(f"🚀 {Messages.DATABASE_SETUP}")
    await create_default_users()


if __name__ == "__main__":
    asyncio.run(main())
