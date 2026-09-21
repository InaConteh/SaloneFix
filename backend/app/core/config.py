from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "SaloneFix"
    APP_ENV: str = "development"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "sqlite:///./salonefix.db"
    STORAGE_DIR: str = "./media_storage"

    JWT_SECRET: str = "development_jwt_secret_key_minimum_32_characters_for_salonefix"
    SESSION_SECRET: str = "development_session_secret_salonefix_prototype"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Future integration flags / placeholders (safe defaults)
    AI_ENABLED: bool = False
    AI_API_KEY: str | None = None
    AI_BASE_URL: str | None = None
    WHATSAPP_ENABLED: bool = False
    WHATSAPP_TOKEN: str | None = None
    WHATSAPP_WEBHOOK_SECRET: str | None = None


settings = Settings()
