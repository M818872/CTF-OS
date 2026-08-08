from functools import lru_cache

from app.core.config import Settings, get_settings


@lru_cache(maxsize=1)
def settings_dependency() -> Settings:
    return get_settings()
