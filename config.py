from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "yfinance api"
    api_key_enabled: bool = False
    api_keys: List[str] = []
    debug: bool = False
    allow_origins: List[str] = ["*"]
    yfinance_currency_rate_cache_seconds: int = Field(default=3600, ge=0)
    gold_api_price_cache_seconds: int = Field(default=30, ge=0)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()
