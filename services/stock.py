from datetime import datetime, timezone
from typing import List

import pandas as pd
import yfinance as yf
from cachetools import TTLCache, cached

from models.stock import StockData
from utils.safe_dict import safe_get
from utils.markets import build_symbol
from utils.currency import convert_price
from utils.currency import guess_currency


def get_stocks_by_tickers(tickers: List[str], markets: List[str]) -> dict[str, StockData | None]:
    results: dict[str, StockData | None] = {}

    # 如果 markets 长度为1，自动扩展
    if len(markets) == 1:
        markets = markets * len(tickers)

    # 构建 yahoo_symbol 映射表
    symbol_map = {t: build_symbol(t, m)[0] for t, m in zip(tickers, markets)}

    # 批量获取数据
    yahoo_symbols = list(symbol_map.values())
    stocks_data = get_stocks_by_symbols(yahoo_symbols)  # 返回 dict[symbol, StockData | None]

    for ticker, market in zip(tickers, markets):
        yahoo_symbol = symbol_map[ticker]
        stock = stocks_data.get(yahoo_symbol)
        key = f"{market}-{ticker}"
        if stock:
            # 补回原始 ticker 和 market
            stock.ticker = ticker
            stock.market = market
            results[key] = stock
        else:
            results[key] = None
    return results


def get_stocks_by_symbols(symbols: List[str]) -> dict[str, StockData | None]:
    results: dict[str, StockData | None] = {}
    tickers_obj = yf.Tickers(" ".join(symbols))

    for yahoo_symbol in symbols:
        try:
            tk = tickers_obj.tickers.get(yahoo_symbol)
            if not tk:
                results[yahoo_symbol] = None
                continue

            info = getattr(tk, "info", {}) or {}
            fi = getattr(tk, "fast_info", {}) or {}

            ts = info.get("regularMarketTime") or fi.get("last_trade_time")
            dt_str = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else None

            stockData = StockData(
                symbol=yahoo_symbol,
                short_name=info.get("shortName") or fi.get("shortName"),
                long_name=info.get("longName") or fi.get("longName"),
                price=fi.get("last_price") or info.get("regularMarketPrice"),
                previous_close=fi.get("previous_close") or info.get("previousClose"),
                open=fi.get("open") or info.get("open"),
                high=fi.get("day_high") or info.get("dayHigh"),
                low=fi.get("day_low") or info.get("dayLow"),
                volume=fi.get("volume") or info.get("volume"),
                currency=fi.get("currency") or info.get("currency"),
                data_time=dt_str
            )
            stockData.price_usd, stockData.rate_to_usd = convert_price(stockData.price, stockData.currency)
            results[yahoo_symbol] = stockData

        except Exception as e:
            print(f"error for {yahoo_symbol}: {e}")
            results[yahoo_symbol] = None

    return results
