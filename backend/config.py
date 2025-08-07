import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/backend_db"
    
    # LightRAG Server
    lightrag_server_url: str = "http://localhost:8020"
    lightrag_api_key: Optional[str] = None
    
    # Application
    app_name: str = "RAG System Backend"
    debug: bool = False
    cors_origins: list = ["http://localhost:3000"]
    
    # File Storage
    upload_dir: str = "./uploads"
    documents_dir: str = "./static/documents"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


# Create global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.documents_dir, exist_ok=True) 