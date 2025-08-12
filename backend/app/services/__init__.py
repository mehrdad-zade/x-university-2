"""
Business Logic Services Package

This package contains the service layer for the X University backend,
implementing all business logic and operations that interact with the database.

Current Services:
- auth_service.py: User authentication and session management service
  - User registration and login operations
  - JWT token management (creation, validation, refresh)
  - Session tracking and security operations
  - Password validation and security checks

Service Architecture:
- Clean separation between API routes and business logic
- Database operations encapsulated in service methods
- Async/await pattern for non-blocking operations
- Comprehensive error handling with custom exceptions
- Transaction management for data consistency
- Security-focused operations (password hashing, token validation)

Design Principles:
- Single responsibility principle - each service handles one domain
- Dependency injection pattern for database sessions
- Type hints for development safety and documentation
- Comprehensive logging for debugging and monitoring
- Proper exception handling and error propagation

Services act as the middle layer between API routes and database models,
containing all business logic and ensuring proper separation of concerns.

Future services will be added here as features are implemented
(course management, enrollment, assessment, etc.).

Version: 0.1.0
"""
