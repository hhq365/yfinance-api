from typing import List

from pydantic import BaseModel


class MarketTickers(BaseModel):
    market: str  # 市场/交易所
    tickers: List[str]  # 该市场下的股票代码列表
