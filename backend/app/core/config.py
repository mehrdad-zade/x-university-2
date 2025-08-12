"""
Configuration Management for X University API

This module manages all application configuration using Pydantic Settings,
providing type-safe environment variable handling with validation and documentation.

Environment variables are loaded from:
1. System environment variables
2. .env files (if present)

The configuration is validated at startup and provides sensible defaults
for development while requiring explicit configuration for production.

Key features:
- Type-safe configuration with validation
- Automatic environment variable parsing
- Production-ready security defaults  
- Comprehensive database and external service configuration
- CORS origin validation and parsing

Author: X University Development Team
Created: 2025
"""

from typing import Any, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, ConfigDict


class Settings(BaseSettings):
    """
    Application settings configuration class.
    
    This class defines all configuration settings for the X University API,
    loading values from environment variables with appropriate defaults and validation.
    
    Settings are organized by category:
    - Application: Basic app configuration
    - Database: PostgreSQL and Neo4j connections  
    - Security: JWT tokens and authentication
    - External APIs: Third-party service integrations
    - Development: Debug and development settings
    """
    
    # ========================================
    # APPLICATION SETTINGS
    # ========================================
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production-minimum-32-chars"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    API_PORT: int = 8000
    
    # ========================================
    # DATABASE CONFIGURATION
    # ========================================
    DATABASE_URL: str = "postgresql+psycopg://dev:devpass@localhost:5432/xu2"
    
    # Neo4j configuration (optional for learning graph features)
    ENABLE_NEO4J: bool = False
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "devpass"
    
    # ========================================
    # JWT AUTHENTICATION SETTINGS
    # ========================================
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRES_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # ========================================
    # EXTERNAL API INTEGRATIONS
    # ========================================
    # OpenAI for AI-powered content generation
    OPENAI_API_KEY: str = ""
    
    # Payment processing integrations
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    PAYPAL_CLIENT_ID: str = ""
    PAYPAL_CLIENT_SECRET: str = ""

    @field_validator("ALLOWED_ORIGINS", mode='before')
    def validate_cors_origins(cls, value: Any) -> Union[list[str], str]:
        """
        Validate and parse CORS origins configuration.
        
        Accepts either:
        - A comma-separated string of origins: "http://localhost:3000,https://app.example.com"
        - A list of origin strings: ["http://localhost:3000", "https://app.example.com"]
        - A single origin string: "http://localhost:3000"
        
        Args:
            value: The CORS origins configuration from environment
            
        Returns:
            Parsed list of allowed origins
            
        Raises:
            ValueError: If the value format is invalid
        """
        if isinstance(value, str) and not value.startswith("["):
            # Handle comma-separated string format
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        elif isinstance(value, (list, str)):
            return value
        else:
            raise ValueError(f"Invalid CORS origins format: {value}")
    
    # Pydantic v2 configuration for environment variable loading
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"  # Ignore unknown environment variables
    )
# Global settings instance - initialized once and reused throughout the application
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency function to get application settings.
    
    This function can be used as a FastAPI dependency to inject
    settings into route handlers while maintaining testability.
    
    Returns:
        Settings: The global settings instance
    """
    return settings
