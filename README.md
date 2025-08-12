# 🎓 X University 2.0

> Modern Learning Management System with AI-powered content generation and personalized learning paths

X University 2.0 is a comprehensive, next-generation learning management system designed for modern educational needs. It combines traditional course management with cutting-edge AI-powered content generation, personalized learning paths, integrated payment processing, and intelligent tutoring to create a complete educational ecosystem.

## 🌟 Project Overview

X University 2.0 represents a paradigm shift in educational technology, offering:

- **AI-First Approach**: Every aspect of the platform leverages artificial intelligence to enhance learning outcomes
- **Microlearning Focus**: Bite-sized, interconnected lessons that build comprehensive knowledge graphs
- **Personalized Pathways**: Adaptive learning routes that adjust to individual student needs and progress
- **Real-time Intelligence**: Live analytics, instant feedback, and dynamic content generation
- **Modern Architecture**: Built with scalable, cloud-native technologies for enterprise deployment

The platform serves educators, students, and institutions by providing tools for course creation, content delivery, progress tracking, and educational analytics—all powered by advanced AI algorithms.

## 🎯 Current Implementation Status

### ✅ Completed Features (Sprint S001_auth)

**Authentication System** - Fully Implemented & Tested
- ✅ JWT-based authentication with access & refresh tokens
- ✅ User registration with role-based permissions (Student, Instructor, Admin)
- ✅ Secure login/logout with bcrypt password hashing
- ✅ Session management and token validation
- ✅ Complete API endpoints with comprehensive error handling
- ✅ Database models with proper relationships and UUIDs
- ✅ 150+ comprehensive test cases covering all scenarios
- ✅ Interactive testing tools and documentation

**Development Environment** - Production Ready
- ✅ Complete Docker-based development setup
- ✅ Automated setup script with dependency checking
- ✅ Cross-platform support (macOS, Linux, Windows)
- ✅ Hot reload for both frontend and backend
- ✅ Comprehensive documentation and troubleshooting guides
- ✅ Browser tab integration (fixed new window issue)

**Code Quality & Testing**
- ✅ Type-safe backend with mypy strict mode
- ✅ Comprehensive test suite with pytest and async support
- ✅ Code formatting with ruff and black
- ✅ TypeScript frontend with strict mode enabled
- ✅ Database migrations with Alembic

### 🚧 In Development (Next Sprints)

**Course Management System** (Sprint S002_courses)
- 🔄 Course CRUD operations with rich content support
- 🔄 Lesson management and multimedia integration
- 🔄 Student enrollment and progress tracking
- 🔄 Instructor dashboard and course analytics

**AI Content Generation** (Sprint S006_ai_generation) 
- 🔄 OpenAI integration for automated course creation
- 🔄 Dynamic lesson and quiz generation
- 🔄 Intelligent content suggestions and optimization
- 🔄 Quality assurance for AI-generated content

**Learning Knowledge Graph** (Sprint S003_learning_graph)
- 🔄 Neo4j integration for concept relationships  
- 🔄 Visual learning path representation
- 🔄 Prerequisite tracking and enforcement
- 🔄 Adaptive learning route optimization

### 📋 Upcoming Features

**Dashboard & UI** (Sprint S004_dashboard_ui)
- 🔜 Student and instructor dashboards
- 🔜 Course catalog and search functionality
- 🔜 Progress visualization and analytics
- 🔜 Responsive design for all devices

**Payment Integration** (Sprint S005_payments)
- 🔜 Stripe integration for course purchases
- 🔜 PayPal alternative payment method
- 🔜 Subscription management and billing
- 🔜 Revenue analytics and reporting

**Progress Tracking** (Sprint S007_progress)
- 🔜 Detailed learning analytics
- 🔜 Competency mapping and skill tracking
- 🔜 Gamification elements and achievements
- 🔜 Performance insights and recommendations

**AI Tutor Bot** (Sprint S008_tutor_bot)
- 🔜 24/7 intelligent tutoring assistant
- 🔜 Contextual help and learning guidance
- 🔜 Natural language interaction interface
- 🔜 Personalized learning support

### 🧪 Testing & Quality Assurance

**Current Test Coverage**
- ✅ Authentication System: 95%+ coverage
- ✅ Database Models: 100% coverage
- ✅ API Endpoints: All auth endpoints tested
- ✅ Security Features: Comprehensive security testing
- ✅ Integration Tests: Database and API integration
- ✅ Error Handling: All error scenarios covered

**Quality Metrics**
- ✅ Zero known security vulnerabilities
- ✅ Full TypeScript strict mode compliance
- ✅ mypy strict mode for Python backend
- ✅ ESLint + Prettier for frontend consistency
- ✅ Comprehensive API documentation

