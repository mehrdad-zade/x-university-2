"""
API Package for X University Backend

This package contains all FastAPI routes, endpoints, and API-related functionality.
The API is organized using a modular structure with clear separation of concerns.

Structure:
- main.py: Main API router that aggregates all route modules
- deps.py: Dependency injection for authentication, authorization, and services
- routes/: Individual route modules organized by feature area
  - auth.py: Authentication and user management endpoints
  - users.py: User profile and account management
  - monitor.py: System monitoring and health check endpoints

Design Principles:
- RESTful API design following HTTP standards
- Comprehensive OpenAPI documentation generation
- Consistent error handling and response formats
- Role-based access control with dependency injection
- Input validation using Pydantic schemas
- Type hints for automatic API documentation

All routes include proper authentication, authorization, request validation,
and error handling. The API supports JSON request/response format with
automatic schema validation and OpenAPI documentation generation.

Version: 0.1.0
"""
