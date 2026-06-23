# app/core/config.py
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Consultation App"
    
    # Updated to validation_alias for modern Pydantic v2 settings management
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    secret_key: str = Field(..., validation_alias="SECRET_KEY")
    frontend_url: str = Field(..., validation_alias="FRONTEND_URL")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 🚀 Crucial validation fix for Render / Cloud deployments
    @field_validator("database_url", mode="before")
    @classmethod
    def fix_postgres_protocol(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore" # Prevents validation crashes if extra parameters exist in Render envs
    )


settings = Settings()