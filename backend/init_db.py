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


async def create_default_users():
    """Create default users for development and testing."""
    async with AsyncSessionLocal() as db:
        try:
            # Check if users already exist
            result = await db.execute(select(User))
            existing_users = result.scalars().all()
            
            if existing_users:
                print(f"Found {len(existing_users)} existing users, skipping initialization.")
                return
            
            # Create default users
            default_users = [
                {
                    "email": "admin@example.com",
                    "password": "admin123",
                    "full_name": "Default Admin",
                    "role": UserRole.ADMIN,
                },
                {
                    "email": "instructor@example.com",
                    "password": "instructor123",
                    "full_name": "Default Instructor",
                    "role": UserRole.INSTRUCTOR,
                },
                {
                    "email": "student@example.com",
                    "password": "student123",
                    "full_name": "Default Student",
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
            print("\n✅ Default users created successfully!")
            print("\nLogin credentials:")
            print("  Admin:      admin@example.com      / admin123")
            print("  Instructor: instructor@example.com / instructor123")
            print("  Student:    student@example.com    / student123")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating default users: {e}")
            raise


async def main():
    """Main initialization function."""
    print("🚀 Initializing database with default users...")
    await create_default_users()


if __name__ == "__main__":
    asyncio.run(main())
