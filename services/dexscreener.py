from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from threading import RLock
from urllib.parse import quote

import requests
from cachetools import TTLCache, cached

from config import get_settings
from utils.currency import convert_price

settings = get_settings()
price_cache = TTLCache(maxsize=256, ttl=settings.dexscreener_price_cache_seconds)
price_cache_lock = RLock()


class DexScreenerError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def _positive_number(value):
    try:
        number = Decimal(str(value))
        if number.is_finite() and number > 0 and number <= Decimal("1e100"):
            return number
    except (InvalidOperation, ValueError):
        pass
    return None


def _object(value):
    return value if isinstance(value, dict) else {}


def get_dexscreener_price(chain: str, symbol: str) -> dict:
    chain, symbol = chain.lower(), symbol.upper()
    address = settings.dexscreener_token_addresses.get(chain, {}).get(symbol)
    if not address:
        raise DexScreenerError(f"Unsupported chain/symbol: {chain}/{symbol}", 404)
    return _get_price_cached(chain, symbol, address)


@cached(price_cache, lock=price_cache_lock)
def _get_price_cached(chain: str, symbol: str, address: str) -> dict:
    url = f"https://api.dexscreener.com/token-pairs/v1/{quote(chain, safe='')}/{quote(address, safe='')}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        pairs = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise DexScreenerError("DexScreener is unavailable or returned an invalid response") from exc
    if not isinstance(pairs, list):
        raise DexScreenerError("DexScreener returned an invalid response")

    candidates = []
    for pair in pairs:
        if not isinstance(pair, dict) or pair.get("chainId") != chain:
            continue
        base_address = _object(pair.get("baseToken")).get("address")
        if not isinstance(base_address, str):
            continue
        # EVM addresses are case-insensitive; Solana and Tron addresses are not.
        matches = base_address.lower() == address.lower() if address.startswith("0x") else base_address == address
        price = _positive_number(pair.get("priceUsd"))
        liquidity = _positive_number(_object(pair.get("liquidity")).get("usd"))
        volume = _positive_number(_object(pair.get("volume")).get("h24"))
        if matches and price is not None and liquidity is not None and volume is not None:
            candidates.append((liquidity, volume, price, pair))
    if not candidates:
        raise DexScreenerError(f"No usable base-token price found for {chain}/{symbol}", 404)

    liquidity, volume, price_usd, pair = max(candidates, key=lambda item: (item[0], item[1]))
    price_hkd, rate = convert_price(price_usd, "USD", "HKD")
    if _positive_number(price_hkd) is None or _positive_number(rate) is None:
        raise DexScreenerError("USD to HKD conversion is unavailable")
    return {
        "chain": chain,
        "symbol": symbol,
        "tokenSymbol": pair["baseToken"].get("symbol"),
        "tokenAddress": address,
        "priceUSD": float(price_usd),
        "priceHKD": float(price_hkd),
        "usdToHkdRate": float(rate),
        "fxRateSource": "Frankfurter",
        "source": "DexScreener",
        "dexId": pair.get("dexId"),
        "pairAddress": pair.get("pairAddress"),
        "liquidityUSD": float(liquidity),
        "volume24hUSD": float(volume),
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
    }
