import datetime

from pydantic import BaseModel

class TimeSeriesDataGetRequest(BaseModel):
    code: str
    market: str | None = None
    start: datetime.date | None = None
    end: datetime.date | None = None

class TimeSeriesDataGetResponse(BaseModel):
    results: list[dict]