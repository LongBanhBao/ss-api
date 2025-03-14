from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    MISTRAL_API_KEY: str
    AGENT_ID: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # one week

    DATABASE_URL: str

    FRONTEND_ORIGIN: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    settings = Settings()
    return settings
