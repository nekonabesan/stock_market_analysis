from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API server for stock market analysis",
)

app.include_router(v1_router, prefix=settings.api_prefix)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
