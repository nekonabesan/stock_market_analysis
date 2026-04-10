from pathlib import Path
from unittest.mock import patch

import pandas as pd

from app.api.v1.infra.get_market_data import GetMarketData


class TestGetMarketData:
    def test_get_data_from_yfinance_delegates_to_yfinance_download(self):
        # yfinance.download をモックし、OHLCVのDataFrameを返す。
        # インフラ層で列名正規化と list[dict] 変換ができることを確認する。
        expected = pd.DataFrame(
            {
                "Open": [100.0, 101.0],
                "High": [102.0, 103.0],
                "Low": [99.0, 100.0],
                "Close": [101.0, 102.0],
                "Volume": [1000, 1200],
            },
            index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
        )
        market_data = GetMarketData(data_path=Path("/tmp"))

        with patch("app.api.v1.infra.get_market_data.yf.download", return_value=expected) as mock_download:
            result = market_data.get_data_from_yfinance(
                "7203.T",
                start="2024-01-01",
                end="2024-01-31",
            )

        mock_download.assert_called_once_with("7203.T", start="2024-01-01", end="2024-01-31", progress=False)
        assert len(result) == 2
        assert set(result[0].keys()) == {"date", "open", "high", "low", "close", "volume"}
        assert result[0]["open"] == 100.0
        assert result[1]["close"] == 102.0

    def test_get_data_from_yfinance_logs_and_raises_runtime_error(self):
        # yfinanceで例外が発生した場合、logger.errorを呼び出したうえで
        # RuntimeErrorへ変換して送出することを確認する。
        market_data = GetMarketData(data_path=Path("/tmp"))

        with patch("app.api.v1.infra.get_market_data.yf.download", side_effect=Exception("network error")):
            with patch("app.api.v1.infra.get_market_data.logger.error") as mock_logger_error:
                try:
                    market_data.get_data_from_yfinance("7203.T", start="2024-01-01", end="2024-01-31")
                    assert False, "RuntimeError が送出される想定"
                except RuntimeError as error:
                    assert "yfinance fetch failed for 7203.T" in str(error)

        mock_logger_error.assert_called_once()