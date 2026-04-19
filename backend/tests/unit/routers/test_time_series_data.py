import datetime as dt
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@patch("app.api.v1.routers.time_series_data.TimeSeriesStockDataService")
def test_get_time_series_data_success(mock_service, client):
    fake = [
        {"date": "2024-01-01", "close": 100, "ma5": 100, "macd": 0, "rsi14": 50},
        {"date": "2024-01-02", "close": 101, "ma5": 100.5, "macd": 0.1, "rsi14": 51},
    ]
    mock_service.return_value.get_time_series_data.return_value = fake
    params = {
        "code": "7203.T",
        "market": "TSE",
        "start": "2024-01-01",
        "end": "2024-01-02"
    }
    resp = client.get("/api/v1/time_series_data/stock/", params=params)
    assert resp.status_code == 200
    assert resp.json()["results"] == fake
    mock_service.return_value.get_time_series_data.assert_called_once()

@patch("app.api.v1.routers.time_series_data.TimeSeriesStockDataService")
def test_get_time_series_data_not_found(mock_service, client):
    mock_service.return_value.get_time_series_data.return_value = []
    params = {
        "code": "7203.T",
        "market": "TSE",
        "start": "2024-01-01",
        "end": "2024-01-02"
    }
    resp = client.get("/api/v1/time_series_data/stock/", params=params)
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()
