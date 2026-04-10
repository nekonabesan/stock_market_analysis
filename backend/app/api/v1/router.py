from fastapi import APIRouter

from app.api.v1.routers import stock_data

router = APIRouter()

router.include_router(stock_data.router, prefix="/stock", tags=["stock"])