## ✨ Key Features

### 🎯 Core Learning Management
- **Intelligent Course Management**: AI-assisted course structure optimization and content organization
- **Interactive Multimedia Lessons**: Rich content with embedded videos, interactive elements, and real-time assessments
- **Advanced Student Dashboard**: Personalized learning experience with AI-driven recommendations and progress visualization
- **Comprehensive Assessment System**: Automated quiz generation, intelligent grading, and detailed performance analytics
- **Learning Path Optimization**: Dynamic curriculum adjustment based on student performance and learning patterns

### 🤖 AI-Powered Intelligence
- **Automated Course Generation**: Create entire courses from simple prompts using advanced language models
- **Dynamic Content Creation**: Generate lessons, quizzes, assignments, and supplementary materials on-demand
- **Personalized Learning Paths**: AI algorithms create custom learning sequences for each student
- **Smart Content Recommendations**: Machine learning-driven suggestions for enhanced learning outcomes
- **Intelligent Tutoring System**: 24/7 AI teaching assistant providing personalized support and guidance

### 💡 Advanced Platform Features
- **Learning Knowledge Graph**: Neo4j-powered visualization of concept relationships and dependencies
- **Real-time Progress Analytics**: Deep insights into learning patterns, engagement metrics, and performance trends
- **Integrated Payment Processing**: Full Stripe and PayPal integration for course monetization
- **Multi-tenant Architecture**: Support for multiple institutions and organizations
- **API-First Design**: RESTful APIs with comprehensive documentation for third-party integrations
- **Mobile-Responsive Interface**: Seamless experience across all devices and screen sizes

## 🚀 Quick Start

The fastest way to get X University 2.0 running locally is using our automated setup script:

```bash
# Make the script executable (one-time setup)
chmod +x setup.sh

# Run complete setup (takes 5-10 minutes)
./setup.sh
```

This single command will:
- ✅ Verify and install all prerequisites (Python 3.12, Node.js 20+, Docker)
- ✅ Set up isolated Python virtual environment with all backend dependencies
- ✅ Configure Node.js environment and install frontend dependencies
- ✅ Launch Docker services (PostgreSQL, optional Neo4j for learning graphs)
- ✅ Execute database migrations and initialize the authentication system
- ✅ Run comprehensive test suites (backend API tests, frontend component tests)
- ✅ Auto-open browser tabs in existing browser window (no new windows!)

### 🔐 Default Login Credentials

After setup, you can test the authentication system with these credentials:

**Test Admin User:**
- Email: `admin@example.com`
- Password: `admin123`
- Role: Administrator

**Test Student User:**
- Email: `student@example.com` 
- Password: `admin123`
- Role: Student

**Test Instructor User:**
- Email: `instructor@example.com`
- Password: `admin123`
- Role: Instructor

> **Note**: These are development-only credentials. In production, create secure admin accounts through the API.

### Setup Options

```bash
./setup.sh                    # Standard setup with all features
./setup.sh --clean           # Clean install (removes existing environments)
./setup.sh --skip-tests      # Skip test execution during setup
./setup.sh --skip-browser    # Don't auto-open browser tabs in existing window
```

### Browser Integration Features

The setup script now intelligently opens all service endpoints in **new tabs** of your existing browser window (no more annoying new windows!):

- 🌐 **Frontend Application**: Opens in a new tab
- 📚 **API Documentation**: Opens in a new tab  
- 🔧 **Health Check**: Opens in a new tab

The script detects your running browser (Safari, Chrome, Firefox) and uses the appropriate method to create tabs instead of new windows.

### Services After Setup

Once setup completes successfully, you'll have access to:
- 🌐 **Frontend Application**: http://localhost:5173 - Main user interface
- 🔧 **Backend API**: http://localhost:8000 - Core application services
- 📚 **Interactive API Documentation**: http://localhost:8000/docs - Swagger/OpenAPI interface
- 📊 **Health Monitoring**: http://localhost:8000/health - Service health checks
- 🗄️ **PostgreSQL Database**: localhost:5432 - Primary data storage
- 🕸️ **Neo4j Browser** (optional): http://localhost:7474 - Learning graph visualization

##  Prerequisites

X University 2.0 requires specific software versions for optimal performance and compatibility:

### Required Software

