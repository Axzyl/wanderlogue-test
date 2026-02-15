from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

# Find .env file - check backend folder first, then parent folder
def find_env_file():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_env = os.path.join(current_dir, ".env")
    parent_env = os.path.join(os.path.dirname(current_dir), ".env")

    if os.path.exists(local_env):
        return local_env
    elif os.path.exists(parent_env):
        return parent_env
    return ".env"


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str

    # Clerk
    clerk_secret_key: str
    clerk_publishable_key: str

    # Database (SQLite for local testing, PostgreSQL for production)
    database_url: str = "sqlite:///./photo_memory.db"

    # App settings
    backend_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore VITE_* and other frontend variables
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
