"""
API Routes Package

This package contains all individual route modules for the X University API,
organized by feature area for maintainability and scalability.

Current Route Modules:
- auth.py: Authentication and user management endpoints
  - User registration, login, logout
  - Token refresh and validation
  - User profile management
  
- users.py: Extended user management endpoints
  - User profile operations
  - Account settings and preferences
  
- monitor.py: System monitoring and health check endpoints
  - Health status monitoring
  - System status and metrics

Route Organization:
- Each module focuses on a specific domain area
- RESTful endpoint design with proper HTTP methods
- Comprehensive error handling and validation
- Role-based access control using dependencies
- Automatic OpenAPI documentation generation

All routes follow consistent patterns:
- Proper HTTP status codes and responses
- Input validation using Pydantic schemas
- Authentication and authorization where required
- Comprehensive error handling with structured responses
- Type hints for development safety and documentation

Version: 0.1.0
"""
