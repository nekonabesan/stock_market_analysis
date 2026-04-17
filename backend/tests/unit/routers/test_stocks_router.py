from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


def _override_db():
    # Router unit testでは実DB接続しない。
    yield object()


class _MockStocksServiceSuccess:
    def __init__(self, db):
        self.db = db

    def get_stock_data(self):
        return [
            {
                "id": 1,
                "code": "7203",
                "market": "TSE",
                "name": "TOYOTA",
                "currency": "JPY",
            }
        ]


class _MockStocksServiceNotFound:
    def __init__(self, db):
        self.db = db

    def get_stock_data(self):
        return None


class _MockStocksServiceValueError:
    def __init__(self, db):
        self.db = db

    def get_stock_data(self):
        raise ValueError("invalid request")


class _MockStocksServiceUnexpectedError:
    def __init__(self, db):
        self.db = db

    def get_stock_data(self):
        raise RuntimeError("unexpected")


def test_get_stocks_returns_200_when_service_success(monkeypatch):
    from app.api.v1.routers import stocks as router_module

    monkeypatch.setattr(router_module, "StocksService", _MockStocksServiceSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get("/api/v1/stocks/")


    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["code"] == "7203"
    assert results[0]["currency"] == "JPY"

    app.dependency_overrides.clear()


def test_get_stocks_returns_404_when_service_returns_none(monkeypatch):
    from app.api.v1.routers import stocks as router_module

    monkeypatch.setattr(router_module, "StocksService", _MockStocksServiceNotFound)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get("/api/v1/stocks/")

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock data not found"

    app.dependency_overrides.clear()


def test_get_stocks_returns_400_when_service_raises_value_error(monkeypatch):
    from app.api.v1.routers import stocks as router_module

    monkeypatch.setattr(router_module, "StocksService", _MockStocksServiceValueError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get("/api/v1/stocks/")

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid request"

    app.dependency_overrides.clear()


def test_get_stocks_returns_500_when_service_raises_unexpected_error(monkeypatch):
    from app.api.v1.routers import stocks as router_module

    monkeypatch.setattr(router_module, "StocksService", _MockStocksServiceUnexpectedError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get("/api/v1/stocks/")

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred"

    app.dependency_overrides.clear()
