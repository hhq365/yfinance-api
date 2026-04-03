from typing import Optional

from pydantic import BaseModel


class MarketStatus(BaseModel):
    is_open: bool = False
    is_work_day: bool = False
    current_time: str
    current_open: Optional[str] = None
    current_close: Optional[str] = None
    next_open: Optional[str] = None
    next_close: Optional[str] = None
    seconds_to_next_open: float = 0
