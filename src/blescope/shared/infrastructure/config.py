from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application configuration settings."""
    app_name: str = "Bluetooth Scanner/Jammer API"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # logging
    log_level: str = "DEBUG"

    # Bluetooth settings
    scan_timeout: int = 10  # seconds
    connection_timeout: int = 30  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
