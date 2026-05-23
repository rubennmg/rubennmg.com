from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    service_name: str = Field(default="rubennmg-api", alias="SERVICE_NAME")
    database_url: str = Field(
        default="postgresql+psycopg://rubennmg:change-me@localhost:5432/rubennmg_staging",
        alias="DATABASE_URL",
    )
    cors_allowed_origins: str = Field(default="", alias="CORS_ALLOWED_ORIGINS")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
