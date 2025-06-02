"""
Application settings and configuration management.
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_secure_random_secret_key_here")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS and Security
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://your-production-domain.com"]
    ALLOWED_HOSTS: List[str] = ["*"]

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/space_db")
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Redis Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Plugin Settings
    PLUGIN_DIR: str = "plugins"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/api.log")
    
    # MCP Settings
    MCP_VERSION: str = "1.0"
    MCP_ENABLED: bool = True
    
    # Monitoring
    PROMETHEUS_METRICS: bool = True
    HEALTH_CHECK_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
