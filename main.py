from fastapi import FastAPI, Depends

from auth import check_api_key
from routes import stock_routes
from routes import currency_routes
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name,
              dependencies=[Depends(check_api_key)] if settings.api_key_enabled else None,)

app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册路由
app.include_router(stock_routes.router, prefix="/api/yfinance/stocks", tags=["stocks"])
app.include_router(currency_routes.router, prefix="/api/yfinance/currency", tags=["currency"])


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
