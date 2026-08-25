from typing import Any, Optional

import requests


GOLD_API_BASE_URL = "https://api.gold-api.com"
TROY_OUNCE_IN_GRAMS = 31.1034768
POUND_IN_GRAMS = 453.59237
REQUEST_TIMEOUT_SECONDS = 10

# Precious metals are quoted per troy ounce; COMEX copper (HG) is quoted per
# pound. Crypto assets do not have a weight unit and retain only `price`.
PRICE_UNIT_IN_GRAMS = {
    "XAU": TROY_OUNCE_IN_GRAMS,
    "XAG": TROY_OUNCE_IN_GRAMS,
    "XPT": TROY_OUNCE_IN_GRAMS,
    "XPD": TROY_OUNCE_IN_GRAMS,
    "HG": POUND_IN_GRAMS,
}


class GoldApiError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def get_gold_price(symbol: str, currency: Optional[str] = None) -> dict[str, Any]:
    """Fetch a price from gold-api.com and add ounce/gram price fields."""
    normalized_symbol = symbol.upper()
    url = f"{GOLD_API_BASE_URL}/price/{normalized_symbol}"
    if currency:
        url = f"{url}/{currency.upper()}"

    try:
        upstream_response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise GoldApiError("Gold API is currently unavailable") from exc

    if not upstream_response.ok:
        message = _upstream_error_message(upstream_response)
        # A failed upstream dependency is represented as a gateway error, except
        # for caller errors such as an unsupported symbol or currency.
        status_code = upstream_response.status_code if 400 <= upstream_response.status_code < 500 else 502
        raise GoldApiError(message, status_code)

    try:
        data = upstream_response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise GoldApiError("Gold API returned an invalid response") from exc

    if not isinstance(data, dict):
        raise GoldApiError("Gold API returned an invalid response")

    price = data.get("price")
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise GoldApiError("Gold API response does not contain a valid price")

    grams_per_price_unit = PRICE_UNIT_IN_GRAMS.get(normalized_symbol)
    if grams_per_price_unit is not None:
        data["pricePerGram"] = price / grams_per_price_unit

    return data


def _upstream_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
    except requests.exceptions.JSONDecodeError:
        payload = None

    if isinstance(payload, dict):
        for key in ("message", "error", "detail"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value

    return f"Gold API request failed with status {response.status_code}"
