from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from app.api.v1.services.corp_finance_data import CorporateFinanceDataService
from app.models.balance_sheet import BalanceSheet
from app.models.cashflow import CashFlow
from app.models.financials import Financials
from app.models.income_stmt import IncomeStatement
from app.models.quarterly_income_stmt import QuarterlyIncomeStatement


class TestCorporateFinanceDataInit:
    """CorporateFinanceDataService.__init__ のユニットテスト"""

    def test_init_with_code_and_market(self):
        """code と market を指定した場合、ticker_info が取得されることを確認"""
        with patch('app.api.v1.services.corp_finance_data.yf.Ticker') as mock_ticker:
            mock_ticker_instance = MagicMock()
            mock_ticker.return_value = mock_ticker_instance

            corp_finance = CorporateFinanceDataService(code="7203.T", market="TSE")

            assert corp_finance._code == "7203.T"
            assert corp_finance._market == "TSE"
            assert corp_finance._ticker_info is not None
            mock_ticker.assert_called_once_with("7203.T")

    def test_init_without_code(self):
        """code を指定しない場合、ticker_info は None であることを確認"""
        corp_finance = CorporateFinanceDataService(code=None, market="TSE")

        assert corp_finance._code is None
        assert corp_finance._market == "TSE"
        assert corp_finance._ticker_info is None

    def test_init_with_empty_code(self):
        """空の code を指定した場合、ticker_info は None であることを確認"""
        corp_finance = CorporateFinanceDataService(code="", market="TSE")

        assert corp_finance._code == ""
        assert corp_finance._ticker_info is None


class TestBuildTickerSymbol:
    """CorporateFinanceDataService._build_ticker_symbol のユニットテスト"""

    def test_build_ticker_symbol_with_market(self):
        """code と market から正しい ticker 記号を構築"""
        corp_finance = CorporateFinanceDataService()
        result = corp_finance._build_ticker_symbol("7203", "T")

        assert result == "7203.T"

    def test_build_ticker_symbol_with_dot_already_included(self):
        """既にドット付きの code は そのままを返す"""
        corp_finance = CorporateFinanceDataService()
        result = corp_finance._build_ticker_symbol("7203.T", "TSE")

        assert result == "7203.T"

    def test_build_ticker_symbol_with_index_symbol(self):
        """指数記号（^で始まる）はそのまま返す"""
        corp_finance = CorporateFinanceDataService()
        result = corp_finance._build_ticker_symbol("^N225", None)

        assert result == "^N225"

    def test_build_ticker_symbol_without_market(self):
        """market が None の場合は code のみを返す"""
        corp_finance = CorporateFinanceDataService()
        result = corp_finance._build_ticker_symbol("AAPL", None)

        assert result == "AAPL"

    def test_build_ticker_symbol_raises_error_on_empty_code(self):
        """空の code は ValueError を発生させる"""
        corp_finance = CorporateFinanceDataService()

        with pytest.raises(ValueError, match="code is required"):
            corp_finance._build_ticker_symbol("", "T")


class TestConvertDataStructure:
    """CorporateFinanceDataService.convert_data_structure のユニットテスト"""

    def test_convert_data_structure_with_valid_dataframe(self):
        """有効な DataFrame が正しく変換されることを確認"""
        # 日付をインデックスとした DataFrame を作成
        df = pd.DataFrame(
            {
                "2024-01-01": [100, 200],
                "2023-01-01": [150, 250],
            },
            index=["Revenue", "Expenses"],
        )

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        result = corp_finance.convert_data_structure(df)

        assert "Date" in result.columns
        assert "code" in result.columns
        assert "market" in result.columns
        assert len(result) == 2
        assert result.loc[0, "code"] == "7203"
        assert result.loc[0, "market"] == "T"

    def test_convert_data_structure_with_empty_dataframe(self):
        """空の DataFrame は そのまま返される"""
        df = pd.DataFrame()

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        result = corp_finance.convert_data_structure(df)

        assert result.empty

    def test_convert_data_structure_date_format(self):
        """Date カラムが YYYY-MM-DD 形式になることを確認"""
        df = pd.DataFrame(
            {
                "2024-12-31": [100],
                "2023-12-31": [150],
            },
            index=["Revenue"],
        )

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        result = corp_finance.convert_data_structure(df)

        dates = result["Date"].tolist()
        assert all(isinstance(d, str) for d in dates)
        assert all(len(d) == 10 for d in dates)  # YYYY-MM-DD format
        assert "2024-12-31" in dates or "2023-12-31" in dates

    def test_convert_data_structure_normalizes_title_case_columns(self):
        """タイトルケース列が snake_case に正規化されることを確認"""
        df = pd.DataFrame(
            {
                "2024-12-31": [1000],
            },
            index=["Tax Effect Of Unusual Items"],
        )

        corp_finance = CorporateFinanceDataService(code="VWS", market="CO")
        result = corp_finance.convert_data_structure(df)

        assert "tax_effect_of_unusual_items" in result.columns


