from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


def _override_db():
    # Controller unit testでは実DB接続しない。
    yield object()


class _MockServiceSuccess:
    def __init__(self, db):
        self.db = db

    def update_stock_data(self, code, market, start, end):
        return True


class _MockServiceNotFound:
    def __init__(self, db):
        self.db = db

    def update_stock_data(self, code, market, start, end):
        return False


class _MockServiceValueError:
    def __init__(self, db):
        self.db = db

    def update_stock_data(self, code, market, start, end):
        raise ValueError("start and end are required")


class _MockServiceUnexpectedError:
    def __init__(self, db):
        self.db = db

    def update_stock_data(self, code, market, start, end):
        raise RuntimeError("unexpected")


class _MockServiceGetSuccess:
    def __init__(self, db):
        self.db = db

    def get_stock_data(self, code, market, start, end):
        return [
            {
                "code": code,
                "market": market,
                "date": "2024-01-10",
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.5,
                "volume": 1000,
            }
        ]


class _MockServiceGetNotFound:
    def __init__(self, db):
        self.db = db

    def get_stock_data(self, code, market, start, end):
        return None


class _MockServiceGetValueError:
    def __init__(self, db):
        self.db = db

    def get_stock_data(self, code, market, start, end):
        raise ValueError("start and end are required")


class _MockServiceGetRuntimeError:
    def __init__(self, db):
        self.db = db

    def get_stock_data(self, code, market, start, end):
        raise RuntimeError("stock data fetch failed for 7203.T")


def test_upsert_stock_data_returns_200_when_service_success(monkeypatch):
    from app.api.v1.routers import stock_data as router_module

    monkeypatch.setattr(router_module, "StockDataService", _MockServiceSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post("/api/v1/stock_price/", json={"code": "7203.T"})

    assert response.status_code == 200
    assert response.json() == {"result": True}

    app.dependency_overrides.clear()


def test_upsert_stock_data_returns_404_when_service_false(monkeypatch):
    from app.api.v1.routers import stock_data as router_module

    monkeypatch.setattr(router_module, "StockDataService", _MockServiceNotFound)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post("/api/v1/stock_price/", json={"code": "7203.T"})

    assert response.status_code == 404
    assert "could not be fetched" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_upsert_stock_data_returns_400_when_service_raises_value_error(monkeypatch):
    from app.api.v1.routers import stock_data as router_module

    monkeypatch.setattr(router_module, "StockDataService", _MockServiceValueError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post("/api/v1/stock_price/", json={"code": "7203.T"})

    assert response.status_code == 400
    assert response.json()["detail"] == "start and end are required"

    app.dependency_overrides.clear()


def test_upsert_stock_data_returns_500_when_service_raises_unexpected_error(monkeypatch):
    from app.api.v1.routers import stock_data as router_module

    monkeypatch.setattr(router_module, "StockDataService", _MockServiceUnexpectedError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post("/api/v1/stock_price/", json={"code": "7203.T"})

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred"

    app.dependency_overrides.clear()


def test_get_stock_data_returns_200_when_service_success(monkeypatch):
    from app.api.v1.routers import stock_data as router_module

    monkeypatch.setattr(router_module, "StockDataService", _MockServiceGetSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/stock_price/",
        params={"code": "7203.T", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1

    app.dependency_overrides.clear()


def test_get_stock_data_returns_404_when_service_returns_none(monkeypatch):
    from app.api.v1.routers import stock_data as router_module

    monkeypatch.setattr(router_module, "StockDataService", _MockServiceGetNotFound)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/stock_price/",
        params={"code": "7203.T", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock data not found"

    app.dependency_overrides.clear()


def test_get_stock_data_returns_400_when_service_raises_value_error(monkeypatch):
    from app.api.v1.routers import stock_data as router_module

    monkeypatch.setattr(router_module, "StockDataService", _MockServiceGetValueError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get("/api/v1/stock_price/", params={"code": "7203.T"})

    assert response.status_code == 400
    assert response.json()["detail"] == "start and end are required"

    app.dependency_overrides.clear()


def test_get_stock_data_returns_500_when_service_raises_runtime_error(monkeypatch):
    from app.api.v1.routers import stock_data as router_module

    monkeypatch.setattr(router_module, "StockDataService", _MockServiceGetRuntimeError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/stock_price/",
        params={"code": "7203.T", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "stock data fetch failed for 7203.T"

    app.dependency_overrides.clear()