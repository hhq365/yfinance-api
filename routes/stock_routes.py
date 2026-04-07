from fastapi import APIRouter, Query
from typing import List, Optional

from models.market_ticker import MarketTickers
from models.res import success, error, ResponseModel
from services.stock import get_stocks_by_tickers, get_stocks_by_symbols
from models.stock import StockData

router = APIRouter()


@router.get("/tickers", response_model=ResponseModel)
async def get_stocks_tickers(
        tickers: List[str] = Query(..., description="股票代码列表"),
        markets: Optional[List[str]] = Query(None, description="对应的市场列表，如果只有一个值，会用于所有股票")
):
    if markets is None:
        markets = ["US"]
    if len(markets) != 1 and len(markets) != len(tickers):
        return error("tickers 和 markets 长度不一致")

    return success(get_stocks_by_tickers(tickers, markets))


@router.post("/tickers", response_model=ResponseModel)
async def get_stocks_tickers_post(request: List[MarketTickers]):
    results: dict[str, StockData | None] = {}

    for item in request:
        market = item.market
        tickers = item.tickers
        if not tickers:
            continue  # 忽略空列表
        # 合并 dict
        results.update(get_stocks_by_tickers(tickers, [market]))  # 返回 dict

    return success(results)


@router.post("/symbols", response_model=ResponseModel)
async def get_stocks_symbols_post(symbols: List[str]):
    results = get_stocks_by_symbols(symbols)
    return success(results)
