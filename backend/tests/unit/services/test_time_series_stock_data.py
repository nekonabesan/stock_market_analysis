import datetime as dt
import pandas as pd
import pytest
from unittest.mock import MagicMock

from app.api.v1.services.time_series_stock_data import TimeSeriesStockDataService
from app.api.v1.services.time_series_data import TimeSeriesDataService

class DummySession:
    def __init__(self, data=None):
        self._data = data or []
    def query(self, model):
        return self
    def filter(self, *args, **kwargs):
        return self
    def all(self):
        return self._data

def make_stock_row(date, close=100, high=110, low=90, open_=95, volume=1000, market="TSE", code="7203.T"):
    class Row:
        pass
    r = Row()
    r.id = 1
    r.date = date
    r.close = close
    r.high = high
    r.low = low
    r.open = open_
    r.volume = volume
    r.stock_market = market
    r.stock_code = code
    # テクニカル指標系は全てNoneで埋める
    r.ma5 = None
    r.ma25 = None
    r.ma75 = None
    r.upper2 = None
    r.lower2 = None
    r.macd = None
    r.macd_signal = None
    r.hist = None
    r.rsi14 = None
    r.rsi28 = None
    r.rci9 = None
    r.rci26 = None
    r.created_at = None
    r.updated_at = None
    return r

@pytest.fixture
def dummy_data():
    base = dt.date(2024, 1, 1)
    return [make_stock_row(base + dt.timedelta(days=i), close=100+i) for i in range(30)]

@pytest.fixture
def stock_service(dummy_data):
    return TimeSeriesStockDataService(db_session=DummySession(data=dummy_data))

@pytest.fixture
def base_df(dummy_data):
    return pd.DataFrame([{k: getattr(row, k) for k in ["date","close","high","low","open","volume","stock_market","stock_code"]} for row in dummy_data])

@pytest.fixture
def base_service():
    return TimeSeriesDataService(db_session=MagicMock())

def test_time_series_stock_data_service_get_time_series_data(stock_service):
    result = stock_service.get_time_series_data("7203.T", "TSE", dt.date(2024,1,1), dt.date(2024,1,30))
    assert isinstance(result, list)
    assert len(result) > 0
    assert "ma5" in result[0]
    assert "macd" in result[0]
    assert "rsi14" in result[0]

def test_time_series_data_service_get_time_series_data(base_service, base_df):
    result = base_service.get_time_series_data(base_df)
    assert isinstance(result, list)
    assert len(result) > 0
    assert "ma5" in result[0]
    assert "macd" in result[0]
    assert "rsi14" in result[0]

def test_time_series_data_service_empty(base_service):
    df = pd.DataFrame([])
    result = base_service.get_time_series_data(df)
    assert result == []

def test_time_series_stock_data_service_invalid_period(stock_service):
    with pytest.raises(ValueError):
        stock_service.get_time_series_data("7203.T", "TSE", None, dt.date(2024,1,30))
    with pytest.raises(ValueError):
        stock_service.get_time_series_data("7203.T", "TSE", dt.date(2024,2,1), dt.date(2024,1,1))
