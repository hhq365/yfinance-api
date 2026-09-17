from decimal import Decimal, InvalidOperation
from datetime import date, datetime, timedelta, timezone
import math
import re
from threading import RLock
from typing import Optional
import yfinance as yf
import requests
from cachetools import TTLCache, cached

from config import get_settings


def guess_currency(symbol: str):
    if symbol.endswith(".HK"):
        return "HKD"
    if symbol.endswith(".T"):
        return "JPY"
    if symbol.endswith(".SS") or symbol.endswith(".SZ"):
        return "CNY"
    return "USD"


def convert_price(
        price: Optional[Decimal],
        from_currency: Optional[str],
        to_currency: str = "USD",
        ts: Optional[int] = None
) -> tuple[Optional[Decimal], Optional[Decimal]]:
    if price is None or from_currency is None:
        return None, None
    rate = get_fx_rate(from_currency, to_currency, ts)
    if rate is None:
        return None, None
    return price * rate, rate


settings = get_settings()
currencyRateCache = TTLCache(
    maxsize=128,
    ttl=settings.yfinance_currency_rate_cache_seconds
)
currencyRateCacheLock = RLock()

frankfurterRateCache = TTLCache(maxsize=256, ttl=300)
frankfurterRateCacheLock = RLock()


class FrankfurterError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def get_frankfurter_rate(base: str, quote: str) -> dict:
    base, quote = base.upper(), quote.upper()
    if not re.fullmatch(r"[A-Z]{3}", base) or not re.fullmatch(r"[A-Z]{3}", quote):
        raise FrankfurterError("Currency codes must contain three letters", 422)
    try:
        return dict(_get_frankfurter_rate_cached(base, quote))
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code in (400, 404, 422):
            raise FrankfurterError(f"Unsupported currency pair: {base}/{quote}", 404) from exc
        raise FrankfurterError("Frankfurter is currently unavailable") from exc
    except (requests.RequestException, ValueError, InvalidOperation, OverflowError) as exc:
        raise FrankfurterError("Frankfurter is unavailable or returned an invalid rate") from exc


@cached(frankfurterRateCache, lock=frankfurterRateCacheLock)
def _get_frankfurter_rate_cached(base: str, quote: str) -> dict:
    # Raise on failures so cachetools never caches an unavailable/invalid rate.
    response = requests.get(f"https://api.frankfurter.dev/v2/rate/{base}/{quote}", timeout=10)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or data.get("base") != base or data.get("quote") != quote:
        raise ValueError("Invalid Frankfurter currency pair")
    rate = Decimal(str(data.get("rate")))
    if not rate.is_finite() or rate <= 0 or not math.isfinite(float(rate)) or float(rate) <= 0:
        raise ValueError("Invalid Frankfurter exchange rate")
    rate_date = data.get("date")
    if not isinstance(rate_date, str):
        raise ValueError("Missing Frankfurter rate date")
    date.fromisoformat(rate_date)
    return {
        "base": base, "quote": quote, "rate": rate, "date": rate_date,
        "source": "Frankfurter",
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
    }


def _get_frankfurter_usd_hkd() -> Decimal:
    return get_frankfurter_rate("USD", "HKD")["rate"]


def get_fx_rate(
        from_currency: str,
        to_currency: str,
        ts: Optional[int] = None  # UNIX timestamp
) -> Optional[Decimal]:
    """
    获取汇率
    :param from_currency: 原货币，如 HKD
    :param to_currency: 目标货币，如 USD
    :param ts: 时间戳（秒），可选
    :return: 汇率（Decimal）或 None
    """

    from_currency, to_currency = from_currency.upper(), to_currency.upper()
    if ts is None and {from_currency, to_currency} == {"USD", "HKD"}:
        try:
            rate = _get_frankfurter_usd_hkd()
            return rate if from_currency == "USD" else Decimal(1) / rate
        except (FrankfurterError, requests.RequestException, ValueError, InvalidOperation):
            return None
    return _get_fx_rate_cached(from_currency, to_currency, ts)


@cached(currencyRateCache, lock=currencyRateCacheLock)
def _get_fx_rate_cached(
        from_currency: str,
        to_currency: str,
        ts: Optional[int] = None
) -> Optional[Decimal]:

    # ✅ 1. 同币种
    if from_currency == to_currency:
        return Decimal(str(1.0))

    pair = f"{from_currency}{to_currency}=X"

    try:
        fx = yf.Ticker(pair)

        # ✅ 2. 没传时间 → 用最新
        if ts is None:
            fi = getattr(fx, "fast_info", {}) or {}
            rate = fi.get("last_price")
            if rate:
                return Decimal(rate)

            # fallback
            info = getattr(fx, "info", {}) or {}
            return Decimal(info.get("regularMarketPrice"))

        # ✅ 3. 传了时间 → 用 history
        dt = datetime.utcfromtimestamp(ts)

        # yfinance 限制：分钟级最多7天
        now = datetime.utcnow()
        if (now - dt) > timedelta(days=7):
            # fallback 最新
            fi = getattr(fx, "fast_info", {}) or {}
            return Decimal(fi.get("last_price"))

        df = fx.history(
            start=dt.strftime("%Y-%m-%d"),
            end=(dt + timedelta(days=1)).strftime("%Y-%m-%d"),
            interval="1m"
        )

        if df.empty:
            return None

        # ✅ 对齐时区
        if df.index.tz is not None:
            dt = dt.replace(tzinfo=df.index.tz)

        # 找最接近时间
        df["diff"] = abs(df.index - dt)
        nearest = df.sort_values("diff").iloc[0]

        return Decimal(nearest["Close"])

    except Exception:
        return None
