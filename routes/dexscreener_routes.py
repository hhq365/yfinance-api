from fastapi import APIRouter, Path, Response

from models.res import error, success
from services.dexscreener import DexScreenerError, get_dexscreener_price

router = APIRouter()


@router.get("/price/{chain}/{symbol}")
def price(
    response: Response,
    chain: str = Path(..., min_length=1, max_length=64, pattern=r"^[A-Za-z0-9-]+$"),
    symbol: str = Path(..., min_length=1, max_length=32, pattern=r"^[A-Za-z0-9]+$"),
):
    """Get an on-chain reference price for a configured token contract in both USD and HKD."""
    try:
        data = get_dexscreener_price(chain, symbol)
    except DexScreenerError as exc:
        response.status_code = exc.status_code
        response.headers["Cache-Control"] = "no-store"
        return error(str(exc))
    # The service owns the TTL so clients cannot extend a cached quote's lifetime.
    response.headers["Cache-Control"] = "no-store"
    return success(data)
