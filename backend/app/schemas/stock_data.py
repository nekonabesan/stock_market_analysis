import datetime

from pydantic import BaseModel


class StockDataUpsertRequest(BaseModel):
    code: str
    market: str | None = None
    name: str | None = None
    sector: str | None = None
    memo: str | None = None
    start: datetime.date | None = None
    end: datetime.date | None = None
    message: str | None = None


class StockDataUpsertResponse(BaseModel):
    result: bool


class StockDataGetRequest(BaseModel):
    code: str
    market: str | None = None
    start: datetime.date | None = None
    end: datetime.date | None = None

class StockDataGetResponse(BaseModel):
    results: list[dict]