"""
Database Models Package

This package contains all SQLAlchemy database models for the X University platform.
Models define the database schema and relationships using SQLAlchemy 2.0 ORM.

Current Models:
- auth.py: User authentication and session management models
  - User: Core user accounts with authentication details
  - Session: Active user sessions for security tracking
  - UserRole: Enumeration of user roles (Admin, Instructor, Student)

Model Architecture:
- All models inherit from Base class with automatic timestamps
- Integer primary keys for compatibility with existing data
- Comprehensive relationships with proper cascade options
- Type hints using SQLAlchemy 2.0 Mapped annotations
- Timezone-aware datetime fields
- Proper indexing for query performance

Design Principles:
- Clear model relationships with back_populates
- Comprehensive field validation and constraints
- Security-focused design (password hashing, session tracking)
- Audit trails with created_at/updated_at timestamps
- Role-based access control support

Future models will be added here as features are implemented
(courses, enrollments, assessments, etc.).

Version: 0.1.0
"""
