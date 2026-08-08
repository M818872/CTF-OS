from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CTF-OS"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="CTF_OS_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
