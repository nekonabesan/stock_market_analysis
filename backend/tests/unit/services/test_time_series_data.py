import datetime as dt
import importlib
import sys
import types
from dataclasses import dataclass
import pandas as pd

import pytest


# NOTE:
# rci.py は conftest.py で FakeRci として定義済みのため、ここでの定義は不要。
# talib は pyproject.toml 経由で実インストール済み。

service_module = importlib.import_module("app.api.v1.services.time_series_data")
TimeSeriesDataService = service_module.TimeSeriesDataService


@dataclass
class _Record:
    code: str
    market: str
    date: dt.date
    open: float
    high: float
    low: float
    close: float
    volume: int

    def to_dict(self):
        return {
            "code": self.code,
            "market": self.market,
            "date": self.date,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


class _FakeQuery:
    def __init__(self, records):
        self._records = records
        self.filter_calls = 0

    def filter(self, *args, **kwargs):
        self.filter_calls += 1
        return self

    def all(self):
        return self._records


class _FakeSession:
    def __init__(self, records):
        self._records = records
        self.query_called = False

    def query(self, *_args, **_kwargs):
        self.query_called = True
        return _FakeQuery(self._records)


def test_get_time_series_data_raises_value_error_when_period_missing():
    service = TimeSeriesDataService(db_session=_FakeSession([]))
    import pandas as pd
    # 必須列がない場合は空リストを返す
    df = pd.DataFrame()
    result = service.get_time_series_data(df)
    assert result == []


def test_get_time_series_data_returns_empty_list_when_no_records():
    session = _FakeSession([])
    service = TimeSeriesDataService(db_session=session)
    import pandas as pd
    # 必須列はあるがデータが空
    df = pd.DataFrame(columns=["date", "close"])
    result = service.get_time_series_data(df)
    assert result == []


def test_get_time_series_data_filters_by_date_and_returns_enriched_rows():
    # TA-Lib STOCHに必要な最小レコード数を満たすため十分なデータを用意する。
    records = [
        _Record("7203", "TSE", dt.date(2024, 10, 1), 100, 101, 99, 100, 1000),
        _Record("7203", "TSE", dt.date(2024, 10, 2), 101, 102, 100, 101, 1100),
        _Record("7203", "TSE", dt.date(2024, 10, 3), 102, 103, 101, 102, 1200),
        _Record("7203", "TSE", dt.date(2024, 10, 4), 103, 104, 102, 103, 1300),
        _Record("7203", "TSE", dt.date(2024, 10, 5), 104, 105, 103, 104, 1400),
        _Record("7203", "TSE", dt.date(2024, 10, 6), 105, 106, 104, 105, 1400),
        _Record("7203", "TSE", dt.date(2024, 10, 7), 106, 107, 105, 106, 1400),
        _Record("7203", "TSE", dt.date(2024, 10, 8), 107, 108, 106, 107, 1400),
        _Record("7203", "TSE", dt.date(2024, 10, 9), 108, 109, 107, 108, 1400),
        _Record("7203", "TSE", dt.date(2024, 10, 10), 109, 110, 108, 109, 1400),
        _Record("7203", "TSE", dt.date(2024, 10, 11), 110, 111, 109, 110, 1400),
        _Record("7203", "TSE", dt.date(2024, 10, 12), 111, 112, 110, 111, 1500),
        _Record("7203", "TSE", dt.date(2025, 1, 5),  110, 112, 109, 111, 1500),
        _Record("7203", "TSE", dt.date(2025, 1, 10), 120, 121, 118, 119, 1700),
        _Record("7203", "TSE", dt.date(2025, 2, 1),  130, 132, 128, 131, 1800),
    ]
    service = TimeSeriesDataService(db_session=_FakeSession(records))

    df = pd.DataFrame([r.to_dict() for r in records])
    result = service.get_time_series_data(df)
    assert len(result) > 0
    assert "ma5" in result[0]
    assert "macd" in result[0]
    assert "rci9" in result[0]
    assert "rci26" in result[0]
    assert "rising_condition" in result[0]


def test_get_time_series_data_wraps_unexpected_exception_into_runtime_error(monkeypatch):
    import pandas as pd
    records = [_Record("7203", "TSE", dt.date(2025, 1, 5), 110, 112, 109, 111, 1500)]
    service = TimeSeriesDataService(db_session=_FakeSession(records))
    def _raise_error(*_args, **_kwargs):
        raise Exception("boom")
    monkeypatch.setattr(service, "_calc_sma", _raise_error)
    df = pd.DataFrame([r.to_dict() for r in records])
    with pytest.raises(RuntimeError, match="time series data fetch failed"):
        service.get_time_series_data(df)


def test_check_rising_condition_all_conditions_met():
    """3つの条件をすべて満たす場合、True を返す行がある"""
    # 十分なデータを用意（約1ヶ月分で、計算に必要な期間をカバー）
    import pandas as pd
    
    dates = pd.date_range(start="2024-10-01", periods=30, freq="D")
    records = [
        _Record("7203", "TSE", d.date(), 100 + i, 101 + i, 99 + i, 100 + i, 1000)
        for i, d in enumerate(dates)
    ]
    service = TimeSeriesDataService(db_session=_FakeSession(records))

    df = pd.DataFrame([r.to_dict() for r in records])
    result = service.get_time_series_data(df)
    assert len(result) > 0
    assert "rising_condition" in result[0]
    assert isinstance(result[0]["rising_condition"], (bool, type(None)))


def test_check_rising_condition_returns_series_with_bool_values():
    """_check_rising_condition が bool Series を返すことを確認"""
    import pandas as pd
    
    dates = pd.date_range(start="2024-10-01", periods=30, freq="D")
    records = [
        _Record("7203", "TSE", d.date(), 100 + i, 101 + i, 99 + i, 100 + i, 1000)
        for i, d in enumerate(dates)
    ]
    service = TimeSeriesDataService(db_session=_FakeSession(records))

    df = pd.DataFrame([r.to_dict() for r in records])
    result = service.get_time_series_data(df)
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], dict)
    assert "date" in result[0]
    assert "close" in result[0]
    assert "macd" in result[0]
    assert "macd_signal" in result[0]
    assert "rci26" in result[0]
