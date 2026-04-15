from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


def _override_db():
    yield object()


class _MockServiceUpsertSuccess:
    def __init__(self, db):
        self.db = db

    def update_index_data(self, code, market, start, end):
        return True


class _MockServiceUpsertNotFound:
    def __init__(self, db):
        self.db = db

    def update_index_data(self, code, market, start, end):
        return False


class _MockServiceUpsertValueError:
    def __init__(self, db):
        self.db = db

    def update_index_data(self, code, market, start, end):
        raise ValueError("start and end are required")


class _MockServiceAllSuccess:
    def __init__(self, db):
        self.db = db

    def update_all_index_data(self, start, end):
        return True


class _MockServiceAllNotFound:
    def __init__(self, db):
        self.db = db

    def update_all_index_data(self, start, end):
        return False


class _MockServiceGetSuccess:
    def __init__(self, db):
        self.db = db

    def get_index_data(self, code, market, start, end):
        return [
            {
                "code": code,
                "market": market,
                "date": "2024-01-10",
                "close": 33000.0,
            }
        ]


class _MockServiceGetNotFound:
    def __init__(self, db):
        self.db = db

    def get_index_data(self, code, market, start, end):
        return None


class _MockServiceGetRuntimeError:
    def __init__(self, db):
        self.db = db

    def get_index_data(self, code, market, start, end):
        raise RuntimeError("stock data fetch failed for ^N225")


def test_upsert_index_data_returns_200_when_service_success(monkeypatch):
    from app.api.v1.routers import stock_price_index as router_module

    monkeypatch.setattr(router_module, "StockPriceIndexService", _MockServiceUpsertSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/stock_price_index/",
        json={"code": "^N225", "market": "TSE", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 200
    assert response.json() == {"result": True}

    app.dependency_overrides.clear()


def test_upsert_index_data_returns_404_when_service_false(monkeypatch):
    from app.api.v1.routers import stock_price_index as router_module

    monkeypatch.setattr(router_module, "StockPriceIndexService", _MockServiceUpsertNotFound)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/stock_price_index/",
        json={"code": "^N225", "market": "TSE", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 404
    assert "could not be fetched" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_upsert_index_data_returns_422_when_start_or_end_missing(monkeypatch):
    from app.api.v1.routers import stock_price_index as router_module

    monkeypatch.setattr(router_module, "StockPriceIndexService", _MockServiceUpsertSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/stock_price_index/",
        json={"code": "^N225", "market": "TSE", "start": "2024-01-01"},
    )

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_upsert_all_index_data_returns_200_when_service_success(monkeypatch):
    from app.api.v1.routers import stock_price_index as router_module

    monkeypatch.setattr(router_module, "StockPriceIndexService", _MockServiceAllSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/stock_price_index/all/",
        json={"code": "ALL", "market": "ALL", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 200
    assert response.json() == {"result": True}

    app.dependency_overrides.clear()


def test_upsert_all_index_data_returns_404_when_service_false(monkeypatch):
    from app.api.v1.routers import stock_price_index as router_module

    monkeypatch.setattr(router_module, "StockPriceIndexService", _MockServiceAllNotFound)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/stock_price_index/all/",
        json={"code": "ALL", "market": "ALL", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 404
    assert "could not be fetched" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_upsert_all_index_data_returns_422_when_start_or_end_missing(monkeypatch):
    from app.api.v1.routers import stock_price_index as router_module

    monkeypatch.setattr(router_module, "StockPriceIndexService", _MockServiceAllSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/stock_price_index/all/",
        json={"code": "ALL", "market": "ALL", "start": "2024-01-01"},
    )

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_get_index_data_returns_200_when_service_success(monkeypatch):
    from app.api.v1.routers import stock_price_index as router_module

    monkeypatch.setattr(router_module, "StockPriceIndexService", _MockServiceGetSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/stock_price_index/",
        params={"code": "^N225", "market": "TSE", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1

    app.dependency_overrides.clear()


def test_get_index_data_returns_404_when_service_returns_none(monkeypatch):
    from app.api.v1.routers import stock_price_index as router_module

    monkeypatch.setattr(router_module, "StockPriceIndexService", _MockServiceGetNotFound)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/stock_price_index/",
        params={"code": "^N225", "market": "TSE", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock price index data not found"

    app.dependency_overrides.clear()


def test_get_index_data_returns_422_when_start_or_end_missing(monkeypatch):
    from app.api.v1.routers import stock_price_index as router_module

    monkeypatch.setattr(router_module, "StockPriceIndexService", _MockServiceGetSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/stock_price_index/",
        params={"code": "^N225", "market": "TSE", "start": "2024-01-01"},
    )

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_get_index_data_returns_500_when_service_raises_runtime_error(monkeypatch):
    from app.api.v1.routers import stock_price_index as router_module

    monkeypatch.setattr(router_module, "StockPriceIndexService", _MockServiceGetRuntimeError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/stock_price_index/",
        params={"code": "^N225", "market": "TSE", "start": "2024-01-01", "end": "2024-01-31"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "stock data fetch failed for ^N225"

    app.dependency_overrides.clear()