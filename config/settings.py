from dotenv import load_dotenv
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class Settings(BaseSettings):
    # Database
    database_url: str = Field(description="PostgreSQL async connection URL")

    # Security
    secret_key: str = Field(description="Secret key for JWT signing")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24)
    jwt_refresh_expiration_days: int = Field(default=7)
    debug: bool = Field(default=False)
    env: str = Field(default="development")
    supabase_url: str | None = None
    supabase_key: str | None = None
    gemini_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
