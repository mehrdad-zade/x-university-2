"""
Core Application Components

This package contains the foundational components and utilities that support
the entire X University backend application.

Components:
- config.py: Application configuration management using Pydantic Settings
- security.py: JWT authentication, password hashing, and security utilities

The core package provides:
- Environment variable configuration with validation
- JWT token creation, validation, and management
- Password hashing and verification using bcrypt
- Security utilities for session management
- Application settings with type safety

These components are used throughout the application to maintain consistent
security practices and configuration management.

All security functions follow industry best practices:
- bcrypt for password hashing with automatic salting
- JWT tokens with configurable expiration times
- Cryptographically secure random ID generation
- Proper error handling for authentication failures

Version: 0.1.0
"""
