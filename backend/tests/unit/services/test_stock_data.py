import types

class TestStockDataServiceCurrencyId:
    def test_get_currency_id_returns_id(self, mock_db):
        # Arrange
        service = StockDataService(db_session=mock_db)
        # market="TSE"に対してid=1を返すようにMock
        mock_db.execute.return_value.scalar_one_or_none.return_value = 1
        # Act
        result = service._get_currency_id("TSE")
        # Assert
        assert result == 1

    def test_get_currency_id_returns_none_if_market_none(self, mock_db):
        service = StockDataService(db_session=mock_db)
        assert service._get_currency_id(None) is None

    def test_get_currency_id_returns_none_if_not_found(self, mock_db):
        service = StockDataService(db_session=mock_db)
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        assert service._get_currency_id("NOEXIST") is None
import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.api.v1.services.stock_data import StockDataService


class TestStockDataServiceGetStockData:
    """StockDataService.get_stock_data のユニットテスト"""

    def test_get_stock_data_calls_yfinance(self, stock_data_service):
        """yfinance の get_data_from_yfinance が呼び出されることを確認する"""
        # TODO: 実装後にアサーションを追加する
        pass

    def test_get_stock_data_with_start_end(self, stock_data_service):
        """start / end を指定した場合に正常に動作することを確認する"""
        # TODO: 実装後にアサーションを追加する
        pass

    def test_get_stock_data_without_start_end(self, stock_data_service):
        """start / end を省略した場合に正常に動作することを確認する"""
        # TODO: 実装後にアサーションを追加する
        pass


class TestStockDataServiceReadData:
    def test_get_stock_data_returns_none_when_no_data(self, stock_data_service, monkeypatch):
        monkeypatch.setattr(stock_data_service, "_fetch_trn_stock_price", lambda *args, **kwargs: [])

        result = stock_data_service.get_stock_data(
            code="7203.T",
            market="TSE",
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 31),
        )

        assert result is None

    def test_get_stock_data_raises_value_error_when_period_missing(self, stock_data_service):
        with pytest.raises(ValueError):
            stock_data_service.get_stock_data(
                code="7203.T",
                market="TSE",
                start=None,
                end=datetime.date(2024, 1, 31),
            )

    def test_get_stock_data_raises_runtime_error_on_unexpected_exception(self, stock_data_service, monkeypatch):
        def _raise_error(*args, **kwargs):
            raise Exception("db broken")

        monkeypatch.setattr(stock_data_service, "_fetch_trn_stock_price", _raise_error)

        with pytest.raises(RuntimeError):
            stock_data_service.get_stock_data(
                code="7203.T",
                market="TSE",
                start=datetime.date(2024, 1, 1),
                end=datetime.date(2024, 1, 31),
            )
