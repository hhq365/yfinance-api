import pytz
from fastapi import APIRouter, Query
from typing import Optional
import exchange_calendars as xcals
import pandas as pd

from models.market_status import MarketStatus
from utils.markets import market_iso_code
router = APIRouter()


@router.get("/status")
def get_market_status(
        market: str = Query(..., description="股票市场"),
        ts: Optional[int] = Query(None, description="UNIX 时间戳，可选")
):
    isoCode = market_iso_code(market)
    if isoCode is None:
        return {"error": f"No iso code found for market {market}"}
    cal = xcals.get_calendar(isoCode)
    now = pd.Timestamp.utcnow()
    if ts:
        if ts > 1_000_000_000_000:
            ts = ts / 1000
        now = pd.Timestamp(ts, unit='s', tz='UTC')

    is_work_day = cal.is_session(now.date())
    if cal.is_open_on_minute(now):
        session = cal.minute_to_session(now)
        return MarketStatus(
            is_open=True,
            is_work_day=is_work_day,
            current_time=now.isoformat(),
            session_open=cal.session_open(session).isoformat(),
            session_close=cal.session_close(session).isoformat()
        )
    else:
        next_open_time = cal.next_open(now)
        next_close_time = cal.next_close(now)
        return MarketStatus(
            is_open=False,
            is_work_day=is_work_day,
            current_time=now.isoformat(),
            next_open=next_open_time.isoformat(),
            next_close=next_close_time.isoformat(),
            seconds_to_next_open=(next_open_time-now).total_seconds()
        )
