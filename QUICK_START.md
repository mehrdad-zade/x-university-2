# X-University Development Quick Start Guide

## 🚀 Fresh Setup (Recommended)

```bash
# Complete fresh setup - removes everything and rebuilds
make fresh
# OR
./scripts/cleanup.sh && ./setup.sh --clean
```

## ⚡ Quick Setup (Existing Environment)

```bash
# Preserves existing data
make setup
# OR  
./setup.sh
```

## 🔧 Common Development Commands

```bash
# Check system health (includes auth test)
make health

# View logs
make logs              # All services
make logs-backend      # Backend only
make logs-frontend     # Frontend only

# Restart services
make restart           # All services
make quick-restart     # Just backend/frontend

# Database management
make db-init           # Initialize with default users
make db-reset          # ⚠️  Destroys all data!

# Testing
make test              # Run all tests
make health            # Test authentication
```

## 🆘 Troubleshooting

### Issue: Authentication fails / "401 Unauthorized"
```bash
make db-init           # Recreate default users
make health            # Verify authentication works
```

### Issue: Services won't start / Container conflicts
```bash
make fresh             # Nuclear option - complete reset
```

### Issue: Database connection problems
```bash
make logs-db           # Check database logs
make db-reset          # Last resort (destroys data)
```

### Issue: Backend API not responding
```bash
make logs-backend      # Check backend logs
make quick-restart     # Restart main services
```

## 👥 Default User Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| Instructor | instructor@example.com | instructor123 |
| Student | student@example.com | student123 |

## 🌐 Service URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

## 📋 Complete Command Reference

```bash
make help              # Show all available commands
make setup             # Standard setup
make fresh             # Complete fresh setup
make status            # Show service status
make health            # Comprehensive health check
make info              # Project information
make troubleshoot      # Troubleshooting guide
make open              # Open URLs in browser
```

## 🔄 Development Workflow

1. **Start working**: `make setup` or `make fresh` (first time)
2. **Check health**: `make health` 
3. **Make changes**: Edit code
4. **Quick test**: `make quick-test` (backend) or `make test`
5. **View logs**: `make logs-backend` or `make logs-frontend`
6. **Restart if needed**: `make quick-restart`
7. **Full reset if broken**: `make fresh`

## ⚠️  Important Notes

- **Always use `make fresh`** for a guaranteed clean setup
- **Check `make health`** to verify authentication is working
- **Use `make troubleshoot`** when things go wrong
- **Database password changes require `make db-init`**
- **Container naming conflicts are resolved by `make fresh`**

## 🎯 Quick Health Check

```bash
make health
```

This will test:
✅ Backend API  
✅ Authentication system  
✅ Database connectivity  
✅ User account creation  

If any fail, try `make db-init` first, then `make fresh` as last resort.
