import datetime
from typing import Any

from pydantic import BaseModel


class CorporateFinanceDataUpdateRequest(BaseModel):
    code: str
    market: str | None = None


class CorporateFinanceDataUpdateResponse(BaseModel):
    result: bool


class _FinanceGetRequest(BaseModel):
    """財務データ取得 API 共通リクエストモデル"""
    code: str
    market: str | None = None
    start: datetime.date | None = None
    end: datetime.date | None = None


class FinanceDataGetRequest(_FinanceGetRequest):
    """財務諸表取得 API のリクエストモデル"""


class FinanceDataGetResponse(BaseModel):
    """財務諸表取得 API のレスポンスモデル"""

    results: list[dict[str, Any]]


class BalanceSheetGetRequest(_FinanceGetRequest):
    """バランスシート取得 API のリクエストモデル"""


class BalanceSheetGetResponse(BaseModel):
    """バランスシート取得 API のレスポンスモデル"""

    results: list[dict[str, Any]]


class CashFlowGetRequest(_FinanceGetRequest):
    """キャッシュフロー取得 API のリクエストモデル"""


class CashFlowGetResponse(BaseModel):
    """キャッシュフロー取得 API のレスポンスモデル"""

    results: list[dict[str, Any]]


class EarningsGetRequest(_FinanceGetRequest):
    """損益計算書取得 API のリクエストモデル"""


class EarningsGetResponse(BaseModel):
    """損益計算書取得 API のレスポンスモデル"""

    results: list[dict[str, Any]]


class QuarterlyEarningsGetRequest(_FinanceGetRequest):
    """四半期損益計算書取得 API のリクエストモデル"""


class QuarterlyEarningsGetResponse(BaseModel):
    """四半期損益計算書取得 API のレスポンスモデル"""

    results: list[dict[str, Any]]

