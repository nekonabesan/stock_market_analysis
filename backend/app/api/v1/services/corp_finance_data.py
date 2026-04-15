from datetime import date, datetime
import re
from typing import Any

import pandas as pd
import yfinance as yf
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.session import SessionLocal
from app.models.balance_sheet import BalanceSheet
from app.models.cashflow import CashFlow
from app.models.financials import Financials
from app.models.income_stmt import IncomeStatement
from app.models.quarterly_income_stmt import QuarterlyIncomeStatement


class CorporateFinanceDataService:
    EARNINGS_ROW_CANDIDATES = {
        "Revenue": ["Total Revenue", "Operating Revenue", "Revenue"],
        "Earnings": [
            "Net Income",
            "Net Income Common Stockholders",
            "Net Income Including Noncontrolling Interests",
        ],
    }

    def __init__(self, code: str | None = None, market: str | None = None, db_session: Session | None = None):
        self._code = code
        self._market = market
        self._db_session = db_session or SessionLocal()
        self._ticker_info = self._get_corporate_finance_data(code, market) if code else None

    def _build_ticker_symbol(self, code: str, market: str | None) -> str:
        """code と market から yfinance のティッカー文字列を組み立てる。"""
        normalized_code = code.strip()
        if not normalized_code:
            raise ValueError("code is required")

        # 既にサフィックス付き、もしくは指数記号のときはそのまま使う。
        if "." in normalized_code or normalized_code.startswith("^"):
            return normalized_code

        if market is None or not market.strip():
            return normalized_code

        return f"{normalized_code}.{market.strip()}"

    def _get_corporate_finance_data(
        self,
        code: str,
        market: str | None,
    ) -> Any | None:
        """
        yfinance の Ticker オブジェクトを取得
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
        Returns:
            Any | None: yfinance Ticker オブジェクト、または取得不可の場合は None
        """
        try:
            ticker_symbol = self._build_ticker_symbol(code, market)
            return yf.Ticker(ticker_symbol)
        except Exception as e:
            logger.error(f"Error fetching ticker object for code={code}, market={market}: {e}")
            return None

    def _resolve_ticker_info(self, code: str | None, market: str | None):
        """キャッシュ済み ticker が使える場合は再利用し、必要時のみ再取得する。"""
        if code is None or not code.strip():
            raise ValueError("code is required")

        if (
            self._ticker_info is not None
            and code == self._code
            and (market or "") == (self._market or "")
        ):
            return self._ticker_info

        return self._get_corporate_finance_data(code, market)

    def _safe_frame(self, frame: pd.DataFrame | None) -> pd.DataFrame:
        """None の場合に空 DataFrame を返して呼び出し側の扱いを安定させる。"""
        if frame is None:
            return pd.DataFrame()
        return frame

    def _get_frame_from_ticker(self, ticker_info, attr_name: str) -> pd.DataFrame:
        """Ticker から指定属性を安全に取得し、失敗時は空 DataFrame を返す。"""
        try:
            frame = getattr(ticker_info, attr_name, None)
            return self._safe_frame(frame)
        except Exception as e:
            logger.error(f"Error reading {attr_name}: {e}")
            return pd.DataFrame()

    def _pick_first_matching_row(self, df: pd.DataFrame, candidates: list[str]) -> pd.Series | None:
        """候補名のうち最初に一致した行を返す。"""
        for row_name in candidates:
            if row_name in df.index:
                return df.loc[row_name]
        return None

    def _extract_earnings_frame(self, statement_df: pd.DataFrame) -> pd.DataFrame:
        """income_stmt から収益系の代表項目を抽出し、既存形式で返す。"""
        if statement_df.empty:
            return pd.DataFrame()

        extracted_rows: dict[str, pd.Series] = {}
        for output_name, candidates in self.EARNINGS_ROW_CANDIDATES.items():
            matched_row = self._pick_first_matching_row(statement_df, candidates)
            if matched_row is not None:
                extracted_rows[output_name] = matched_row

        if not extracted_rows:
            return pd.DataFrame()

        return pd.DataFrame(extracted_rows).T
    
    def update_corp_finance_data(self, code: str, market: str | None) -> bool:
        """
        指定された code と market に基づいて財務データを更新する。
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
        Returns:
            bool: データの更新が成功した場合は True、失敗した場合は例外をスロー
        """
        try:
            # convert_data_structure で利用する code/market を常に更新して保持する。
            self._code = code
            self._market = market

            # 直近４年分の財務諸表を取得しtrn_financialsテーブルをUPDATE/INSERT
            financials = self._get_financial_statements(code, market)

            # 直近４年分のバランスシートを取得しtrn_balance_sheetテーブルをUPDATE/INSERT
            balance_sheet = self._get_balance_sheet(code, market)

            # 直近４年分のキャッシュフローを取得しtrn_cashflowテーブルをUPDATE/INSERT
            cashflow = self._get_cashflow(code, market)

            # 直近４年分の収益を取得しtrn_income_stmtテーブルをUPDATE/INSERT
            income_stmt = self._get_earnings(code, market)

            # 直近４年分の四半期収益を取得しtrn_quarterly_income_stmtテーブルをUPDATE/INSERT
            quarterly_income_stmt = self._get_quarterly_earnings(code, market)

            db = self._db_session
            try:
                # 各財務データを変換してupsert
                self._convert_and_upsert_records(db, Financials, financials)
                self._convert_and_upsert_records(db, BalanceSheet, balance_sheet)
                self._convert_and_upsert_records(db, CashFlow, cashflow)
                self._convert_and_upsert_records(db, IncomeStatement, income_stmt)
                self._convert_and_upsert_records(db, QuarterlyIncomeStatement, quarterly_income_stmt)
                
                db.commit()
                logger.info(f"Successfully updated financial data for {code}")
                return True
            except Exception as e:
                db.rollback()
                raise
            finally:
                db.close()
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating financial data for {code}: {e}")
            raise RuntimeError(f"stock data update failed for {code}") from e


    def _convert_and_upsert_records(self, db: Session, model_class: type, df: pd.DataFrame) -> None:
        """
        DataFrameを変換してモデルに対してUPSERTする
        Args:
            db (Session): SQLAlchemy セッション
            model_class (type): ORM モデルクラス
            df (pd.DataFrame): 変換前のDataFrame
        """
        if df.empty:
            return

        # データを変換
        converted_df = self.convert_data_structure(df)
        records = converted_df.to_dict('records')

        for record in records:
            # Date 文字列を date オブジェクトに変換
            if 'Date' in record:
                record_date = datetime.strptime(record.pop('Date'), '%Y-%m-%d').date()
            else:
                continue

            record_market = record.pop('market')
            record_code = record.pop('code')

            # 既存レコードを検索
            existing = db.query(model_class).filter(
                model_class.date == record_date,
                model_class.market == record_market,
                model_class.code == record_code,
            ).first()

            if existing:
                # 既存レコードを更新（PK以外）
                for key, value in record.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
            else:
                # 新規レコードを作成
                new_record = model_class(
                    date=record_date,
                    market=record_market,
                    code=record_code,
                    **record,
                )
                db.add(new_record)

    def _get_financial_statements(self, code: str, market: str | None) -> pd.DataFrame:
        """
        直近４年分の財務諸表を取得
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
        Returns:
            pd.DataFrame: 財務データのDataFrame
        """
        ticker_info = self._resolve_ticker_info(code, market)
        if ticker_info is None:
            return pd.DataFrame()
        return self._get_frame_from_ticker(ticker_info, "financials")
    
    def _get_balance_sheet(self, code: str, market: str | None) -> pd.DataFrame:
        """
        直近４年分のバランスシートを取得
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
        Returns:
            pd.DataFrame: バランスシートのDataFrame
        """
        ticker_info = self._resolve_ticker_info(code, market)
        if ticker_info is None:
            return pd.DataFrame()
        return self._get_frame_from_ticker(ticker_info, "balance_sheet")
    
    def _get_cashflow(self, code: str, market: str | None) -> pd.DataFrame:
        """
        直近４年分のキャッシュフローを取得
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
        Returns:
            pd.DataFrame: キャッシュフローのDataFrame
        """
        ticker_info = self._resolve_ticker_info(code, market)
        if ticker_info is None:
            return pd.DataFrame()
        return self._get_frame_from_ticker(ticker_info, "cashflow")
    
    def _get_earnings(self, code: str, market: str | None) -> pd.DataFrame:
        """
        直近４年分の収益を取得
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
        Returns:
            pd.DataFrame: 収益のDataFrame
        """
        ticker_info = self._resolve_ticker_info(code, market)
        if ticker_info is None:
            return pd.DataFrame()
        income_stmt_df = self._get_frame_from_ticker(ticker_info, "income_stmt")
        return self._extract_earnings_frame(income_stmt_df)
    
    def _get_quarterly_earnings(self, code: str, market: str | None) -> pd.DataFrame:
        """
        直近４年分の四半期収益を取得
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
        Returns:
            pd.DataFrame: 四半期収益のDataFrame
        """
        ticker_info = self._resolve_ticker_info(code, market)
        if ticker_info is None:
            return pd.DataFrame()
        quarterly_income_stmt_df = self._get_frame_from_ticker(ticker_info, "quarterly_income_stmt")
        return self._extract_earnings_frame(quarterly_income_stmt_df)
    
    def get_financial_statements(
        self,
        code: str,
        market: str,
        start: str | date | None = None,
        end: str | date | None = None,
    ) -> list[Financials]:
        """
        trn_financialsテーブルから財務諸表を取得
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
            start (str | date | None): 開始日（YYYY-MM-DD）
            end (str | date | None): 終了日（YYYY-MM-DD）
        Returns:
            list[Financials]: 財務諸表ORMエンティティのリスト
        """
        stmt = select(Financials).where(
            Financials.code == code,
            Financials.market == market,
        )

        if start is not None:
            start_date = date.fromisoformat(start) if isinstance(start, str) else start
            stmt = stmt.where(Financials.date >= start_date)
        if end is not None:
            end_date = date.fromisoformat(end) if isinstance(end, str) else end
            stmt = stmt.where(Financials.date <= end_date)

        return self._db_session.execute(stmt.order_by(Financials.date.asc())).scalars().all()

    def get_balance_sheet(
        self,
        code: str,
        market: str,
        start: str | date | None = None,
        end: str | date | None = None,
    ) -> list[BalanceSheet]:
        """
        trn_balance_sheetテーブルからバランスシートを取得
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
            start (str | date | None): 開始日（YYYY-MM-DD）
            end (str | date | None): 終了日（YYYY-MM-DD）
        Returns:
            list[BalanceSheet]: バランスシートORMエンティティのリスト
        """
        stmt = select(BalanceSheet).where(
            BalanceSheet.code == code,
            BalanceSheet.market == market,
        )

        if start is not None:
            start_date = date.fromisoformat(start) if isinstance(start, str) else start
            stmt = stmt.where(BalanceSheet.date >= start_date)
        if end is not None:
            end_date = date.fromisoformat(end) if isinstance(end, str) else end
            stmt = stmt.where(BalanceSheet.date <= end_date)

        return self._db_session.execute(stmt.order_by(BalanceSheet.date.asc())).scalars().all()

    def get_cashflow(
        self,
        code: str,
        market: str,
        start: str | date | None = None,
        end: str | date | None = None,
    ) -> list[CashFlow]:
        """
        trn_cash_flowテーブルからキャッシュフローを取得
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
            start (str | date | None): 開始日（YYYY-MM-DD）
            end (str | date | None): 終了日（YYYY-MM-DD）
        Returns:
            list[CashFlow]: キャッシュフローORMエンティティのリスト
        """
        stmt = select(CashFlow).where(
            CashFlow.code == code,
            CashFlow.market == market,
        )

        if start is not None:
            start_date = date.fromisoformat(start) if isinstance(start, str) else start
            stmt = stmt.where(CashFlow.date >= start_date)
        if end is not None:
            end_date = date.fromisoformat(end) if isinstance(end, str) else end
            stmt = stmt.where(CashFlow.date <= end_date)

        return self._db_session.execute(stmt.order_by(CashFlow.date.asc())).scalars().all()

    def get_earnings(
        self,
        code: str,
        market: str,
        start: str | date | None = None,
        end: str | date | None = None,
    ) -> list[IncomeStatement]:
        """
        trn_income_stmtテーブルから収益を取得
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
            start (str | date | None): 開始日（YYYY-MM-DD）
            end (str | date | None): 終了日（YYYY-MM-DD）
        Returns:
            list[IncomeStatement]: 収益ORMエンティティのリスト
        """
        stmt = select(IncomeStatement).where(
            IncomeStatement.code == code,
            IncomeStatement.market == market,
        )

        if start is not None:
            start_date = date.fromisoformat(start) if isinstance(start, str) else start
            stmt = stmt.where(IncomeStatement.date >= start_date)
        if end is not None:
            end_date = date.fromisoformat(end) if isinstance(end, str) else end
            stmt = stmt.where(IncomeStatement.date <= end_date)

        return self._db_session.execute(stmt.order_by(IncomeStatement.date.asc())).scalars().all()

    def get_quarterly_earnings(
        self,
        code: str,
        market: str,
        start: str | date | None = None,
        end: str | date | None = None,
    ) -> list[QuarterlyIncomeStatement]:
        """
        trn_quarterly_income_stmtテーブルから四半期収益を取得
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
            start (str | date | None): 開始日（YYYY-MM-DD）
            end (str | date | None): 終了日（YYYY-MM-DD）
        Returns:
            list[QuarterlyIncomeStatement]: 四半期収益ORMエンティティのリスト
        """
        stmt = select(QuarterlyIncomeStatement).where(
            QuarterlyIncomeStatement.code == code,
            QuarterlyIncomeStatement.market == market,
        )

        if start is not None:
            start_date = date.fromisoformat(start) if isinstance(start, str) else start
            stmt = stmt.where(QuarterlyIncomeStatement.date >= start_date)
        if end is not None:
            end_date = date.fromisoformat(end) if isinstance(end, str) else end
            stmt = stmt.where(QuarterlyIncomeStatement.date <= end_date)

        return self._db_session.execute(stmt.order_by(QuarterlyIncomeStatement.date.asc())).scalars().all()
    
    def convert_data_structure(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        財務データのDataFrameを日付をインデックスに持つ形式に変換
        Args:
            df (pd.DataFrame): 変換前のDataFrame
        Returns:
            pd.DataFrame: 変換後のDataFrame
        """
        if df.empty:
            return df
        converted_df = df.T.copy()
        # yfinance のタイトルケース列を ORM モデルの snake_case に正規化する。
        converted_df.columns = [
            re.sub(r"[^a-z0-9]+", "_", str(col).strip().lower()).strip("_")
            for col in converted_df.columns
        ]
        converted_df.index = pd.to_datetime(converted_df.index).strftime("%Y-%m-%d")
        converted_df = converted_df.reset_index().rename(columns={"index": "Date"})
        converted_df['code'] = self._code
        converted_df['market'] = self._market
        return converted_df
