from fastapi import APIRouter, Path, Response

from models.res import error, success
from utils.currency import FrankfurterError, get_frankfurter_rate

router = APIRouter()


@router.get("/rate/{base}/{quote}")
def rate(
    response: Response,
    base: str = Path(..., pattern=r"^[A-Za-z]{3}$", description="源货币，如 USD"),
    quote: str = Path(..., pattern=r"^[A-Za-z]{3}$", description="目标货币，如 HKD"),
):
    """获取 Frankfurter 最新可用参考汇率，缓存 5 分钟；不是逐笔实时行情。"""
    response.headers["Cache-Control"] = "no-store"
    try:
        data = get_frankfurter_rate(base, quote)
    except FrankfurterError as exc:
        response.status_code = exc.status_code
        return error(str(exc))
    data["rate"] = float(data["rate"])
    return success(data)
