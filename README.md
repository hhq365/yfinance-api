# yfinance API

A FastAPI service for stock and ETF quotes, gold prices, exchange rates, and on-chain token prices.

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open [Swagger UI](http://localhost:8000/docs) for all parameters and interactive requests.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/yfinance/stocks/tickers?markets=HK&tickers=2840&tickers=3081` | Quotes by market and ticker |
| POST | `/api/yfinance/stocks/tickers` | Batch quotes; body: `[{"market":"HK","tickers":["2840","3081"]}]` |
| POST | `/api/yfinance/stocks/symbols` | Quotes by Yahoo symbol; body: `["2840.HK","GLD"]` |
| GET | `/api/yfinance/etfs?region=hk&page=1&pagesize=100` | ETFs by listing region |
| GET | `/api/yfinance/market/status?market=HK` | Market hours and status |
| GET | `/api/frankfurter/rate/USD/HKD` | Latest available reference exchange rate |
| GET | `/api/yfinance/currency/rate?from_currency=USD&to_currency=HKD` | Legacy exchange-rate endpoint; optional `ts` |
| GET | `/api/gold-api/price/XAU` | Gold price in USD, including `pricePerGram` |
| GET | `/api/gold-api/price/XAU/HKD` | Gold price in a specified currency |
| GET | `/api/dexscreener/price/bsc/USDT` | Token price in USD and HKD, with pool and liquidity data |

### ETF queries

- `region`: required listing region, e.g. `hk`, `us`, `cn`, `jp`, or `gb`.
- `page`: starts at 1; default `1`.
- `pagesize`: default `100`; maximum `250`.
- `ticker`: optional exact Yahoo symbol, e.g. `2840.HK`; empty by default. No wildcard matching.

Results include `total`, `count`, `hasMore`, and `items`. Different currency counters may appear separately. Quotes may be delayed.

### Price sources

- **Frankfurter:** cached for 5 minutes. `date` is the rate date; `fetchedAt` is the UTC fetch time and stays unchanged on cache hits. Rates are reference rates, not tick-by-tick quotes.
- **Legacy currency endpoint:** current USD/HKD conversions use Frankfurter; other pairs and historical requests use Yahoo Finance. Historical requests older than 7 days fall back to the latest rate.
- **DexScreener:** defaults to USDT on `ethereum`, `bsc`, `solana`, `tron`, and `arbitrum` (USD₮0). Selects the highest-liquidity eligible base-token pool with positive 24-hour volume. Returns `priceUSD`, `priceHKD`, `pairAddress`, and `liquidityUSD`, among other fields. HKD uses Frankfurter; this is a pool reference price, not an official Tether price.

## Configuration

Optional `.env` file:

```dotenv
API_KEY_ENABLED=false
API_KEYS=["your-api-key"]
ALLOW_ORIGINS=["*"]
YFINANCE_CURRENCY_RATE_CACHE_SECONDS=3600
GOLD_API_PRICE_CACHE_SECONDS=30
DEXSCREENER_PRICE_CACHE_SECONDS=30
```

When authentication is enabled, send the `X-API-Key` header.

To customize token contracts, set `DEXSCREENER_TOKEN_ADDRESSES` to a JSON map of chain → symbol → address. This replaces the entire default map. See [config.py](config.py) for defaults.

## Responses

Business endpoints use this envelope:

```json
{"code": 0, "message": "success", "data": {}}
```

Application errors use `code: -1`. Authentication and parameter-validation errors use FastAPI's `detail` format.
