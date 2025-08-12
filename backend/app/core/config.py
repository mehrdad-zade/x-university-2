"""
Configuration settings for X University API.
Uses Pydantic settings with environment variable support.
"""
from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Basic app settings
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production-minimum-32-chars"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Database settings
    DATABASE_URL: str = "postgresql+psycopg://dev:devpass@localhost:5432/xu2"
    
    # Neo4j settings (optional)
    ENABLE_NEO4J: bool = False
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "devpass"
    
    # JWT settings
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRES_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # External API keys
    OPENAI_API_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    PAYPAL_CLIENT_ID: str = ""
    PAYPAL_CLIENT_SECRET: str = ""
    
    # API settings
    API_PORT: int = 8000

    @field_validator("ALLOWED_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Any) -> list[str] | str:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


# Global settings instance
settings = Settings()
