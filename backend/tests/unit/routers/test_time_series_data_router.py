from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


def _override_db():
    # Router unit testでは実DB接続しない。
    yield object()


class _MockTimeSeriesDataServiceSuccess:
    def __init__(self, db):
        self.db = db

    def get_time_series_data(self, code, market, start, end):
        return [
            {
                "stock_code": code,
                "stock_market": market,
                "date": "2024-01-10",
                "close": 100.5,
                "ma5": 100.1,
                "rsi14": 60.0,
            }
        ]


class _MockTimeSeriesDataServiceNotFound:
    def __init__(self, db):
        self.db = db

    def get_time_series_data(self, code, market, start, end):
        return []


class _MockTimeSeriesDataServiceValueError:
    def __init__(self, db):
        self.db = db

    def get_time_series_data(self, code, market, start, end):
        raise ValueError("start and end are required")


class _MockTimeSeriesDataServiceRuntimeError:
    def __init__(self, db):
        self.db = db

    def get_time_series_data(self, code, market, start, end):
        raise RuntimeError("time series data fetch failed")


class _MockTimeSeriesDataServiceUnexpectedError:
    def __init__(self, db):
        self.db = db

    def get_time_series_data(self, code, market, start, end):
        raise Exception("unexpected")


def test_get_time_series_data_returns_200_when_service_success(monkeypatch):
    from app.api.v1.routers import time_series_data as router_module

    monkeypatch.setattr(router_module, "TimeSeriesStockDataService", _MockTimeSeriesDataServiceSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/time_series_data/stock/",
        params={"code": "7203.T", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1

    app.dependency_overrides.clear()


def test_get_time_series_data_returns_404_when_service_returns_empty_list(monkeypatch):
    from app.api.v1.routers import time_series_data as router_module

    monkeypatch.setattr(router_module, "TimeSeriesStockDataService", _MockTimeSeriesDataServiceNotFound)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/time_series_data/stock/",
        params={"code": "7203.T", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock data not found"

    app.dependency_overrides.clear()


def test_get_time_series_data_returns_400_when_service_raises_value_error(monkeypatch):
    from app.api.v1.routers import time_series_data as router_module

    monkeypatch.setattr(router_module, "TimeSeriesStockDataService", _MockTimeSeriesDataServiceValueError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get("/api/v1/time_series_data/stock/", params={"code": "7203.T"})

    assert response.status_code == 400
    assert response.json()["detail"] == "start and end are required"

    app.dependency_overrides.clear()


def test_get_time_series_data_returns_500_when_service_raises_runtime_error(monkeypatch):
    from app.api.v1.routers import time_series_data as router_module

    monkeypatch.setattr(router_module, "TimeSeriesStockDataService", _MockTimeSeriesDataServiceRuntimeError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/time_series_data/stock/",
        params={"code": "7203.T", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "time series data fetch failed"

    app.dependency_overrides.clear()


def test_get_time_series_data_returns_500_when_service_raises_unexpected_error(monkeypatch):
    from app.api.v1.routers import time_series_data as router_module

    monkeypatch.setattr(router_module, "TimeSeriesStockDataService", _MockTimeSeriesDataServiceUnexpectedError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/time_series_data/stock/",
        params={"code": "7203.T", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred"

    app.dependency_overrides.clear()
