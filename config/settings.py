"""Application settings and configuration management."""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    supabase_url: str
    supabase_key: str
    google_api_key: str
    environment: str = "production"
    backend_url: Optional[str] = None  # Backend URL for CORS and self-reference
    
    # API Configuration
    api_title: str = "Nemo AI Assistant API"
    api_version: str = "1.0.0"
    api_description: str = "Backend API for Nemo, the AI assistant for club management"
    
    # CORS Settings
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080","https://snucpotentialclub.vercel.app"]
    
    # WebSocket Configuration
    ws_heartbeat_interval: int = 30  # seconds
    ws_timeout: int = 300  # 5 minutes
    
    # Rate Limiting
    max_requests_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create singleton instance
settings = Settings()
