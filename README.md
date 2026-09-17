# yfinance API

## Overview
This repository is a FastAPI application for accessing and utilizing the `yfinance` library to fetch financial data from Yahoo Finance. The API provides multiple endpoints to query stock data easily.

## Routes
- **`/api/frankfurter/rate/{base}/{quote}`**: Latest available Frankfurter reference exchange rate, with a 5-minute server cache. Currency codes are case-insensitive, e.g. `/api/frankfurter/rate/USD/HKD` or `/api/frankfurter/rate/EUR/JPY`.
- **`/api/yfinance/stocks/xxx`**: Fetch stock data for multiple tickers of markets or symbols.
- **`/api/yfinance/market/xxx`**: Get market status and office-time for specified stock market.
- **`/api/yfinance/currency/xxx`**: Get exchange rate between two currency.
- **`/api/gold-api/price/{symbol}`**: Get a Gold API price in USD; weight-based assets also include a price per gram.
- **`/api/gold-api/price/{symbol}/{currency}`**: Get the same price in a specified currency (for example, `CNY`).
- **`/api/dexscreener/price/{chain}/{symbol}`**: Get a chain-specific DEX reference price with numeric `priceUSD` and `priceHKD` fields.

### Frankfurter exchange rates

Example response for `GET /api/frankfurter/rate/USD/HKD` (illustrative):

```json
{"code":0,"message":"success","data":{"base":"USD","quote":"HKD","rate":7.8515,"date":"2026-09-17","source":"Frankfurter"}}
```

`rate` is the amount of quote currency per one unit of base currency; `date` is
the upstream rate date, not the request time. This is the latest available reference
rate, not a tick-by-tick real-time quote. Successful results are cached per pair
for 300 seconds; USD/HKD shares its cache with existing price conversions.
Unsupported currencies return HTTP 404, malformed currency codes HTTP 422,
and upstream failures/invalid responses HTTP 502. Failures are not cached.
The existing application API-key policy applies. Historical queries remain on
the existing `/api/yfinance/currency/rate` endpoint.

### DexScreener prices

Example: `GET /api/dexscreener/price/bsc/USDT` (chain and symbol are case-insensitive).
The response uses the existing `{code, message, data}` envelope. `data` includes
`priceUSD`, `priceHKD`, `usdToHkdRate`, `fxRateSource`, `tokenAddress`, `tokenSymbol`,
`dexId`, `pairAddress`, `liquidityUSD`, `volume24hUSD`, and `fetchedAt` (UTC fetch time,
not the time of the last trade).

Defaults support USDT on `ethereum`, `bsc`, `solana`, `tron`, and `arbitrum`.
On Arbitrum, `USDT` and `USDT0` resolve to the same USD₮0 contract; `tokenSymbol`
preserves the upstream name. Token versions on different chains are not necessarily
equivalent to native Tether issuance.

Symbols resolve through configured contract addresses, never a name search.
Among returned pools on the requested chain with the target contract as base token,
a positive finite USD price, positive liquidity and positive 24-hour volume,
the service selects the highest USD liquidity (24-hour volume breaks ties).
This is a single-pool reference price, not an official Tether or chain-wide price;
low activity and incomplete upstream pool coverage can affect its usefulness.
HKD uses the latest available USD/HKD reference rate from
`https://api.frankfurter.dev/v2/rate/USD/HKD`; `fxRateSource` is `Frankfurter`.
The FX rate is cached for **5 minutes**; HKD to USD uses its reciprocal and shares
the same cache. This applies to current stock conversions and the currency-rate
endpoint too. Explicit historical timestamps retain the Yahoo Finance path.
Failed FX requests are not cached and do not fall back to a fixed rate.
Frankfurter reference rates are not tick-by-tick market quotes.
Successful DexScreener results are cached server-side for 30 seconds.
Unsupported chain/symbol or no usable pool returns HTTP 404; upstream failures return
HTTP 502. Errors use the existing error envelope and are not cached. Existing API-key
authentication applies to this route too.

## Configuration
You can configure the FastAPI application by create the `.env` file. The configuration settings include:
- `APP_NAME`: name the FastAPI application (default is `yfinance api`).
- `API_KEY_ENABLED`: if enable authorization access or not (default is `false`).
- `API_KEYS`: assignable api keys (default is `[]`).
- `ALLOW_ORIGINS`: allow origins of response header (default is `["*"]`).
- `YFINANCE_CURRENCY_RATE_CACHE_SECONDS`: currency-rate cache duration in seconds (default is `3600`).
- `GOLD_API_PRICE_CACHE_SECONDS`: Gold API price cache duration in seconds (default is `30`).
- `DEXSCREENER_PRICE_CACHE_SECONDS`: DexScreener price cache duration in seconds (default is `30`; `0` disables caching).
- `DEXSCREENER_TOKEN_ADDRESSES`: JSON mapping of lowercase chain IDs to uppercase symbols and contract addresses. Replaces the default map, e.g. `{"ethereum":{"USDC":"0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"}}`; include every chain/symbol you want to support. Only configure trusted contract addresses.

## Installation
To install the necessary requirements for this FastAPI application, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/hhq365/yfinance-api.git
    cd yfinance-api
    ```
2. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage Examples
To run the FastAPI application, use:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
