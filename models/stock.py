from _decimal import Decimal

from pydantic import BaseModel
from typing import Optional

from pydantic import BaseModel
from typing import List


class StockData(BaseModel):
    symbol: str  # 股票代码
    market: Optional[str] = None  # 市场/交易所
    ticker: Optional[str] = None  # 股票代码
    short_name: Optional[str]  # 股票名称
    long_name: Optional[str]  # 股票名称
    price: Optional[Decimal]  # 当前价格
    price_usd: Optional[Decimal] = None
    previous_close: Optional[Decimal]  # 昨收
    open: Optional[Decimal]  # 今开
    high: Optional[Decimal]  # 今日最高
    low: Optional[Decimal]  # 今日最低
    volume: Optional[int]  # 成交量
    currency: Optional[str]  # 货币
    rate_to_usd: Optional[Decimal] = None
    data_time: Optional[str]  # 数据时间 ISO 格式
