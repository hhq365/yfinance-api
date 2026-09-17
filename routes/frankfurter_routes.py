from fastapi import APIRouter, Path, Response

from models.res import error, success
from utils.currency import FrankfurterError, get_frankfurter_rate

router = APIRouter()


@router.get("/rate/{base}/{quote}")
def rate(
    response: Response,
    base: str = Path(..., pattern=r"^[A-Za-z]{3}$", description="Base currency, such as USD"),
    quote: str = Path(..., pattern=r"^[A-Za-z]{3}$", description="Quote currency, such as HKD"),
):
    """Get the latest available Frankfurter reference rate, cached for 5 minutes. This is not a tick-by-tick market quote."""
    response.headers["Cache-Control"] = "no-store"
    try:
        data = get_frankfurter_rate(base, quote)
    except FrankfurterError as exc:
        response.status_code = exc.status_code
        return error(str(exc))
    data["rate"] = float(data["rate"])
    return success(data)
