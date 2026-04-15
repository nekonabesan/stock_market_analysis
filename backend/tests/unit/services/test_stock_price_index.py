import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.api.v1.services.stock_price_index import StockPriceIndexService
from app.core.config import IndexDefinition, INDICES


@pytest.fixture
def service(mock_db):
    return StockPriceIndexService(db_session=mock_db)


class TestStockPriceIndexServiceInit:
    """StockPriceIndexService の初期化テスト"""

    def test_indices_loaded_from_config(self, service):
        """INDICES が config から読み込まれることを確認する"""
        assert service.indices == INDICES

    def test_indices_are_index_definition(self, service):
        """各要素が IndexDefinition インスタンスであることを確認する"""
        for index in service.indices:
            assert isinstance(index, IndexDefinition)

    def test_indices_not_empty(self, service):
        """INDICES が空でないことを確認する"""
        assert len(service.indices) > 0


class TestStockPriceIndexServiceUpdateIndexData:
    """StockPriceIndexService.update_index_data のテスト"""

    def test_update_index_data_returns_true(self, service, monkeypatch):
        """正常に更新した場合 True を返すことを確認する"""
        monkeypatch.setattr(service, "_update_index_data", lambda *args, **kwargs: True)

        result = service.update_index_data(
            code="^N225",
            market="TSE",
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 31),
        )

        assert result is True

    def test_update_index_data_passes_args_to_private_method(self, service, monkeypatch):
        """指定した code と market が _update_index_data に渡ることを確認する"""
        called_args = []

        def fake_update(code, market, start, end):
            called_args.append((code, market, start, end))
            return True

        monkeypatch.setattr(service, "_update_index_data", fake_update)

        service.update_index_data(
            code="^GSPC",
            market="NYSE",
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 31),
        )

        assert called_args == [
            ("^GSPC", "NYSE", datetime.date(2024, 1, 1), datetime.date(2024, 1, 31))
        ]

    def test_update_index_data_propagates_runtime_error(self, service, monkeypatch):
        """_update_index_data が RuntimeError を送出した場合に伝播することを確認する"""
        def fake_update(code, market, start, end):
            raise RuntimeError(f"stock data update failed for {code}")

        monkeypatch.setattr(service, "_update_index_data", fake_update)

        with pytest.raises(RuntimeError):
            service.update_index_data(
                code="^N225",
                market="TSE",
                start=datetime.date(2024, 1, 1),
                end=datetime.date(2024, 1, 31),
            )


class TestStockPriceIndexServiceUpdateAllIndexData:
    """StockPriceIndexService.update_all_index_data のテスト"""

    def test_update_all_index_data_returns_true(self, service, monkeypatch):
        """全インデックス更新が成功した場合 True を返すことを確認する"""
        monkeypatch.setattr(service, "_update_index_data", lambda *args, **kwargs: True)

        result = service.update_all_index_data(
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 31),
        )

        assert result is True

    def test_update_all_index_data_calls_update_for_each_index(self, service, monkeypatch):
        """インデックス数分だけ _update_index_data が呼ばれることを確認する"""
        called_codes = []

        def fake_update(code, market, start, end):
            called_codes.append(code)
            return True

        monkeypatch.setattr(service, "_update_index_data", fake_update)

        service.update_all_index_data(
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 31),
        )

        expected_codes = [index.code for index in INDICES]
        assert called_codes == expected_codes

    def test_update_all_index_data_raises_runtime_error(self, service, monkeypatch):
        """全件更新中の例外が RuntimeError に変換されることを確認する"""
        def fake_update(code, market, start, end):
            raise RuntimeError("stock data update failed")

        monkeypatch.setattr(service, "_update_index_data", fake_update)

        with pytest.raises(RuntimeError, match="Failed to update all indices"):
            service.update_all_index_data(
                start=datetime.date(2024, 1, 1),
                end=datetime.date(2024, 1, 31),
            )


