from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from utils.currency import get_fx_rate

router = APIRouter()


@router.get("/rate")
def fx_rate(
        from_currency: str = Query(..., min_length=3, max_length=3, description="源货币"),
        to_currency: str = Query(..., min_length=3, max_length=3, description="目标货币"),
        ts: Optional[int] = Query(None, description="UNIX 时间戳，可选")
):
    """
    查询货币汇率
    """
    rate = get_fx_rate(from_currency, to_currency, ts)
    if rate is None:
        return {"error": f"No FX rate found for {from_currency} -> {to_currency}"}
    return {
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "timestamp": ts or int(datetime.now().timestamp()),
        "rate": rate
    }