class TestConvertAndUpsertRecords:
    """CorporateFinanceDataService._convert_and_upsert_records のユニットテスト"""

    def test_upsert_with_empty_dataframe(self):
        """空の DataFrame の場合、処理がスキップされることを確認"""
        db_mock = MagicMock()
        df = pd.DataFrame()

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._convert_and_upsert_records(db_mock, Financials, df)

        # query が呼ばれていないことを確認
        db_mock.query.assert_not_called()

    def test_upsert_inserts_new_record(self):
        """新規レコードが正しく挿入されることを確認"""
        db_mock = MagicMock()
        db_mock.query.return_value.filter.return_value.first.return_value = None

        # convert_data_structure の出力形式をシミュレート
        df = pd.DataFrame({
            "Date": ["2024-01-01", "2023-01-01"],
            "code": ["7203", "7203"],
            "market": ["T", "T"],
            "tax_effect_of_unusual_items": [1000, 2000],
            "tax_rate_for_calcs": [0.25, 0.25],
        })

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        
        # convert_data_structure をモック化
        with patch.object(corp_finance, 'convert_data_structure', return_value=df):
            # インデックス形式の DataFrame を使用（実装が期待する形式）
            source_df = pd.DataFrame({
                "2024-01-01": [1000, 0.25],
                "2023-01-01": [2000, 0.25],
            }, index=["tax_effect_of_unusual_items", "tax_rate_for_calcs"])
            
            corp_finance._convert_and_upsert_records(db_mock, Financials, source_df)

        # 新規レコードが db.add で追加されたことを確認
        assert db_mock.add.call_count >= 1

    def test_upsert_updates_existing_record(self):
        """既存レコードが更新されることを確認"""
        # 既存レコードのモック
        existing_record = MagicMock()
        existing_record.tax_effect_of_unusual_items = 1000

        db_mock = MagicMock()
        db_mock.query.return_value.filter.return_value.first.return_value = existing_record

        # convert_data_structure の出力形式をシミュレート
        df = pd.DataFrame({
            "Date": ["2024-01-01"],
            "code": ["7203"],
            "market": ["T"],
            "tax_effect_of_unusual_items": [2000],
        })

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        
        # convert_data_structure をモック化
        with patch.object(corp_finance, 'convert_data_structure', return_value=df):
            # インデックス形式の DataFrame を使用
            source_df = pd.DataFrame({
                "2024-01-01": [2000],
            }, index=["tax_effect_of_unusual_items"])
            
            corp_finance._convert_and_upsert_records(db_mock, Financials, source_df)

        # 既存レコードが更新されたことを確認（setattr が呼ばれる）
        # add は呼ばれないはず
        db_mock.add.assert_not_called()


