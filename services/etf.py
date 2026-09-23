import yfinance as yf


class ETFQueryError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def get_etfs(region: str, page: int = 1, pagesize: int = 100, ticker: str = "") -> dict:
    offset = (page - 1) * pagesize
    region = region.lower()
    query = yf.ETFQuery("eq", ["region", region])
    # Yahoo's region values correspond to the country keys in its exchange map.
    if region not in query.valid_values["exchange"]:
        raise ETFQueryError(f"Unsupported region: {region}", 422)
    ticker = ticker.strip().upper()
    if ticker:
        query = yf.ETFQuery("and", [query, yf.ETFQuery("eq", ["ticker", ticker])])
    try:
        result = yf.screen(query, offset=offset, size=pagesize, sortField="ticker", sortAsc=True)
    except Exception as exc:
        raise ETFQueryError("Yahoo Finance ETF screening is currently unavailable") from exc
    if not isinstance(result, dict) or not isinstance(result.get("quotes"), list):
        raise ETFQueryError("Yahoo Finance returned an invalid ETF response")
    total = result.get("total")
    items = result["quotes"]
    if isinstance(total, bool) or not isinstance(total, int) or total < 0 or not all(isinstance(item, dict) for item in items):
        raise ETFQueryError("Yahoo Finance returned an invalid ETF response")
    return {
        "region": region,
        "page": page,
        "pagesize": pagesize,
        "count": len(items),
        "total": total,
        "hasMore": offset + len(items) < total,
        "items": [{key: item.get(key) for key in (
            "symbol", "shortName", "longName", "exchange", "fullExchangeName",
            "currency", "regularMarketPrice", "regularMarketTime",
        )} for item in items],
    }
