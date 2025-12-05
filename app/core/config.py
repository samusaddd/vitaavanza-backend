from pydantic import BaseSettings
from functools import lru_cache
from typing import List
import os

class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "VitaAvanza Backend")
    app_env: str = os.getenv("APP_ENV", "development")
    app_debug: bool = os.getenv("APP_DEBUG", "True") == "True"

    secret_key: str = os.getenv("SECRET_KEY", "CHANGE_ME")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    algorithm: str = "HS256"

    database_url: str = os.getenv("DATABASE_URL", "")
    allowed_origins: List[str] = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
