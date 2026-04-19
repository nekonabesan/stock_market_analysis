import datetime as dt
from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, MagicMock

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@patch("app.api.v1.routers.commodity_data.CommodityDataService")
def test_upsert_commodity_data_success(mock_service, client):
    mock_service.return_value.update_commodity_data.return_value = True
    req = {
        "code": "GOLD",
        "market": "COMEX",
        "start": "2024-01-01",
        "end": "2024-01-31"
    }
    resp = client.post("/api/v1/commodity_data/", json=req)
    assert resp.status_code == 200
    assert resp.json() == {"result": True}
    mock_service.return_value.update_commodity_data.assert_called_once()

@patch("app.api.v1.routers.commodity_data.CommodityDataService")
def test_upsert_commodity_data_not_found(mock_service, client):
    mock_service.return_value.update_commodity_data.return_value = False
    req = {
        "code": "GOLD",
        "market": "COMEX",
        "start": "2024-01-01",
        "end": "2024-01-31"
    }
    resp = client.post("/api/v1/commodity_data/", json=req)
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()

@patch("app.api.v1.routers.commodity_data.CommodityDataService")
def test_get_commodity_data_success(mock_service, client):
    fake = [{"commodity_id": 1, "date": "2024-01-01", "open": 1, "high": 2, "low": 0.5, "close": 1.5, "adj_close": 1.4, "volume": 1000}]
    mock_service.return_value.get_commodity_data.return_value = fake
    req = {
        "code": "GOLD",
        "market": "COMEX",
        "start": "2024-01-01",
        "end": "2024-01-31"
    }
    resp = client.get("/api/v1/commodity_data/", params=req)
    assert resp.status_code == 200
    assert resp.json() == {"results": fake}
    mock_service.return_value.get_commodity_data.assert_called_once()

@patch("app.api.v1.routers.commodity_data.CommodityDataService")
def test_get_commodity_data_not_found(mock_service, client):
    mock_service.return_value.get_commodity_data.return_value = None
    req = {
        "code": "GOLD",
        "market": "COMEX",
        "start": "2024-01-01",
        "end": "2024-01-31"
    }
    resp = client.get("/api/v1/commodity_data/", params=req)
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()
