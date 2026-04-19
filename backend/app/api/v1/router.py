from fastapi import APIRouter

from app.api.v1.routers import corp_finance_data
from app.api.v1.routers import stock_data
from app.api.v1.routers import stocks
from app.api.v1.routers import search
from app.api.v1.routers import time_series_data
from app.api.v1.routers import stock_price_index
from app.api.v1.routers import commodity_data

router = APIRouter()

router.include_router(stock_data.router, prefix="/stock_price", tags=["stock_price"])
router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(time_series_data.router, prefix="/time_series_data", tags=["time_series_data"])
router.include_router(stock_price_index.router, prefix="/stock_price_index", tags=["stock_price_index"])
router.include_router(corp_finance_data.router, prefix="/corp_finance_data", tags=["corp_finance_data"])
router.include_router(commodity_data.router, prefix="/commodity_data", tags=["commodity_data"])