| Software | Version | Installation |
|----------|---------|-------------|
| **Python** | 3.12.x (exact version required) | [Download](https://www.python.org/downloads/) |
| **Node.js** | ≥ 20.0 (tested with 23.6.1) | [Download](https://nodejs.org/) |
| **Docker Desktop** | Latest stable | [Download](https://www.docker.com/products/docker-desktop) |
| **Docker Compose** | Included with Docker Desktop | - |
| **Git** | Latest | [Download](https://git-scm.com/) |

### Platform-Specific Installation

#### macOS (Recommended: Homebrew)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install python@3.12 node@20 git
brew link --force python@3.12
brew link node@20

# Install Docker Desktop manually from https://www.docker.com/products/docker-desktop
```

#### Ubuntu/Debian Linux
```bash
# Update package manager
sudo apt update

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3.12-dev

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Docker
sudo apt install docker.io docker-compose-plugin

# Install Git
sudo apt install git
```

#### RHEL/Fedora/CentOS
```bash
# Install Python 3.12
sudo dnf install python3.12 python3.12-pip python3.12-devel

# Install Node.js 20.x
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install nodejs

# Install Docker
sudo dnf install docker docker-compose

# Install Git
sudo dnf install git
```

### Version Verification

Before proceeding, verify your installations:

```bash
# Check Python version (must be 3.12.x)
python3.12 --version
# or
python3 --version

# Check Node.js version (must be ≥ 20.0)
node --version

# Check npm version
npm --version

# Check Docker installation
docker --version
docker-compose --version

# Check Git installation
git --version
```

### Additional Notes

- **Python 3.13**: Not yet supported due to some dependencies not being compatible
- **Node.js**: Versions below 20.0 may cause compatibility issues with frontend dependencies
- **Docker**: Make sure Docker Desktop is running before executing the setup script
- **Virtual Environments**: The setup script will automatically create isolated Python and Node.js environments

### Quick Compatibility Check

The setup script includes built-in compatibility checking and will:
- ✅ Auto-detect installed software versions
- ✅ Provide specific installation instructions for your platform
- ✅ Auto-start Docker Desktop on macOS if not running
- ⚠️ Stop with clear error messages if incompatible versions are detected

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/mehrdad-zade/x-university-2.git
cd x-university-2

# Run the setup script
./setup.sh
```

The setup script will:
- ✅ Check all prerequisites and versions
- ✅ Auto-start Docker Desktop (macOS)
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Start all services with Docker
- ✅ Run database migrations
- ✅ Execute tests
- ✅ Open services in your browser

### Setup Options

```bash
# Clean setup (removes existing environments)
./setup.sh --clean

# Skip running tests during setup
./setup.sh --skip-tests

# Skip opening browser tabs
./setup.sh --skip-browser

# Combine options
./setup.sh --clean --skip-tests --skip-browser
```

## 🌐 Services

After setup, these services will be available:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | React application |
| **Backend API** | http://localhost:8000 | FastAPI REST API |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger documentation |
| **Health Check** | http://localhost:8000/health | Backend health status |
| **PostgreSQL** | localhost:5432 | Database (credentials in .env) |
| **Neo4j Browser** | http://localhost:7474 | Graph database (if enabled) |

## 🛠 Development Workflow

### Daily Development Commands

The project includes a Makefile with common development tasks:

```bash
# Service management
make up          # Start all services
make down        # Stop all services
make restart     # Restart all services
make logs        # View service logs

# Development tasks
make test        # Run all tests (backend + frontend)
make test-backend # Run only backend tests
make test-frontend # Run only frontend tests
make fmt         # Format all code (Python + JavaScript/TypeScript)
make lint        # Run linters
make migrate     # Run database migrations
make seed        # Load seed data
```

### Project Structure

```
x-university-2/
├── backend/                    # FastAPI backend service
│   ├── app/
│   │   ├── api/               # API routes and endpoints
│   │   │   ├── v1/            # API v1 routes
│   │   │   │   ├── auth/      # Authentication endpoints
│   │   │   │   ├── courses/   # Course management
│   │   │   │   ├── users/     # User management
│   │   │   │   └── ai/        # AI content generation
│   │   │   └── deps.py        # API dependencies
│   │   ├── core/              # Configuration and security
│   │   │   ├── config.py      # Settings and environment
│   │   │   ├── security.py    # JWT and auth utilities
│   │   │   └── database.py    # Database connection
│   │   ├── db/                # Database models and utilities
│   │   │   ├── models/        # SQLAlchemy models
│   │   │   └── schemas/       # Pydantic schemas
│   │   ├── services/          # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── course_service.py
│   │   │   └── ai_service.py
│   │   └── main.py            # FastAPI application entry
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend test suite
│   │   ├── conftest.py        # Test configuration
│   │   ├── test_auth.py       # Authentication tests
│   │   └── test_courses.py    # Course management tests
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container definition
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── ui/           # Basic UI primitives
│   │   │   ├── forms/        # Form components
│   │   │   └── layout/       # Layout components
│   │   ├── pages/            # Application pages/routes
│   │   │   ├── auth/         # Login, signup pages
│   │   │   ├── courses/      # Course-related pages
│   │   │   └── dashboard/    # Student/teacher dashboards
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API client and utilities
│   │   │   ├── api.ts        # API client configuration
│   │   │   ├── auth.ts       # Authentication service
│   │   │   └── courses.ts    # Course API calls
│   │   ├── types/            # TypeScript type definitions
│   │   ├── utils/            # Utility functions
│   │   └── App.tsx           # Main application component
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies
│   └── Dockerfile            # Frontend container definition
├── infra/                     # Infrastructure configuration
│   ├── docker-compose.yml    # Service orchestration
│   ├── .env.example          # Environment variables template
│   └── init-data/            # Database initialization scripts
│       ├── sample_users.sql  # Sample user data
│       └── sample_courses.sql # Sample course content
├── documents-references/      # Project documentation and planning
│   ├── README.md             # Development specifications
│   └── sprints/              # Development sprint planning
│       ├── S001_auth.md      # Authentication sprint
│       ├── S002_courses.md   # Course management sprint
│       └── ...               # Additional sprints
├── scripts/                   # Utility scripts
│   └── cleanup.sh            # Environment cleanup script
├── setup.sh                  # Automated development setup
├── Makefile                  # Common development commands
├── LICENSE                   # MIT license
└── README.md                 # This file
```

### Coding Standards and Best Practices

#### Backend Standards (Python/FastAPI)
- **Type Safety**: Full mypy support with strict type checking
- **Code Quality**: `ruff` for linting, `black` for formatting
- **Testing**: `pytest` with async support, minimum 80% coverage on API routes
- **Database**: Alembic-only migrations, never raw schema changes
- **API Design**: Pydantic schemas at API boundaries, separate DTOs from ORM models
- **Logging**: Structured JSON logging with `structlog`
- **Documentation**: Comprehensive docstrings and auto-generated OpenAPI docs

#### Frontend Standards (React/TypeScript)
- **Type Safety**: TypeScript strict mode enabled
- **Code Quality**: ESLint + Prettier for consistent formatting
- **Testing**: React Testing Library for component tests, focus on key user flows
- **State Management**: React Query for server state, Zustand for client state
- **Styling**: TailwindCSS utility classes, component-scoped styles
- **Performance**: Code splitting, lazy loading, optimized bundle size

#### Development Workflow Standards
- **Git Flow**: Feature branches, comprehensive commit messages
- **CI/CD Ready**: All formatting, linting, and tests automated
- **Container First**: Development parity with production via Docker
- **Environment Management**: Comprehensive `.env` configuration
- **Security**: JWT authentication, bcrypt password hashing, CORS configuration

### Database Management

The project uses PostgreSQL with automatic initialization:

- **Main Database**: `xu2` (development data)
- **Test Database**: `xu2_test` (testing only)
- **Sample Data**: Automatically loaded on first run
- **Migrations**: Handled with Alembic

#### Database Commands

```bash
# Run migrations
docker compose -f infra/docker-compose.yml exec backend alembic upgrade head

# Create new migration
docker compose -f infra/docker-compose.yml exec backend alembic revision --autogenerate -m "description"

# Reset database (removes all data)
docker compose -f infra/docker-compose.yml down -v
docker compose -f infra/docker-compose.yml up -d
```

### Cleanup

```bash
# Stop and remove everything
./scripts/cleanup.sh

# Or manually
docker compose -f infra/docker-compose.yml down -v
docker system prune -a
```

## 🧪 Testing

### Backend Tests
```bash
# Run all backend tests
make test-backend
# or
docker compose -f infra/docker-compose.yml exec backend pytest

# Run specific test file
docker compose -f infra/docker-compose.yml exec backend pytest tests/test_health.py

# Run with coverage
docker compose -f infra/docker-compose.yml exec backend pytest --cov=app
```

### Frontend Tests
```bash
# Run frontend tests
make test-frontend
# or
docker compose -f infra/docker-compose.yml exec frontend npm test

# Run in watch mode
docker compose -f infra/docker-compose.yml exec frontend npm run test:watch
```

## 🏗 Architecture & Technology Stack

X University 2.0 is built with a modern, scalable microservices architecture designed for cloud-native deployment and enterprise-grade performance.

### Technology Stack Overview

#### Backend Stack
| Component | Technology | Purpose | Version |
|-----------|------------|---------|---------|
| **Web Framework** | FastAPI | High-performance async API framework | Latest |
| **Database ORM** | SQLAlchemy 2.0 | Modern async ORM with type safety | 2.x |
| **Migrations** | Alembic | Database schema version control | Latest |
| **Validation** | Pydantic v2 | Data validation and serialization | 2.x |
| **Authentication** | JWT | Stateless authentication with refresh tokens | Custom |
| **Password Hashing** | bcrypt | Secure password storage | Latest |
| **Logging** | structlog | Structured JSON logging | Latest |
| **Type Checking** | mypy | Static type checking | Latest |
| **Code Quality** | ruff + black | Linting and code formatting | Latest |

#### Database Layer
| Database | Purpose | Usage | Optional |
|----------|---------|-------|----------|
| **PostgreSQL 16** | Primary data store | User data, courses, progress, transactions | No |
| **Neo4j 5.x** | Graph database | Learning path relationships and knowledge graphs | Yes |

#### Frontend Stack
| Component | Technology | Purpose | Version |
|-----------|------------|---------|---------|
| **Framework** | React 18 | Modern component-based UI | 18.x |
| **Language** | TypeScript | Type-safe JavaScript development | 5.x |
| **Build Tool** | Vite | Lightning-fast development and builds | Latest |
| **Styling** | TailwindCSS | Utility-first CSS framework | 3.x |
| **State Management** | React Query + Zustand | Server state and client state management | Latest |
| **Testing** | React Testing Library | Component and integration testing | Latest |
| **Code Quality** | ESLint + Prettier | Linting and code formatting | Latest |

#### External Services Integration
| Service | Purpose | Environment | Status |
|---------|---------|-------------|--------|
| **OpenAI API** | AI content generation and tutoring | Production ready | Active |
| **Stripe** | Primary payment processing | Test mode for development | Active |
| **PayPal** | Alternative payment processing | Sandbox for development | Active |

#### Infrastructure & DevOps
| Tool | Purpose | Usage | Environment |
|------|---------|-------|-------------|
| **Docker Compose** | Local development orchestration | Multi-service coordination | Development |
| **PostgreSQL 16** | Production-grade relational database | Primary data storage | All |
| **Neo4j** (optional) | Graph database for learning relationships | Knowledge graphs | All |
| **Docker** | Containerization platform | Service isolation | All |

### Microservices Architecture

The platform follows a modular microservices approach with clear service boundaries:

#### Core Service Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│              (React + TypeScript + Vite)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────────────────┐
│                  API Gateway Layer                          │
│                   (FastAPI Router)                          │
├─────────────────────┬───────────────────────────────────────┤
│                     │ Internal API Calls                   │
│  ┌──────────────────▼──┐  ┌─────────────┐  ┌─────────────┐ │
│  │   Auth Service      │  │   Course    │  │  AI Content │ │
│  │   - JWT tokens      │  │   Service   │  │   Service   │ │
│  │   - User profiles   │  │   - CRUD    │  │   - OpenAI  │ │
│  │   - Permissions     │  │   - Progress│  │   - Generate│ │
│  └─────────────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ Database Connections
┌─────────────────────▼───────────────────────────────────────┐
│                   Data Layer                                │
│  ┌─────────────────┐           ┌─────────────────────────┐  │
│  │   PostgreSQL    │           │      Neo4j (Optional)  │  │
│  │   - User data   │           │   - Learning graphs    │  │
│  │   - Courses     │           │   - Knowledge maps     │  │
│  │   - Progress    │           │   - Prerequisites      │  │
│  │   - Payments    │           │   - Relationships      │  │
│  └─────────────────┘           └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Service Responsibilities

**Authentication Service**
- JWT token generation and validation
- User registration and login
- Password hashing and security
- Role-based access control (RBAC)
- Session management

**Course Management Service**
- Course CRUD operations
- Lesson content management
- Curriculum structure
- Student enrollment
- Progress tracking

**AI Content Generation Service**
- OpenAI API integration
- Automated course generation
- Dynamic lesson creation
- Quiz and assessment generation
- Content quality assurance

**Payment Processing Service**
- Stripe integration for card payments
- PayPal integration for alternative payments
- Subscription management
- Transaction history
- Revenue analytics

**Analytics Service**
- Learning progress tracking
- Performance metrics
- Engagement analytics
- Recommendation algorithms
- Reporting dashboards

### Data Flow Architecture

```
┌──────────────┐    HTTP/REST    ┌─────────────┐
│   React      │◄──────────────► │   FastAPI   │
│   Frontend   │     API         │   Backend   │
└──────────────┘                 └─────┬───────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
              ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
              │PostgreSQL │      │   Neo4j   │      │ External  │
              │ (Primary) │      │(Optional) │      │   APIs    │
              │           │      │           │      │           │
              │• Users    │      │• Learning │      │• OpenAI   │
              │• Courses  │      │  Paths    │      │• Stripe   │
              │• Progress │      │• Knowledge│      │• PayPal   │
              │• Payments │      │  Graph    │      │           │
              └───────────┘      └───────────┘      └───────────┘
```

### Security Architecture

**Multi-Layer Security Implementation**

1. **Authentication Layer**
   - JWT access tokens (30-minute expiration)
   - Refresh tokens (7-day expiration)
   - Secure token storage and rotation

2. **Authorization Layer**
   - Role-based access control (Student, Instructor, Admin)
   - Resource-level permissions
   - API endpoint protection

3. **Data Security**
   - bcrypt password hashing with salt rounds
   - SQL injection prevention via ORM
   - Input validation with Pydantic schemas

4. **Network Security**
   - CORS policy configuration
   - Rate limiting (planned)
   - Request sanitization

5. **Environment Security**
   - Environment variable isolation
   - Secret management
   - Development/production separation

### Performance & Scalability

**Backend Performance**
- Async/await throughout the application stack
- Connection pooling for database operations
- Lazy loading for optimal query performance
- Caching strategies for frequent operations

**Frontend Performance**
- Code splitting and lazy loading
- React Query for intelligent caching
- Optimized bundle size with tree shaking
- Progressive web app (PWA) capabilities

**Database Optimization**
- Properly indexed columns for fast queries
- Query optimization with SQLAlchemy 2.0
- Connection pooling and management
- Horizontal scaling support (planned)

**Monitoring & Observability**
- Structured JSON logging with correlation IDs
- Health check endpoints for all services
- Performance metrics collection
- Error tracking and alerting (planned)

## 🔧 Configuration & Environment Variables

### Environment Setup

The project uses environment variables for all configuration. Copy the template and customize for your environment:

```bash
cp infra/.env.example infra/.env
```

### Complete Environment Variables Reference

#### Database Configuration
```env
# PostgreSQL Primary Database
POSTGRES_USER=dev
POSTGRES_PASSWORD=devpass  
POSTGRES_DB=xu2
DATABASE_URL=postgresql+psycopg://dev:devpass@postgres:5432/xu2

# Test Database (automatically created)
TEST_DATABASE_URL=postgresql+psycopg://dev:devpass@postgres:5432/xu2_test
```

#### Backend API Configuration
```env
# Core API Settings
API_PORT=8000
SECRET_KEY=change-me-to-a-secure-random-string-in-production
DEBUG=true
ENVIRONMENT=development

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# JWT Token Configuration
ACCESS_TOKEN_EXPIRES_MINUTES=30
REFRESH_TOKEN_EXPIRES_DAYS=7
ALGORITHM=HS256

# API Rate Limiting (planned feature)
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

#### Neo4j Graph Database (Optional)
```env
# Neo4j Configuration
ENABLE_NEO4J=false          # Set to 'true' to enable learning graphs
NEO4J_USER=neo4j
NEO4J_PASSWORD=devpass
NEO4J_URI=bolt://neo4j:7687
NEO4J_DATABASE=neo4j

# Neo4j Licensing
NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
```

#### External API Integration
```env
# OpenAI for AI Content Generation
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Stripe Payment Processing
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
STRIPE_CURRENCY=usd

# PayPal Payment Processing
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_ENVIRONMENT=sandbox  # 'sandbox' for development, 'live' for production
```

#### Email Configuration (Planned)
```env
# Email Service Configuration
EMAIL_PROVIDER=smtp
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_TLS=true
FROM_EMAIL=noreply@xuniversity.dev
```

#### Logging and Monitoring
```env
# Logging Configuration
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json             # 'json' or 'text'
LOG_FILE_PATH=logs/app.log

# Monitoring (Future Implementation)
SENTRY_DSN=                 # Sentry error tracking
ENABLE_METRICS=false        # Prometheus metrics
METRICS_PORT=9090
```

### Environment-Specific Configurations

#### Development Environment
```env
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
```

#### Production Environment (Example)
```env
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=WARNING
SECRET_KEY=very-long-secure-random-string
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DATABASE_URL=postgresql+psycopg://user:password@prod-db:5432/xu2_prod
```

#### Testing Environment
```env
ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=ERROR
DATABASE_URL=postgresql+psycopg://dev:devpass@postgres:5432/xu2_test
```

### Configuration Validation

The application includes comprehensive configuration validation:

```python
# Automatic validation on startup
# - Checks for required environment variables
# - Validates data types and formats  
# - Provides clear error messages for missing/invalid config
# - Supports different configurations per environment
```

### Security Best Practices

#### Secret Management
- ✅ Never commit `.env` files to version control
- ✅ Use strong, unique passwords for all services
- ✅ Rotate API keys and secrets regularly
- ✅ Use environment-specific configurations
- ✅ Enable HTTPS in production environments

#### Database Security
- ✅ Use strong database passwords
- ✅ Limit database user permissions
- ✅ Enable SSL connections in production
- ✅ Regular database backups
- ✅ Monitor for suspicious activity

### Docker Environment Integration

The Docker Compose setup automatically loads your `.env` file:

```yaml
# docker-compose.yml snippet
services:
  backend:
    env_file:
      - .env
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
```

### Environment Variable Precedence

Configuration sources in order of precedence (highest to lowest):
1. **Command line arguments**
2. **Environment variables** 
3. **`.env` file**
4. **Default values in code**

### Troubleshooting Configuration

Common configuration issues and solutions:

```bash
# Check if .env file is loaded correctly
docker compose -f infra/docker-compose.yml config

# Verify environment variables in container
docker compose -f infra/docker-compose.yml exec backend env | grep -E 'DATABASE_URL|SECRET_KEY'

# Test database connection
docker compose -f infra/docker-compose.yml exec backend python -c "
from app.core.config import settings
from app.core.database import engine
print(f'Database URL: {settings.database_url}')
"
```

## 📚 API Documentation & Authentication

Once the backend is running, visit:
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)
- **Health Check**: http://localhost:8000/health

### 🔐 Authentication API Endpoints

The authentication system is fully implemented and ready for testing:

#### Core Auth Endpoints
```bash
# User Registration
POST /api/v1/auth/register
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe",
  "role": "student"  # Optional: student, instructor, admin
}

# User Login
POST /api/v1/auth/login
Content-Type: application/json
{
  "email": "admin@example.com",
  "password": "admin123"
}

# Get Current User Profile
GET /api/v1/auth/me
Authorization: Bearer <your_access_token>

# Refresh Access Token
POST /api/v1/auth/refresh
Content-Type: application/json
{
  "refresh_token": "<your_refresh_token>"
}

# Logout (Invalidate Session)
POST /api/v1/auth/logout
Authorization: Bearer <your_access_token>

# Validate Token
POST /api/v1/auth/validate
Authorization: Bearer <your_access_token>
```

### 🧪 Testing the Authentication System

You can test the authentication system using the provided credentials:

1. **Login via API**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"admin@example.com","password":"admin123"}'
   ```

2. **Use the Interactive Testing Script**:
   ```bash
   cd backend
   python test_auth.py  # Interactive authentication testing
   ```

3. **Via Swagger UI**: Visit http://localhost:8000/docs and use the "Try it out" features

### Key API Features

#### Authentication Features
- ✅ **JWT Access Tokens**: 30-minute expiration with automatic refresh
- ✅ **Refresh Tokens**: 7-day expiration for seamless re-authentication  
- ✅ **Role-Based Access Control**: Student, Instructor, Admin permissions
- ✅ **Session Management**: Secure token invalidation and logout
- ✅ **Password Security**: bcrypt hashing with salt rounds

#### Course Management (Coming Next)
- `GET /api/v1/courses/` - List all available courses
- `POST /api/v1/courses/` - Create new course (instructor/admin only)
- `GET /api/v1/courses/{id}` - Get specific course details
- `PUT /api/v1/courses/{id}` - Update course (owner/admin only)

#### User Management
- `GET /api/v1/users/me` - Current user profile
- `GET /api/v1/users/` - List users (admin only)
- `GET /api/v1/users/{id}` - Get specific user (admin only)
- `PUT /api/v1/users/me` - Update own profile

## 🚨 Troubleshooting

### Common Issues & Solutions

#### Frontend TypeScript Errors
```bash
# Missing React type definitions
cd frontend
npm install --save-dev @types/react @types/react-dom

# Module resolution issues  
rm -rf node_modules package-lock.json
npm install

# If you see "Cannot find module 'react-router-dom'" errors:
npm install react-router-dom
./setup.sh --clean  # Fresh install
```

#### Backend Dependency Issues
```bash
# JWT module missing
# Fixed automatically - requirements.txt includes PyJWT

# Python virtual environment issues
rm -rf backend/.venv
./setup.sh --clean

# Alembic migration errors
docker compose -f infra/docker-compose.yml exec backend alembic stamp head
docker compose -f infra/docker-compose.yml exec backend alembic upgrade head
```
#### Docker Issues
```bash
# Docker not running
# macOS: The setup script will auto-start Docker Desktop
# Linux: sudo systemctl start docker

# Permission denied
sudo usermod -aG docker $USER
# Then log out and back in

# Port conflicts
docker ps  # Check what's using ports 5173, 8000, 5432
lsof -i :8000  # Check specific port usage
```

#### Python Issues
```bash
# Wrong Python version
python3 --version  # Should be 3.12.x
brew link --force python@3.12  # macOS

# Virtual environment issues
rm -rf backend/.venv
./setup.sh --clean
```

#### Node.js Issues
```bash
# Wrong Node version
node --version  # Should be 20.x or higher
npm --version   # Should be 10.x or higher

# Dependency conflicts
rm -rf frontend/node_modules frontend/package-lock.json
cd frontend && npm install
```

#### Database Issues
```bash
# Connection refused
docker compose -f infra/docker-compose.yml logs postgres

# Reset database
docker compose -f infra/docker-compose.yml down -v
docker compose -f infra/docker-compose.yml up -d
```

### Getting Help

1. **Check the logs**: `docker compose -f infra/docker-compose.yml logs -f`
2. **Verify services**: `docker compose -f infra/docker-compose.yml ps`
3. **Check health**: `curl http://localhost:8000/health`
4. **Reset everything**: `./scripts/cleanup.sh && ./setup.sh --clean`

### High-Level Platform Modules

X University 2.0 is organized into distinct, interconnected modules that work together to provide a comprehensive learning experience:

#### 🔐 Authentication & User Management
- **Multi-role user system**: Students, instructors, administrators with granular permissions
- **Secure authentication**: JWT-based with refresh tokens and password security
- **Profile management**: Comprehensive user profiles with learning preferences
- **Social features**: User interactions, discussion forums, peer learning

#### 📚 Course & Content Management  
- **Dynamic course creation**: AI-assisted course structure with intelligent content organization
- **Rich multimedia lessons**: Interactive content with videos, animations, and real-time elements
- **Assessment engine**: Automated quiz generation, various question types, adaptive difficulty
- **Content versioning**: Track changes, rollback capabilities, A/B testing for content

#### � AI-Powered Learning Intelligence
- **Automated content generation**: Create courses, lessons, and assessments from simple prompts
- **Personalized learning paths**: AI algorithms adapt content sequence to individual learning patterns  
- **Intelligent recommendations**: Machine learning-driven content suggestions and next steps
- **Content quality assurance**: Automated review and improvement suggestions for educational materials

#### 📊 Progress Tracking & Analytics
- **Real-time progress monitoring**: Detailed insights into learning patterns and engagement
- **Performance analytics**: Individual and cohort-level performance tracking
- **Competency mapping**: Skills and knowledge gap analysis with targeted improvement suggestions
- **Gamification elements**: Achievements, badges, leaderboards to enhance motivation

#### 💰 Payments & Monetization
- **Multi-payment support**: Stripe and PayPal integration for global accessibility
- **Subscription management**: Flexible pricing models, trial periods, and billing cycles
- **Revenue analytics**: Comprehensive financial reporting and revenue tracking
- **Refund management**: Automated refund processing and dispute handling

#### 💬 Intelligent Tutoring System
- **24/7 AI teaching assistant**: Personalized support and guidance for every student
- **Contextual help**: Understands current lesson context and provides relevant assistance
- **Learning path optimization**: Continuously adjusts difficulty and content based on performance
- **Natural language interaction**: Conversational interface for intuitive learning support

#### 🕸️ Learning Knowledge Graph (Optional)
- **Visual concept relationships**: Interactive visualization of how concepts connect and build upon each other
- **Prerequisite tracking**: Automated identification and enforcement of learning dependencies
- **Adaptive pathways**: Dynamic route adjustment based on mastery and learning goals
- **Collaborative learning maps**: Shared knowledge structures for group learning experiences

### Learning Philosophy & Approach

**Microlearning Focus**: The platform emphasizes bite-sized, focused learning sessions that build comprehensive knowledge over time. Each lesson is designed to be completed in 10-15 minutes, making learning accessible and sustainable.

**Competency-Based Progression**: Students advance based on demonstrated mastery rather than time spent. The AI continuously assesses understanding and adjusts content accordingly.

**Social Learning Integration**: Collaborative features encourage peer-to-peer learning, discussion, and knowledge sharing while maintaining individual learning paths.

**Real-World Application**: Every course includes practical projects and real-world scenarios to ensure knowledge transfer and practical skill development.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `make test`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Workflow

```bash
# Start development
./setup.sh

# Make changes to code (hot reload enabled)
# Backend changes: app/ directory
# Frontend changes: src/ directory

# Run tests
make test

# Format code
make fmt

# Stop when done
make down
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent async Python framework
- React team for the robust frontend library
- Docker for containerization
- PostgreSQL for reliable data storage

---

## 📞 Support

If you encounter any issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the logs: `docker compose -f infra/docker-compose.yml logs -f`
3. Try a clean setup: `./setup.sh --clean`
4. Open an issue on GitHub

**Happy coding! 🚀**