class TestUpdateCorpFinanceData:
    """CorporateFinanceDataService.update_corp_finance_data のユニットテスト"""

    @patch('app.api.v1.services.corp_finance_data.SessionLocal')
    def test_update_corp_finance_data_success(self, mock_session_local):
        """正常に更新が完了することを確認"""
        # セッションのモック
        db_mock = MagicMock()
        mock_session_local.return_value = db_mock

        # CorporateFinanceDataService のモック
        corp_finance = CorporateFinanceDataService(code="7203", market="T")

        # 各 get_* メソッドをモック
        with patch.object(corp_finance, 'get_financial_statements', return_value=pd.DataFrame()):
            with patch.object(corp_finance, 'get_balance_sheet', return_value=pd.DataFrame()):
                with patch.object(corp_finance, 'get_cashflow', return_value=pd.DataFrame()):
                    with patch.object(corp_finance, 'get_earnings', return_value=pd.DataFrame()):
                        with patch.object(corp_finance, 'get_quarterly_earnings', return_value=pd.DataFrame()):
                            result = corp_finance.update_corp_finance_data("7203", "T")

        assert result is True
        db_mock.commit.assert_called_once()
        db_mock.close.assert_called_once()

    @patch('app.api.v1.services.corp_finance_data.SessionLocal')
    def test_update_corp_finance_data_rollback_on_error(self, mock_session_local):
        """エラー時にロールバックが実行されることを確認"""
        db_mock = MagicMock()
        db_mock.commit.side_effect = Exception("Database error")
        mock_session_local.return_value = db_mock

        corp_finance = CorporateFinanceDataService(code="7203", market="T")

        with patch.object(corp_finance, 'get_financial_statements', return_value=pd.DataFrame()):
            with patch.object(corp_finance, 'get_balance_sheet', return_value=pd.DataFrame()):
                with patch.object(corp_finance, 'get_cashflow', return_value=pd.DataFrame()):
                    with patch.object(corp_finance, 'get_earnings', return_value=pd.DataFrame()):
                        with patch.object(corp_finance, 'get_quarterly_earnings', return_value=pd.DataFrame()):
                            with pytest.raises(RuntimeError, match="stock data update failed"):
                                corp_finance.update_corp_finance_data("7203", "T")

        db_mock.rollback.assert_called_once()
        db_mock.close.assert_called_once()

    @patch('app.api.v1.services.corp_finance_data.SessionLocal')
    def test_update_corp_finance_data_updates_internal_code_market(self, mock_session_local):
        """update時に内部 code/market が更新されることを確認"""
        db_mock = MagicMock()
        mock_session_local.return_value = db_mock

        corp_finance = CorporateFinanceDataService(code=None, market=None)

        with patch.object(corp_finance, '_get_financial_statements', return_value=pd.DataFrame()):
            with patch.object(corp_finance, '_get_balance_sheet', return_value=pd.DataFrame()):
                with patch.object(corp_finance, '_get_cashflow', return_value=pd.DataFrame()):
                    with patch.object(corp_finance, '_get_earnings', return_value=pd.DataFrame()):
                        with patch.object(corp_finance, '_get_quarterly_earnings', return_value=pd.DataFrame()):
                            result = corp_finance.update_corp_finance_data("VWS", "CO")

        assert result is True
        assert corp_finance._code == "VWS"
        assert corp_finance._market == "CO"


class TestGetFinancialStatements:
    """CorporateFinanceDataService.get_financial_statements のユニットテスト"""

    def test_get_financial_statements_returns_list(self):
        """ORM エンティティリストが返されることを確認"""
        mock_db = MagicMock()
        mock_record = MagicMock(spec=Financials)
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_record]

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_financial_statements("7203", "T")

        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_financial_statements_with_date_filters(self):
        """start/end 指定時に WHERE 句が付与されることを確認"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_financial_statements(
            "7203", "T", start="2023-01-01", end="2024-01-01"
        )

        assert isinstance(result, list)
        mock_db.execute.assert_called_once()

    def test_get_financial_statements_returns_empty_list_when_no_records(self):
        """該当レコードが存在しない場合、空リストが返される"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        corp_finance = CorporateFinanceDataService(code="9999", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_financial_statements("9999", "T")

        assert result == []


class TestGetCashflow:
    """CorporateFinanceDataService.get_cashflow のユニットテスト"""

    def test_get_cashflow_returns_list(self):
        """ORM エンティティリストが返されることを確認"""
        mock_db = MagicMock()
        mock_record = MagicMock(spec=CashFlow)
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_record]

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_cashflow("7203", "T")

        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_cashflow_with_date_filters(self):
        """start/end 指定時に WHERE 句が付与されることを確認"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_cashflow(
            "7203", "T", start="2023-01-01", end="2024-01-01"
        )

        assert isinstance(result, list)
        mock_db.execute.assert_called_once()

    def test_get_cashflow_returns_empty_list_when_no_records(self):
        """該当レコードが存在しない場合、空リストが返される"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        corp_finance = CorporateFinanceDataService(code="9999", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_cashflow("9999", "T")

        assert result == []


