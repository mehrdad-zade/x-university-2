"""
Backend constants loaded from centralized development configuration.
This file provides Python-friendly access to the common dev.config.json.
"""
import json
from pathlib import Path
from typing import Dict, Any

# Load config once when module is imported
# Try multiple potential locations for the config file
_POTENTIAL_CONFIG_PATHS = [
    Path(__file__).parent / "dev.config.json",  # In container: /app/dev.config.json
    Path(__file__).parent.parent / "infra" / "dev.config.json",  # Host: ../infra/dev.config.json
]

_CONFIG: Dict[str, Any] = None
for _CONFIG_PATH in _POTENTIAL_CONFIG_PATHS:
    try:
        with open(_CONFIG_PATH, 'r') as f:
            _CONFIG = json.load(f)
        break
    except FileNotFoundError:
        continue

if _CONFIG is None:
    raise FileNotFoundError(f"Development config not found at any of: {[str(p) for p in _POTENTIAL_CONFIG_PATHS]}")

# =============================================================================
# URLs & ENDPOINTS
# =============================================================================
class URLs:
    FRONTEND = _CONFIG["urls"]["frontend"]
    BACKEND = _CONFIG["urls"]["backend"] 
    API_BASE = _CONFIG["urls"]["api_base"]
    HEALTH_CHECK = _CONFIG["urls"]["health_check"]
    API_DOCS = _CONFIG["urls"]["api_docs"]
    
    class Auth:
        LOGIN = _CONFIG["endpoints"]["auth"]["login"]
        REGISTER = _CONFIG["endpoints"]["auth"]["register"]
        LOGOUT = _CONFIG["endpoints"]["auth"]["logout"]
        REFRESH = _CONFIG["endpoints"]["auth"]["refresh"]
        ME = _CONFIG["endpoints"]["auth"]["me"]
    
    class Monitor:
        BASE = _CONFIG["endpoints"]["monitor"]["base"]
        DATABASE = _CONFIG["endpoints"]["monitor"]["database"]
        LOGS = _CONFIG["endpoints"]["monitor"]["logs"]
        DOCKER = _CONFIG["endpoints"]["monitor"]["docker"]

# =============================================================================
# DEVELOPMENT CREDENTIALS
# =============================================================================
class DevCredentials:
    PASSWORD = _CONFIG["credentials"]["default_password"]
    
    ADMIN_EMAIL = _CONFIG["credentials"]["users"]["admin"]["email"]
    ADMIN_NAME = _CONFIG["credentials"]["users"]["admin"]["full_name"]
    
    INSTRUCTOR_EMAIL = _CONFIG["credentials"]["users"]["instructor"]["email"] 
    INSTRUCTOR_NAME = _CONFIG["credentials"]["users"]["instructor"]["full_name"]
    
    STUDENT_EMAIL = _CONFIG["credentials"]["users"]["student"]["email"]
    STUDENT_NAME = _CONFIG["credentials"]["users"]["student"]["full_name"]

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
class Database:
    NAME = _CONFIG["database"]["name"]
    TEST_NAME = _CONFIG["database"]["test_name"]
    USER = _CONFIG["database"]["user"]
    PASSWORD = _CONFIG["database"]["password"]
    HOST = _CONFIG["database"]["host"]
    PORT = _CONFIG["database"]["port"]

# =============================================================================
# MESSAGES
# =============================================================================
class Messages:
    # Database messages
    DB_CONNECTION_SUCCESS = _CONFIG["messages"]["database"]["connection_success"]
    DB_MIGRATION_SUCCESS = _CONFIG["messages"]["database"]["migration_success"]
    DB_USERS_CREATED = _CONFIG["messages"]["database"]["users_created"]
    DB_USERS_EXIST = _CONFIG["messages"]["database"]["users_exist"]
    
    # Auth messages
    LOGIN_SUCCESS = _CONFIG["messages"]["auth"]["login_success"]
    LOGIN_FAILED = _CONFIG["messages"]["auth"]["login_failed"]
    LOGIN_CREDENTIALS_INFO = _CONFIG["messages"]["auth"]["credentials_info"]
    
    # Setup messages
    DATABASE_SETUP = _CONFIG["messages"]["setup"]["database_setup"]
    SETUP_COMPLETE = _CONFIG["messages"]["setup"]["setup_complete"]

# =============================================================================
# DOCKER CONFIGURATION  
# =============================================================================
class Docker:
    POSTGRES_CONTAINER = _CONFIG["docker"]["containers"]["postgres"]
    BACKEND_CONTAINER = _CONFIG["docker"]["containers"]["backend"]
    FRONTEND_CONTAINER = _CONFIG["docker"]["containers"]["frontend"]
    PROJECT_NAME = _CONFIG["docker"]["project_name"]
    COMPOSE_FILE = _CONFIG["docker"]["compose_file"]

# =============================================================================
# TIMEOUTS
# =============================================================================
class Timeouts:
    DOCKER_START = _CONFIG["timeouts"]["docker_start"]
    SERVICE_HEALTH = _CONFIG["timeouts"]["service_health"]
    HEALTH_CHECK_INTERVAL = _CONFIG["timeouts"]["health_check_interval"]
    CONNECTION_RETRY = _CONFIG["timeouts"]["connection_retry"]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_user_credentials(role: str) -> dict:
    """Get user credentials for a given role."""
    if role.lower() in _CONFIG["credentials"]["users"]:
        user = _CONFIG["credentials"]["users"][role.lower()]
        return {
            "email": user["email"],
            "password": _CONFIG["credentials"]["default_password"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    return {}

def get_full_url(endpoint: str) -> str:
    """Convert a relative endpoint to a full URL."""
    if endpoint.startswith('http'):
        return endpoint
    return URLs.BACKEND + endpoint

def get_api_url(endpoint: str) -> str:
    """Convert a relative API endpoint to a full API URL."""
    if endpoint.startswith('http'):
        return endpoint
    if endpoint.startswith('/api/v1/'):
        return URLs.BACKEND + endpoint
    return URLs.API_BASE + endpoint
