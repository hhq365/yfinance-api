from typing_extensions import Annotated

from fastapi import Request, HTTPException, status, Depends, Header

from config import Settings, get_settings


async def check_api_key(request: Request,
                        settings: Annotated[Settings, Depends(get_settings)],
                        x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
                        ):
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )

    if x_api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
