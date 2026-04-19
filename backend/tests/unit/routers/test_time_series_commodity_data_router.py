import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

@pytest.mark.parametrize("params,expected_status,service_return", [
    # 200: サービスがリスト返却
    ({"code": "GOLD", "market": "COMEX", "start": "2024-01-01", "end": "2024-01-31"}, 200, [{"date": "2024-01-01", "close": 100, "ma5": 100, "macd": 0, "rsi14": 50}]),
    # 404: サービスが空リスト返却
    ({"code": "INVALID", "market": "COMEX", "start": "2024-01-01", "end": "2024-01-31"}, 404, []),
    # 400: サービスがValueErrorをraise
    ({"code": "GOLD"}, 400, ValueError("invalid request")),
])
def test_get_time_commodity_series_data(params, expected_status, service_return):
    # サービス層をモック
    patch_path = "app.api.v1.routers.time_series_data.TimeSeriesCommodityDataService.get_time_series_data"
    with patch(patch_path) as mock_service:
        if isinstance(service_return, Exception):
            mock_service.side_effect = service_return
        else:
            mock_service.return_value = service_return
        response = client.get("/api/v1/time_series_data/commodity/", params=params)
        assert response.status_code == expected_status
        if expected_status == 200:
            assert "results" in response.json()
            assert response.json()["results"] == service_return
        elif expected_status == 404:
            assert response.json()["detail"] == "Commodity data not found"
        elif expected_status == 400:
            assert "detail" in response.json()
