# X University Backend API

## Requirements
- Python 3.12 (3.13 not yet supported by some dependencies)
- pip (latest version recommended)

Note: Python 3.13 is too new and not yet supported by all dependencies. Please use Python 3.12 for now.

## Technology Stack
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy 2.0** - Async ORM with advanced query capabilities
- **Alembic** - Database migrations management
- **PostgreSQL 16** - Primary relational database
- **Neo4j 5.x** - Graph database (optional for learning paths)
- **JWT Authentication** - Secure token-based authentication
- **OpenAI Integration** - AI content generation
- **Stripe/PayPal** - Payment processing
- **Docker** - Containerized system monitoring
- **psutil** - System performance metrics
- **structlog** - Structured logging

## New Dependencies Added
Recent additions to support new monitoring and authentication features:

```bash
# System monitoring
psutil==6.1.0          # System metrics (CPU, memory, disk, network)
docker==7.1.0          # Docker container management and monitoring

# Enhanced authentication
python-jose[cryptography]==3.3.0  # JWT token handling with crypto support
passlib[bcrypt]==1.7.4            # Password hashing with bcrypt
bcrypt==4.1.2                     # Secure password hashing

# Database performance monitoring
asyncpg==0.29.0        # High-performance PostgreSQL adapter
structlog==23.2.0      # Structured logging for better monitoring

# Testing and development
httpx==0.25.2          # Async HTTP client for testing
pytest-asyncio==0.23.2 # Async testing support
python-multipart>=0.0.7 # Form data parsing
```

## Project Structure
```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Migration environment
├── app/
│   ├── api/             # API routes and endpoints
│   │   ├── routes/      # Route modules
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   ├── users.py     # User management
│   │   │   └── monitor.py   # System monitoring
│   │   ├── deps.py      # Dependency injection
│   │   └── main.py      # API router aggregation
│   ├── core/            # Core functionality and config
│   │   ├── config.py    # Application configuration
│   │   └── security.py  # Authentication & authorization
│   ├── db/              # Database models and setup
│   │   ├── base.py      # Database session management
│   │   └── __init__.py
│   ├── models/          # SQLAlchemy ORM models
│   │   └── auth.py      # User and authentication models
│   ├── schemas/         # Pydantic models
│   │   └── auth.py      # Request/response schemas
│   ├── services/        # Business logic services
│   │   ├── auth_service.py      # Authentication business logic
│   │   └── db_performance.py   # Database monitoring service
│   └── workers/         # Background tasks
├── constants.py         # Centralized configuration constants
└── tests/               # Test suite
    ├── conftest.py      # Test configuration and fixtures
    └── test_*.py        # Test modules
```

## API Endpoints

### Authentication & User Management (`/api/v1/auth`)
- **POST /register** - Register new user account with enhanced security
  - Real-time password strength validation
  - Email normalization and uniqueness checking
  - Terms of service and privacy policy acceptance
  - Automatic login after successful registration
  - Returns JWT tokens for immediate access
- **POST /login** - Authenticate user and get tokens
  - Account lockout protection (5 failed attempts = 30min lockout)
  - Failed login attempt tracking and reset on success
  - Session creation and device tracking
- **POST /refresh** - Refresh access token using refresh token
- **POST /logout** - Logout and revoke tokens
- **GET /me** - Get current user profile with session stats
- **GET /validate** - Validate current access token
- **GET /health** - Authentication system health check

### User Management (`/api/v1/users`)
- User profile management endpoints (protected routes)

### System Monitoring (`/api/v1/monitor`) - **NEW**
Public endpoints for comprehensive system monitoring:

#### Core Monitoring
- **GET /monitor** - Complete system monitoring dashboard
- **GET /monitor/health** - Quick health status check

#### Database Performance - **NEW**
- **GET /monitor/database/performance** - Comprehensive DB metrics
- **GET /monitor/database/health** - Database health status  
- **GET /monitor/database/pool** - Connection pool statistics

#### Container Monitoring - **NEW**
- **POST /monitor/docker/enable-temp** - Enable temporary Docker monitoring
- **GET /monitor/docker/temp-data** - Get cached Docker container data

#### Log Streaming - **NEW**
- **GET /monitor/logs/{service}** - Get historical logs for a service
- **GET /monitor/logs/stream/{service}** - Real-time log streaming (SSE)
  - Supports: `backend`, `frontend`, `postgres`, `all`

