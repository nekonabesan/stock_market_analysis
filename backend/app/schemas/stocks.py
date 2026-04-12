import datetime

from pydantic import BaseModel

class StockGetRequest(BaseModel):
    pass

class StockGetResponse(BaseModel):
    results: list[dict]