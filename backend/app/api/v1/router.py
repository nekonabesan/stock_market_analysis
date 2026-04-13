from fastapi import APIRouter

from app.api.v1.routers import stock_data
from app.api.v1.routers import stocks
from app.api.v1.routers import time_series_data

router = APIRouter()

router.include_router(stock_data.router, prefix="/stock_price", tags=["stock_price"])
router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
router.include_router(time_series_data.router, prefix="/time_series_data", tags=["time_series_data"])

