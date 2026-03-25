def build_symbol(ticker: str, market: str) -> tuple[str, str]:
    """
    返回 (yahoo_symbol, original_ticker)
    """
    market = market.upper()
    original = ticker
    if market in ["NASDAQ", "NYSE", "US"]:
        return ticker, original
    elif market == "HK":
        # 港股去掉前导0，但至少保留4位，不足补0
        num = ticker.lstrip("0")
        num = num if num else "0"
        num = num.zfill(4)
        return f"{num}.HK", original
    elif market == "SS":
        return f"{ticker}.SS", original
    elif market == "SZ":
        return f"{ticker}.SZ", original
    elif market == "JP":
        return f"{ticker}.T", original
    elif market == "LSE":
        return f"{ticker}.L", original
    elif market == "TO":
        return f"{ticker}.TO", original
    else:
        return ticker, original