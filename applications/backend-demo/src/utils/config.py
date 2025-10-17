"""Application configuration using Pydantic settings"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "Backend Demo API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 1

    # Logging
    log_level: str = "info"

    # CORS
    cors_origins: List[str] = ["*"]

    # Features
    enable_docs: bool = True
    enable_metrics: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()
