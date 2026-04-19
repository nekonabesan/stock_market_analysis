import datetime

from pydantic import BaseModel

class CommodityDataUpsertRequest(BaseModel):
    code: str
    market: str | None = None
    name: str | None = None
    memo: str | None = None
    start: datetime.date | None = None
    end: datetime.date | None = None
    message: str | None = None

class CommodityDataUpsertResponse(BaseModel):
    result: bool

class CommodityDataGetRequest(BaseModel):
    code: str
    market: str | None = None
    start: datetime.date | None = None
    end: datetime.date | None = None

class CommodityDataGetResponse(BaseModel):
    results: list[dict]