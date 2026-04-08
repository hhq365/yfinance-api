# yfinance API

## Overview
This repository is a FastAPI application for accessing and utilizing the `yfinance` library to fetch financial data from Yahoo Finance. The API provides multiple endpoints to query stock data easily.

## Routes
- **`/api/yfinance/stocks/xxx`**: Fetch stock data for multiple specified symbols.
- **`/api/yfinance/market/xxx`**: Get market status data for a stock market.
- **`/api/yfinance/currency/xxx`**: Get exchange rate between specified two currency.

## Configuration
You can configure the FastAPI application by create the `.env` file. The configuration settings include:
- `APP_NAME`: name the FastAPI application (default is `yfinance api`).
- `API_KEY_ENABLED`: if enable authorization access or not (default is false).
- `API_KEYS`: access api keys (default is []).
- `ALLOW_ORIGINS`: allow origins of response header (default is [`*`]).

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





