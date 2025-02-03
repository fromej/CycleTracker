import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    project_name: str = "Cycle Tracker"
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    secret_key: str

    # Database
    database_url: str = "sqlite:///./cycle_tracker.db"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
