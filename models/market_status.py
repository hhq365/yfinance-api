from typing import Optional

from pydantic import BaseModel


class MarketStatus(BaseModel):
    is_open: bool
    current_time: str
    session_open: Optional[str] = None
    session_close: Optional[str] = None
    next_open: Optional[str] = None
    next_close: Optional[str] = None
    seconds_to_next_open: float = 0
