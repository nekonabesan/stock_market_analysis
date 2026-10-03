import datetime as dt
import pandas as pd
import pytest
from unittest.mock import MagicMock

from app.api.v1.services.time_series_commodity_data import TimeSeriesCommodityDataService

class DummySession:
    def __init__(self, data=None):
        self._data = data or []
        self.last_query = None
    def query(self, model):
        self.last_query = DummyQuery(self._data)
        return self.last_query


class DummyQuery:
    def __init__(self, data):
        self._data = data
        self.filters = []

    def join(self, *_args, **_kwargs):
        return self

    def filter(self, *args, **kwargs):
        self.filters.extend(args)
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def all(self):
        return self._data

def make_commodity_row(date, close=100, high=110, low=90, open_=95, adj_close=100, volume=1000, market="COM", code="GOLD", commodity_id=1):
    class Row:
        pass
    r = Row()
    r.id = 1
    r.commodity_id = commodity_id
    r.date = date
    r.close = close
    r.high = high
    r.low = low
    r.open = open_
    r.adj_close = adj_close
    r.volume = volume
    r.commodity_market = market
    r.commodity_code = code
    r.created_at = None
    r.updated_at = None
    # StockPrice依存の_row_to_dict参照対策（テスト用ダミー）
    r.stock_code = None
    r.stock_market = None
    return r

@pytest.fixture
def dummy_commodity_data():
    base = dt.date(2024, 1, 1)
    return [make_commodity_row(base + dt.timedelta(days=i), close=100+i) for i in range(30)]

@pytest.fixture
def commodity_service(dummy_commodity_data):
    return TimeSeriesCommodityDataService(db_session=DummySession(data=dummy_commodity_data))

@pytest.fixture
def base_commodity_df(dummy_commodity_data):
    return pd.DataFrame([{k: getattr(row, k) for k in ["date","close","high","low","open","adj_close","volume","commodity_market","commodity_code"]} for row in dummy_commodity_data])

def test_time_series_commodity_data_service_get_time_series_data(commodity_service):
    result = commodity_service.get_time_series_data("GOLD", "COM", dt.date(2024,1,1), dt.date(2024,1,30))
    assert isinstance(result, list)
    assert len(result) > 0
    assert "ma5" in result[0]
    assert "macd" in result[0]
    assert "rsi14" in result[0]


def test_time_series_commodity_data_service_filters_null_market():
    records = [make_commodity_row(dt.date(2024, 1, day)) for day in range(1, 31)]
    session = DummySession(data=records)
    service = TimeSeriesCommodityDataService(db_session=session)

    result = service.get_time_series_data("GOLD", None, dt.date(2024, 1, 1), dt.date(2024, 1, 30))

    assert result
    assert any("mst_commodities.market IS NULL" in str(clause) for clause in session.last_query.filters)


def test_time_series_commodity_data_service_rejects_duplicate_dates():
    duplicate_date = dt.date(2024, 1, 1)
    records = [
        make_commodity_row(duplicate_date, commodity_id=1),
        make_commodity_row(duplicate_date, commodity_id=1),
    ]
    service = TimeSeriesCommodityDataService(db_session=DummySession(data=records))

    with pytest.raises(RuntimeError, match="duplicate commodity price dates"):
        service.get_time_series_data("GOLD", None, duplicate_date, duplicate_date)

def test_time_series_commodity_data_service_invalid_period(commodity_service):
    with pytest.raises(ValueError):
        commodity_service.get_time_series_data("GOLD", "COM", None, dt.date(2024,1,30))
    with pytest.raises(ValueError):
        commodity_service.get_time_series_data("GOLD", "COM", dt.date(2024,2,1), dt.date(2024,1,1))

def test_time_series_commodity_data_service_empty():
    service = TimeSeriesCommodityDataService(db_session=DummySession([]))
    result = service.get_time_series_data("GOLD", "COM", dt.date(2024,1,1), dt.date(2024,1,30))
    assert result == []
