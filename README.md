# 🎓 X University 2.0

> Modern Learning Management System with AI-powered content generation, real-time system monitoring, and personalized learning paths

X University 2.0 is a comprehensive, next-generation learning management system designed for modern educational needs. It combines traditional course management with cutting-edge AI-powered content generation, personalized learning paths, intelligent tutoring, and advanced system monitoring to create a complete educational ecosystem.

## 🌟 Quick Overview

X University 2.0 represents a paradigm shift in educational technology, offering:

- **🤖 AI-First Approach**: Every aspect leverages artificial intelligence to enhance learning
- **📚 Microlearning Focus**: Bite-sized, interconnected lessons with knowledge graphs
- **🎯 Personalized Pathways**: Adaptive learning routes for individual student needs
- **📊 Real-time Intelligence**: Live analytics, instant feedback, and dynamic content generation
- **🔧 System Monitoring**: Comprehensive monitoring with Docker container, database performance, and log streaming
- **☁️ Modern Architecture**: Scalable, cloud-native technologies with containerized deployment

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** - Container orchestration
- **Python 3.12** - Backend development
- **Node.js 20+** - Frontend development
- **Git** - Version control
- **Gmail App Password** - For email functionality, see [Gmail App Password Setup](https://support.google.com/accounts/answer/185833)

### Get Started in 60 Seconds

```bash
# Clone the repository
git clone https://github.com/mehrdad-zade/x-university-2.git
cd x-university-2

# Run automated setup (includes all dependencies)
make fresh

# Or use the detailed setup script
./scripts/setup.sh --clean
```

**That's it!** 🎉 Your development environment is ready with:

- ✅ **Backend API** at http://localhost:8000 (with live docs at `/docs`)
- ✅ **Frontend** at http://localhost:5173 (with hot reload)
- ✅ **PostgreSQL** database ready with sample users
- ✅ **System monitoring** dashboard with real-time metrics

### 🔧 Script Permissions (First Time Setup)

After cloning, make sure all scripts are executable:

```bash
# Make all scripts executable
chmod +x scripts/*.sh

# Verify permissions (should show -rwxr-xr-x)
ls -la scripts/*.sh
```

**Available Scripts:**
- `./scripts/setup.sh` - Complete development setup
- `./scripts/cleanup.sh` - Clean environment
- `./scripts/fix-postgres-startup.sh` - Fix PostgreSQL issues  
- `./scripts/diagnose-postgres.sh` - PostgreSQL diagnostics

### Development Login Credentials
| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@example.com | password123 |
| **Instructor** | instructor@example.com | password123 |
| **Student** | student@example.com | password123 |

For detailed setup instructions, see [Setup Guide](docs/SETUP.md).

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[📋 Setup Guide](docs/SETUP.md)** | Complete installation, development workflow, and troubleshooting |
| **[✨ Features & Architecture](docs/FEATURES.md)** | System features and technical architecture |
| **[🔧 Backend Guide](docs/BACKEND.md)** | FastAPI backend with new monitoring APIs |
| **[⚛️ Frontend Guide](docs/FRONTEND.md)** | React frontend development |
| **[🗄️ Database Guide](docs/DATABASE.md)** | PostgreSQL setup and performance monitoring |
| **[🔐 Auth Flows](docs/AUTH_FLOWS.md)** | Authentication and authorization system |

### Development Resources
- **[Sprint Planning](docs/development/sprints/)** - Feature development roadmap

## 🎯 Current Status

### ✅ Production Ready Features

#### 🔐 Authentication & User Management
- **JWT-based authentication** with access/refresh token system
- **Role-based access control** (Admin, Instructor, Student)
- **Session management** with device tracking and revocation
- **User profile management** with session statistics
- **Secure password hashing** using bcrypt

#### 📊 System Monitoring Suite ✨ **NEW**
- **Real-time system metrics**: CPU, memory, disk, network usage
- **Docker container monitoring**: Container stats, health, and resource usage
- **Database performance monitoring**: Query performance, connection pool stats
- **Live log streaming**: Real-time log viewing with Server-Sent Events
- **Health checks**: Comprehensive system health dashboard

#### 🗄️ Database Performance Monitoring ✨ **NEW**
- **Connection pool monitoring**: Real-time pool utilization and health
- **Query performance analysis**: Slow query detection and optimization
- **Table statistics**: Size monitoring, row counts, and bloat detection
- **Index usage tracking**: Performance optimization recommendations
- **Automated health checks**: Database connectivity and performance alerts

#### 🎨 Modern Frontend
- **React 18** with TypeScript and modern hooks
- **TailwindCSS** for responsive, utility-first styling  
- **React Router** for seamless navigation
- **Real-time monitoring dashboard** with live metrics
- **Responsive design** optimized for desktop and mobile

#### 🏗️ Infrastructure & DevOps
- **Docker containerization** with multi-stage builds
- **PostgreSQL 16** with async connection pooling
- **Centralized configuration management** via JSON config
- **Hot reload development** for frontend and backend
- **Comprehensive test suites** with async support
- **Development Environment**: Complete Docker setup with hot reload
- **Code Quality**: Type-safe backend & frontend with comprehensive testing

### 🚧 In Development  
- **Course Management**: Content creation and student enrollment
- **AI Content Generation**: Automated course and assessment creation
- **Learning Analytics**: Progress tracking and performance insights

### 🔜 Coming Soon
- **Payment Integration**: Stripe/PayPal course purchases
- **AI Tutor Bot**: 24/7 intelligent learning assistance
- **Mobile App**: Native iOS and Android applications

## 🛠 Technology Stack

### Backend
- **FastAPI** - High-performance async Python framework
- **PostgreSQL** - Primary database with full ACID compliance  
- **Neo4j** - Graph database for learning relationships
- **SQLAlchemy 2.0** - Modern async ORM with type safety
- **JWT** - Secure authentication and authorization

### Frontend
- **React 18** - Modern component-based UI framework
- **TypeScript** - Type-safe JavaScript development
- **TailwindCSS** - Utility-first styling framework
- **Vite** - Fast build tool and development server

### Infrastructure
- **Docker** - Containerized development and deployment
- **Redis** - Caching and session management
- **GitHub Actions** - Automated CI/CD pipeline

## 👥 Contributing

We welcome contributions! Please see our [Setup Guide](docs/SETUP.md) for:
- Coding standards and best practices
- Development workflow and git conventions
- Testing requirements and guidelines

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/mehrdad-zade/x-university-2/issues)
- **Documentation**: Comprehensive guides in the `docs/` folder
- **Development Help**: See [Setup Guide](docs/SETUP.md)

---

**Ready to revolutionize education?** Start with our [Setup Guide](docs/SETUP.md) and join the future of learning! 🚀
