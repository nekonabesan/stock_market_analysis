from typing import Any

import pandas as pd
import yfinance as yf


class CorporateFinanceData:
    EARNINGS_ROW_CANDIDATES = {
        "Revenue": ["Total Revenue", "Operating Revenue", "Revenue"],
        "Earnings": [
            "Net Income",
            "Net Income Common Stockholders",
            "Net Income Including Noncontrolling Interests",
        ],
    }

    def __init__(self, code: str | None = None, market: str | None = None):
        self._code = code
        self._market = market
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
            print(f"Error fetching ticker object for code={code}, market={market}: {e}")
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
            print(f"Error reading {attr_name}: {e}")
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
    
    def get_financial_statements(self, code: str, market: str | None) -> pd.DataFrame:
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
    
    def get_balance_sheet(self, code: str, market: str | None) -> pd.DataFrame:
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
    
    def get_cashflow(self, code: str, market: str | None) -> pd.DataFrame:
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
    
    def get_earnings(self, code: str, market: str | None) -> pd.DataFrame:
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
    
    def get_quarterly_earnings(self, code: str, market: str | None) -> pd.DataFrame:
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
        converted_df.index = pd.to_datetime(converted_df.index).strftime("%Y-%m-%d")
        converted_df = converted_df.reset_index().rename(columns={"index": "Date"})
        converted_df['code'] = self._code
        converted_df['market'] = self._market
        return converted_df