## Development

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Code Quality Tools
```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy .

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Configuration

### Environment Variables
All configuration is handled through centralized constants loaded from `infra/dev.config.json`:

```json
{
  "urls": {
    "backend": "http://localhost:8000",
    "frontend": "http://localhost:5173",
    "api_base": "http://localhost:8000/api/v1"
  },
  "database": {
    "name": "xu2",
    "test_name": "xu2_test", 
    "user": "dev",
    "password": "devpass123",
    "host": "localhost",
    "port": 5432
  },
  "credentials": {
    "default_password": "password123"
  }
}
```

Access via: `from constants import URLs, Database, DevCredentials`

## API Documentation
- **Swagger UI**: http://localhost:8000/docs - Interactive API documentation
- **ReDoc**: http://localhost:8000/redoc - Alternative documentation format
- **OpenAPI Spec**: http://localhost:8000/openapi.json - Raw OpenAPI specification

## New Features Added

### 🔐 Enhanced Authentication System
- **JWT token-based authentication** with access and refresh tokens
- **Enhanced user registration** with real-time validation and security features:
  - Password strength checking (8+ chars, mixed case, numbers, symbols)
  - Email normalization and uniqueness validation
  - Role selection (student, instructor, admin)
  - Terms of service and privacy policy acceptance with timestamps
  - Automatic profile completion status tracking
- **Account security features**:
  - Failed login attempt tracking and account lockout (5 attempts = 30min lockout)
  - Password change timestamp tracking for security auditing
  - Email verification status (ready for future implementation)
  - Session management with device tracking and revocation
- **Role-based access control** (Admin, Instructor, Student)
- **Secure password hashing** using bcrypt with salt rounds

### 📊 System Monitoring Suite
- **Real-time system metrics**: CPU, memory, disk, network usage
- **Docker container monitoring**: Container stats, health, and logs
- **Database performance metrics**: Query performance, connection pools
- **Log streaming**: Real-time log viewing with Server-Sent Events
- **Health checks**: Comprehensive system health monitoring

### 🗄️ Database Performance Monitoring
- **Connection pool statistics**: Pool utilization and health
- **Slow query analysis**: Query performance tracking
- **Table statistics**: Size, row counts, and bloat monitoring
- **Index usage statistics**: Optimization recommendations
- **Performance recommendations**: Automated performance suggestions

### 🔧 Development Tools
- **Centralized configuration**: Single source of truth in `infra/dev.config.json`
- **Type-safe constants**: Python constants with IDE support
- **Async-first architecture**: Full async/await support
- **Comprehensive testing**: Fixtures for authentication and database
- **Structured logging**: Better debugging and monitoring

## Testing

### Test Structure
```bash
tests/
├── conftest.py          # Test fixtures and configuration
├── test_auth.py         # Authentication endpoint tests
├── test_health.py       # Health check tests
└── test_monitor.py      # Monitoring endpoint tests
```

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_auth.py

# With verbose output and coverage
pytest -v --cov=app

# Integration tests only
pytest -m "integration"

# Unit tests only
pytest -m "unit"
```

## Security Features

### Authentication Security
- **JWT tokens** with configurable expiration (15min access, 7day refresh)
- **Enhanced user registration security**:
  - Strong password requirements with server-side validation
  - Protection against common passwords and repeated characters
  - Email normalization to prevent duplicate accounts
  - Terms acceptance tracking with timestamps
- **Account protection features**:
  - Account lockout after 5 failed login attempts (30-minute lockout)
  - Failed login attempt counters with automatic reset on success
  - Password change tracking for security auditing
  - Session management with device and IP tracking
- **Refresh token rotation** for enhanced security
- **Session revocation** support (single session or all sessions)
- **Password hashing** using bcrypt with salt rounds
- **User agent and IP tracking** for session management

### API Security
- **Rate limiting** on authentication endpoints
- **Input validation** using Pydantic schemas
- **CORS configuration** for frontend integration
- **Error handling** with secure error messages
- **Database query parameterization** to prevent SQL injection

## Performance Features

### Database Optimization
- **Async connection pooling** with SQLAlchemy 2.0
- **Connection pool monitoring** and optimization
- **Query performance tracking** and analysis
- **Automatic index usage recommendations**
- **Connection leak detection**

### System Monitoring
- **Cached metrics** to reduce system load
- **Background monitoring** tasks
- **Resource usage alerts** and thresholds
- **Container resource monitoring**
- **Real-time log streaming** with rate limiting

## Future Enhancements

Planned features for upcoming releases:

### 📚 Course Management System
- Course creation and management APIs
- Student enrollment and progress tracking
- Assignment and grading systems

### 🤖 AI Content Generation
- OpenAI integration for content creation
- Automated quiz and assignment generation
- Personalized learning recommendations

### 💳 Payment Processing
- Stripe and PayPal integration
- Subscription management
- Invoice and receipt generation

### 📈 Advanced Analytics
- Learning progress analytics
- Performance dashboards
- Predictive learning models
