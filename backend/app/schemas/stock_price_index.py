import datetime

from pydantic import BaseModel


class StockPriceIndexGetRequest(BaseModel):
    code: str
    market: str | None = None
    start: datetime.date
    end: datetime.date


class StockPriceIndexGetResponse(BaseModel):
    results: list[dict]


class StockPriceUpsertRequest(BaseModel):
    code: str
    market: str | None = None
    start: datetime.date
    end: datetime.date


class StockPriceUpsertResponse(BaseModel):
    result: bool