class TestStockPriceIndexServicePrivateUpdateIndexData:
    """StockPriceIndexService._update_index_data のテスト"""

    def test_returns_true_on_success(self, service, monkeypatch):
        """正常時に True を返すことを確認する"""
        mock_stock_data_service = MagicMock()
        mock_stock_data_service.update_stock_data.return_value = True

        with patch(
            "app.api.v1.services.stock_price_index.StockDataService",
            return_value=mock_stock_data_service,
        ):
            result = service._update_index_data(
                code="^N225",
                market="TSE",
                start=datetime.date(2024, 1, 1),
                end=datetime.date(2024, 1, 31),
            )

        assert result is True

    def test_passes_correct_args_to_stock_data_service(self, service):
        """update_stock_data に正しい引数が渡されることを確認する"""
        mock_stock_data_service = MagicMock()

        with patch(
            "app.api.v1.services.stock_price_index.StockDataService",
            return_value=mock_stock_data_service,
        ):
            service._update_index_data(
                code="^GSPC",
                market="NYSE",
                start=datetime.date(2024, 1, 1),
                end=datetime.date(2024, 1, 31),
            )

        mock_stock_data_service.update_stock_data.assert_called_once_with(
            "^GSPC", "NYSE", datetime.date(2024, 1, 1), datetime.date(2024, 1, 31)
        )

    def test_raises_runtime_error_on_exception(self, service):
        """StockDataService が例外を送出した場合に RuntimeError を発生させることを確認する"""
        mock_stock_data_service = MagicMock()
        mock_stock_data_service.update_stock_data.side_effect = Exception("yfinance error")

        with patch(
            "app.api.v1.services.stock_price_index.StockDataService",
            return_value=mock_stock_data_service,
        ):
            with pytest.raises(RuntimeError, match="stock data update failed for \\^N225"):
                service._update_index_data(
                    code="^N225",
                    market="TSE",
                    start=datetime.date(2024, 1, 1),
                    end=datetime.date(2024, 1, 31),
                )


class TestStockPriceIndexServiceGetIndexData:
    """StockPriceIndexService.get_index_data のテスト"""

    def test_returns_data_from_stock_data_service(self, service):
        """StockDataService.get_stock_data の結果をそのまま返すことを確認する"""
        expected = [{"date": "2024-01-01", "close": 33000.0}]
        mock_stock_data_service = MagicMock()
        mock_stock_data_service.get_stock_data.return_value = expected

        with patch(
            "app.api.v1.services.stock_price_index.StockDataService",
            return_value=mock_stock_data_service,
        ):
            result = service.get_index_data(
                code="^N225",
                market="TSE",
                start=datetime.date(2024, 1, 1),
                end=datetime.date(2024, 1, 31),
            )

        assert result == expected

    def test_returns_none_when_no_data(self, service):
        """データなしの場合に None を返すことを確認する"""
        mock_stock_data_service = MagicMock()
        mock_stock_data_service.get_stock_data.return_value = None

        with patch(
            "app.api.v1.services.stock_price_index.StockDataService",
            return_value=mock_stock_data_service,
        ):
            result = service.get_index_data(
                code="^N225",
                market="TSE",
                start=datetime.date(2024, 1, 1),
                end=datetime.date(2024, 1, 31),
            )

        assert result is None

    def test_passes_correct_args_to_stock_data_service(self, service):
        """get_stock_data に正しい引数が渡されることを確認する"""
        mock_stock_data_service = MagicMock()
        mock_stock_data_service.get_stock_data.return_value = []

        with patch(
            "app.api.v1.services.stock_price_index.StockDataService",
            return_value=mock_stock_data_service,
        ):
            service.get_index_data(
                code="^HSI",
                market="HKEX",
                start=datetime.date(2024, 6, 1),
                end=datetime.date(2024, 6, 30),
            )

        mock_stock_data_service.get_stock_data.assert_called_once_with(
            "^HSI", "HKEX", datetime.date(2024, 6, 1), datetime.date(2024, 6, 30)
        )
