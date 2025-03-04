import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv


class Settings(BaseSettings):
    project_name: str = "Cycle Tracker"
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    secret_key: str
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./cycle_tracker.db"
    async_database_url: str = database_url.replace("sqlite:", "sqlite+aiosqlite:")

    model_config = SettingsConfigDict()


@lru_cache()
def get_settings():
    # Dynamically determine the correct env file
    env_file_map = {
        "development": "dev.env",
        "testing": "test.env",
        "production": ".env",
    }
    app_env = os.getenv("APP_ENV", "production")  # Default to production
    env_file = env_file_map.get(app_env, ".env")

    # Load the correct environment file
    print(f"Loading environment: {app_env}, File: {env_file}")
    load_dotenv(env_file, override=True)  # Force correct env variables
    return Settings(_env_file=env_file)
