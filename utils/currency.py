from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional
import yfinance as yf
from cachetools import TTLCache, cached


def guess_currency(symbol: str):
    if symbol.endswith(".HK"):
        return "HKD"
    if symbol.endswith(".T"):
        return "JPY"
    if symbol.endswith(".SS") or symbol.endswith(".SZ"):
        return "CNY"
    return "USD"


def convert_price(
        price: Optional[float],
        from_currency: Optional[str],
        to_currency: str = "USD",
        ts: Optional[int] = None
) -> Optional[float]:
    if price is None or from_currency is None:
        return None
    if price == 0:
        return 0
    if from_currency == "HKD" and to_currency == "USD":
        return price * 0.128
    if from_currency == "USD" and to_currency == "HKD":
        return price * 7.85

    rate = get_fx_rate(from_currency, to_currency, ts)
    if rate is None:
        return None
    return price * rate


currencyRateCache = TTLCache(maxsize=128, ttl=3600)


@cached(currencyRateCache)
def get_fx_rate(
        from_currency: str,
        to_currency: str,
        ts: Optional[int] = None  # UNIX timestamp
) -> Optional[float]:
    """
    获取汇率
    :param from_currency: 原货币，如 HKD
    :param to_currency: 目标货币，如 USD
    :param ts: 时间戳（秒），可选
    :return: 汇率（float）或 None
    """

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    # ✅ 1. 同币种
    if from_currency == to_currency:
        return 1.0

    pair = f"{from_currency}{to_currency}=X"

    try:
        fx = yf.Ticker(pair)

        # ✅ 2. 没传时间 → 用最新
        if ts is None:
            fi = getattr(fx, "fast_info", {}) or {}
            rate = fi.get("last_price")

            if rate:
                return float(rate)

            # fallback
            info = getattr(fx, "info", {}) or {}
            return info.get("regularMarketPrice")

        # ✅ 3. 传了时间 → 用 history
        dt = datetime.utcfromtimestamp(ts)

        # yfinance 限制：分钟级最多7天
        now = datetime.utcnow()
        if (now - dt) > timedelta(days=7):
            # fallback 最新
            fi = getattr(fx, "fast_info", {}) or {}
            return fi.get("last_price")

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

        return float(nearest["Close"])

    except Exception:
        return None
