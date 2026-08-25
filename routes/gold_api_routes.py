from fastapi import APIRouter, Path, Response

from models.res import error, success
from services.gold_api import GoldApiError, get_gold_price


router = APIRouter()


@router.get("/price/{symbol}")
def price(
        response: Response,
        symbol: str = Path(..., min_length=2, max_length=10, pattern=r"^[A-Za-z0-9]+$", description="Gold API 资产代码")
):
    """查询 Gold API 实时报价，并同时返回每金衡盎司与每克价格。"""
    return _price(response, symbol)


@router.get("/price/{symbol}/{currency}")
def price_with_currency(
        response: Response,
        symbol: str = Path(..., min_length=2, max_length=10, pattern=r"^[A-Za-z0-9]+$", description="Gold API 资产代码"),
        currency: str = Path(..., min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$", description="计价货币")
):
    """使用指定货币查询 Gold API 实时报价。"""
    return _price(response, symbol, currency)


def _price(response: Response, symbol: str, currency: str | None = None):
    response.headers["Cache-Control"] = "no-store"
    try:
        data = get_gold_price(symbol, currency)
    except GoldApiError as exc:
        response.status_code = exc.status_code
        return error(str(exc))

    return success(data)
