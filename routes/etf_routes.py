from fastapi import APIRouter, Query, Response

from models.res import ResponseModel, error, success
from services.etf import ETFQueryError, get_etfs

router = APIRouter()


@router.get("", response_model=ResponseModel)
def list_etfs(
    response: Response,
    region: str = Query(..., pattern=r"^[A-Za-z]{2}$", description="Listing region code, such as hk, us, cn, jp, or gb. Case-insensitive."),
    page: int = Query(1, ge=1, description="Page number, starting at 1."),
    pagesize: int = Query(100, ge=1, le=250, description="Maximum number of results per page."),
    ticker: str = Query("", max_length=64, description="Optional exact Yahoo ticker, such as 2840.HK. Empty means no ticker filter. Wildcards are not supported."),
):
    """List ETFs by listing region using Yahoo Finance. Different currency counters may appear separately. Prices may be delayed; this is not a gold-only filter."""
    response.headers["Cache-Control"] = "no-store"
    try:
        return success(get_etfs(region, page, pagesize, ticker))
    except ETFQueryError as exc:
        response.status_code = exc.status_code
        return error(str(exc))
