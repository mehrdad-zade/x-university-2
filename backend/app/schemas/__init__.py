"""
Pydantic Schemas Package

This package contains all Pydantic models for request/response validation
and serialization in the X University API.

Current Schemas:
- auth.py: Authentication-related request and response schemas
  - Request schemas: UserRegisterRequest, UserLoginRequest, etc.
  - Response schemas: TokenResponse, UserResponse, UserProfileResponse
  - Validation schemas with comprehensive field validation

Schema Architecture:
- Request validation with custom validators
- Response serialization with proper field mapping
- Comprehensive error response schemas
- Type-safe data models with Pydantic v2
- Automatic OpenAPI documentation generation
- Example data for API documentation

Features:
- Field validation with custom validators (email, password strength)
- Automatic data normalization (email lowercase, string trimming)
- Comprehensive error handling with structured error responses
- Type hints for IDE support and documentation
- JSON schema generation for client libraries

All schemas follow RESTful API conventions and provide clear
documentation through Pydantic's automatic OpenAPI integration.

Version: 0.1.0
"""
