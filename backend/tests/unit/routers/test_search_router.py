from fastapi.testclient import TestClient

from app.main import app


class _MockSearchServiceSuccess:
    def search(self, market, name=None, code=None):
        return {
            "found": True,
            "market": market,
            "name": "TOYOTA MOTOR CORP.",
            "code": "7203.T",
        }


class _MockSearchServiceNotFound:
    def search(self, market, name=None, code=None):
        return None


class _MockSearchServiceValueError:
    def search(self, market, name=None, code=None):
        raise ValueError("invalid request")


class _MockSearchServiceUnexpectedError:
    def search(self, market, name=None, code=None):
        raise RuntimeError("unexpected")


def test_post_search_returns_200_when_service_success(monkeypatch):
    from app.api.v1.routers import search as router_module

    monkeypatch.setattr(router_module, "SearchService", _MockSearchServiceSuccess)

    client = TestClient(app)
    response = client.post("/api/v1/search/", json={"market": "TSE", "code": "7203"})

    assert response.status_code == 200
    assert response.json()["found"] is True
    assert response.json()["code"] == "7203.T"


def test_post_search_returns_404_when_service_returns_none(monkeypatch):
    from app.api.v1.routers import search as router_module

    monkeypatch.setattr(router_module, "SearchService", _MockSearchServiceNotFound)

    client = TestClient(app)
    response = client.post("/api/v1/search/", json={"market": "TSE", "code": "9999"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock data not found"


def test_post_search_returns_400_when_service_raises_value_error(monkeypatch):
    from app.api.v1.routers import search as router_module

    monkeypatch.setattr(router_module, "SearchService", _MockSearchServiceValueError)

    client = TestClient(app)
    response = client.post("/api/v1/search/", json={"market": "TSE", "code": "7203"})

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid request"


def test_post_search_returns_422_when_name_and_code_missing():
    client = TestClient(app)
    response = client.post("/api/v1/search/", json={"market": "TSE"})

    assert response.status_code == 422


def test_post_search_returns_500_when_service_raises_unexpected_error(monkeypatch):
    from app.api.v1.routers import search as router_module

    monkeypatch.setattr(router_module, "SearchService", _MockSearchServiceUnexpectedError)

    client = TestClient(app)
    response = client.post("/api/v1/search/", json={"market": "TSE", "code": "7203"})

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred"
