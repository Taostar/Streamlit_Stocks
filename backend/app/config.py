from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # External API configuration
    EXTERNAL_API_URL: str = "https://99c0edf47989.ngrok-free.app"

    # Cache TTL values (in seconds)
    CACHE_TTL_HOLDINGS: int = 300  # 5 minutes
    CACHE_TTL_PERFORMANCE: int = 3600  # 1 hour
    CACHE_TTL_CORRELATION: int = 3600  # 1 hour
    CACHE_TTL_EXCHANGE: int = 86400  # 1 day
    CACHE_TTL_BENCHMARK: int = 86400  # 1 day

    # CORS configuration
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    # API configuration
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
