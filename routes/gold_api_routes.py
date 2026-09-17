from fastapi import APIRouter, Path, Response

from config import get_settings
from models.res import error, success
from services.gold_api import GoldApiError, get_gold_price


router = APIRouter()
settings = get_settings()


@router.get("/price/{symbol}")
def price(
        response: Response,
        symbol: str = Path(..., min_length=2, max_length=10, pattern=r"^[A-Za-z0-9]+$", description="Gold API asset symbol")
):
    """Get the latest Gold API price, including per-troy-ounce and per-gram prices where applicable."""
    return _price(response, symbol)


@router.get("/price/{symbol}/{currency}")
def price_with_currency(
        response: Response,
        symbol: str = Path(..., min_length=2, max_length=10, pattern=r"^[A-Za-z0-9]+$", description="Gold API asset symbol"),
        currency: str = Path(..., min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$", description="Quote currency")
):
    """Get the latest Gold API price in the specified currency."""
    return _price(response, symbol, currency)


def _price(response: Response, symbol: str, currency: str | None = None):
    try:
        data = get_gold_price(symbol, currency)
    except GoldApiError as exc:
        response.headers["Cache-Control"] = "no-store"
        response.status_code = exc.status_code
        return error(str(exc))

    response.headers["Cache-Control"] = f"max-age={settings.gold_api_price_cache_seconds}"
    return success(data)
