from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from models.res import success, error
from utils.currency import get_fx_rate

router = APIRouter()


@router.get("/rate")
def fx_rate(
        from_currency: str = Query(..., min_length=3, max_length=3, description="Base currency"),
        to_currency: str = Query(..., min_length=3, max_length=3, description="Quote currency"),
        ts: Optional[int] = Query(None, description="Optional UNIX timestamp")
):
    """
    Get the exchange rate between two currencies.
    """
    rate = get_fx_rate(from_currency, to_currency, ts)
    if rate is None:
        return error(f"No FX rate found for {from_currency} -> {to_currency}")
    return success({
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "timestamp": ts or int(datetime.now().timestamp()),
        "rate": rate
    })
