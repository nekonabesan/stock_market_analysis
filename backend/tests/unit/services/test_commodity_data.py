import datetime as dt
import pytest
from unittest.mock import MagicMock

from app.api.v1.services.commodity_data import CommodityDataService
from app.models.commodities import Commodities
from app.models.commodity_price import CommodityPrice

@pytest.fixture
def mock_db_session():
    class DummySession:
        def __init__(self):
            self._data = {}
            self._added = []
            self._executed = []
        def begin(self):
            return self
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def execute(self, stmt):
            self._executed.append(stmt)
            return MagicMock(first=lambda: None, scalar_one_or_none=lambda: 1, limit=lambda x: self)
        def add(self, obj):
            self._added.append(obj)
        def commit(self):
            pass
        def rollback(self):
            pass
        def flush(self):
            pass
    return DummySession()

@pytest.fixture
def service(mock_db_session):
    return CommodityDataService(db_session=mock_db_session)

def test_update_commodity_data(service):
    result = service.update_commodity_data('GC=F', None, dt.date(2024, 1, 1), dt.date(2024, 1, 31))
    assert result is True
    result = service.update_commodity_data('GC=F', '', dt.date(2024, 1, 1), dt.date(2024, 1, 31))
    assert result is True
    pass

def test_fetch_yfinance(service):
    result = service._fetch_yfinance('GC=F', None, dt.date(2024, 1, 1), dt.date(2024, 1, 31))
    assert isinstance(result, list)
    assert "date" in result[0]
    assert "open" in result[0]
    assert isinstance(result[0]["open"], (int, float))

def test_exists_commodity_true(service):
    service.db_session.execute = MagicMock(return_value=MagicMock(first=lambda: True))
    assert service._exists_commodity("GOLD", "COMEX") is True

def test_exists_commodity_false(service):
    service.db_session.execute = MagicMock(return_value=MagicMock(first=lambda: None))
    assert service._exists_commodity("GOLD", "COMEX") is False

def test_upsert_commodity(service):
    service._exists_commodity = MagicMock(return_value=False)
    service.db_session.add = MagicMock()
    service._upsert_commodity("GOLD", "COMEX", 1)
    service.db_session.add.assert_called_once()

def test_build_yfinance_ticker():
    s = CommodityDataService(db_session=MagicMock())
    assert s._build_yfinance_ticker("GOLD", "COMEX") == "GOLD=F"
    assert s._build_yfinance_ticker("GOLD=F", "COMEX") == "GOLD=F"
    assert s._build_yfinance_ticker("GOLD", None) == "GOLD"

def test_normalize_rows():
    s = CommodityDataService(db_session=MagicMock())
    rows = [{"date": dt.datetime(2024,1,1), "open": 1, "high": 2, "low": 0.5, "close": 1.5, "adj_close": 1.4, "volume": 1000}]
    norm = s._normalize_rows(rows)
    assert norm[0]["date"] == dt.date(2024,1,1)
    assert norm[0]["open"] == 1
    assert norm[0]["adj_close"] == 1.4

def test_get_commodity_data_returns_none_on_empty(service):
    service._fetch_commodity_price = MagicMock(return_value=None)
    assert service.get_commodity_data("GOLD", "COMEX") is None

def test_get_commodity_data_returns_data(service):
    fake = [{"commodity_id": 1, "date": "2024-01-01", "open": 1, "high": 2, "low": 0.5, "close": 1.5, "adj_close": 1.4, "volume": 1000}]
    service._fetch_commodity_price = MagicMock(return_value=fake)
    assert service.get_commodity_data("GOLD", "COMEX") == fake