class TestExtractEarningsFrame:
    """CorporateFinanceDataService._extract_earnings_frame のユニットテスト"""

    def test_extract_earnings_frame_with_valid_data(self):
        """有効なデータから収益情報が抽出されることを確認"""
        df = pd.DataFrame(
            {
                "2024-01-01": [100000, 50000],
                "2023-01-01": [110000, 55000],
            },
            index=["Total Revenue", "Net Income"],
        )

        corp_finance = CorporateFinanceDataService()
        result = corp_finance._extract_earnings_frame(df)

        assert "Revenue" in result.index
        assert "Earnings" in result.index

    def test_extract_earnings_frame_with_empty_dataframe(self):
        """空 DataFrame の場合、空 DataFrame が返される"""
        df = pd.DataFrame()

        corp_finance = CorporateFinanceDataService()
        result = corp_finance._extract_earnings_frame(df)

        assert result.empty


class TestGetBalanceSheet:
    """CorporateFinanceDataService.get_balance_sheet のユニットテスト"""

    def test_get_balance_sheet_returns_list(self):
        """ORM エンティティリストが返されることを確認"""
        mock_db = MagicMock()
        mock_record = MagicMock(spec=BalanceSheet)
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_record]

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_balance_sheet("7203", "T")

        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_balance_sheet_with_date_filters(self):
        """start/end 指定時に WHERE 句が付与されることを確認"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_balance_sheet(
            "7203", "T", start="2023-01-01", end="2024-01-01"
        )

        assert isinstance(result, list)
        mock_db.execute.assert_called_once()

    def test_get_balance_sheet_returns_empty_list_when_no_records(self):
        """該当レコードが存在しない場合、空リストが返される"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        corp_finance = CorporateFinanceDataService(code="9999", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_balance_sheet("9999", "T")

        assert result == []


class TestGetEarnings:
    """CorporateFinanceDataService.get_earnings のユニットテスト"""

    def test_get_earnings_returns_list(self):
        """ORM エンティティリストが返されることを確認"""
        mock_db = MagicMock()
        mock_record = MagicMock(spec=IncomeStatement)
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_record]

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_earnings("7203", "T")

        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_earnings_with_date_filters(self):
        """start/end 指定時に WHERE 句が付与されることを確認"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_earnings(
            "7203", "T", start="2023-01-01", end="2024-01-01"
        )

        assert isinstance(result, list)
        mock_db.execute.assert_called_once()

    def test_get_earnings_returns_empty_list_when_no_records(self):
        """該当レコードが存在しない場合、空リストが返される"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        corp_finance = CorporateFinanceDataService(code="9999", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_earnings("9999", "T")

        assert result == []


class TestGetQuarterlyEarnings:
    """CorporateFinanceDataService.get_quarterly_earnings のユニットテスト"""

    def test_get_quarterly_earnings_returns_list(self):
        """ORM エンティティリストが返されることを確認"""
        mock_db = MagicMock()
        mock_record = MagicMock(spec=QuarterlyIncomeStatement)
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_record]

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_quarterly_earnings("7203", "T")

        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_quarterly_earnings_with_date_filters(self):
        """start/end 指定時に WHERE 句が付与されることを確認"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        corp_finance = CorporateFinanceDataService(code="7203", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_quarterly_earnings(
            "7203", "T", start="2023-01-01", end="2024-01-01"
        )

        assert isinstance(result, list)
        mock_db.execute.assert_called_once()

    def test_get_quarterly_earnings_returns_empty_list_when_no_records(self):
        """該当レコードが存在しない場合、空リストが返される"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        corp_finance = CorporateFinanceDataService(code="9999", market="T")
        corp_finance._db_session = mock_db
        result = corp_finance.get_quarterly_earnings("9999", "T")

        assert result == []
