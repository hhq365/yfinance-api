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
    dexscreener_price_cache_seconds: int = Field(default=30, ge=0)
    dexscreener_token_addresses: dict[str, dict[str, str]] = Field(default_factory=lambda: {
        "ethereum": {"USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7"},
        "bsc": {"USDT": "0x55d398326f99059ff775485246999027b3197955"},
        "solana": {"USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"},
        "tron": {"USDT": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"},
        "arbitrum": {
            "USDT": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
            "USDT0": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
        },
    })

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()
