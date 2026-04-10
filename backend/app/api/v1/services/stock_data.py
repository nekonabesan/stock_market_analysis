import datetime as dt
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.api.v1.infra.get_market_data import GetMarketData
from app.core.logger import logger
from app.models.stocks import Stock
from app.models.trn_stock_price import StockPrice

get_market_data = GetMarketData(data_path=Path("/tmp"))

# Yahoo Financeの市場識別コード -> ティッカーサフィックス
YF_MARKET_SUFFIX_MAP: dict[str, str] = {
    "TSE": ".T",
    "JPX": ".T",
    "HKEX": ".HK",
    "SSE": ".SS",
    "SZSE": ".SZ",
    "LSE": ".L",
    "TSX": ".TO",
    "ASX": ".AX",
    # 米国市場はサフィックス無し
    "NYSE": "",
    "NASDAQ": "",
    "AMEX": "",
}


class StockDataService:
    def __init__(self, db_session):
        """
        StockDataServiceを初期化する
        Args:
            db_session (Session): DBセッション
        Returns:
            None: 初期化のみ行う
        """
        self.db_session = db_session

    def update_stock_data (
            self,
            code: str,
            market: str | None,
            start: dt.date | None,
            end: dt.date | None,
        ) -> bool:
        """
        指定条件の株価データを更新し、必要に応じてDBを補完する
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード（Noneの場合は市場不特定）
            start (dt.date | None): データ取得開始日
            end (dt.date | None): データ取得終了日
        Returns:
            bool: 更新処理の実行結果
        """
        try:
            # 期間指定は必須で扱い、業務的に不正な期間は先に弾く。
            if start is None or end is None:
                raise ValueError("start and end are required")
            if start > end:
                raise ValueError("start must be less than or equal to end")

            # stock登録と価格UPSERTを単一トランザクションで実行する。
            with self.db_session.begin():
                # まず指定期間のDB既存データを取得し、欠損判定の基準を作る。
                db_rows = self._fetch_trn_stock_price_rows(code, market, start, end)
                db_dates = {row.date for row in db_rows}

                # TODO実装: stock テーブルに code + market の組み合わせがあるか確認する。
                stock_exists = self._exists_stock(code, market)
                fetched_rows: list[dict] = []

                # TODO実装: 未登録なら yfinance 取得を試行し、結果に応じて登録 or 404 を出し分ける。
                if not stock_exists:
                    fetched_rows = self._fetch_yfinance(code, market, start, end)
                    if fetched_rows:
                        # TODO実装: yfinance で取得できた場合は mst_stock へ登録する。
                        self._upsert_stock(code, market)
                    else:
                        # TODO実装: 未登録かつ外部取得不能なら 404 を返す。
                        logger.warning(f"No market data found for code={code}, market={market}")
                        return False

                # 欠損判定のため、未取得ならここで取得する。
                if not fetched_rows:
                    fetched_rows = self._fetch_yfinance(code, market, start, end)

                normalized_rows = self._normalize_rows(fetched_rows)
                fetched_dates = {row["date"] for row in normalized_rows if row["date"] is not None}
                missing_dates = fetched_dates - db_dates

                # 期間内が空、または一部欠損なら OHLCV をUPSERTして整合させる。
                if not db_rows or missing_dates:
                    self._upsert_trn_stock_price(code, market, normalized_rows)

            # 更新処理が最後まで完了した場合は成功を返す。
            return True
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching {code}: {e}")
            raise RuntimeError(f"stock data update failed for {code}") from e
        
    def get_stock_data(
        self,
        code: str,
        market: str | None,
        start: dt.date | None,
        end: dt.date | None,
    ) -> list[dict] | None:
        """
        指定条件の株価データをDBから取得する
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード（Noneの場合は市場不特定）
            start (dt.date | None): データ取得開始日
            end (dt.date | None): データ取得終了日
        Returns:
            list[dict] | None: 取得した株価データ（存在しない場合はNone）
        """
        try:
            if start is None or end is None:
                raise ValueError("start and end are required")
            if start > end:
                raise ValueError("start must be less than or equal to end")

            data = self._fetch_trn_stock_price(code, market, start, end)
            if not data:
                return None
            return data
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching {code}: {e}")
            raise RuntimeError(f"stock data fetch failed for {code}") from e

    def _exists_stock(self, code: str, market: str | None) -> bool:
        """
        mst_stockテーブルにcodeとmarketの組み合わせが存在するか確認する
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード（Noneの場合は市場不特定）
        Returns:
            bool: 存在する場合はTrue
        """
        stmt = select(Stock.id).where(Stock.code == code)
        if market is not None:
            stmt = stmt.where(Stock.market == market)
        return self.db_session.execute(stmt.limit(1)).first() is not None

    def _upsert_stock(self, code: str, market: str | None) -> None:
        """
        mst_stockテーブルへ銘柄情報を登録する
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード（Noneの場合は市場不特定）
        Returns:
            None: 登録処理のみ行う
        """
        # 同一 code + market が未登録なら mst_stock へ最小情報で追加する。
        if self._exists_stock(code, market):
            return

        self.db_session.add(Stock(code=code, market=market))

    def _fetch_yfinance(self, code: str, market: str | None, start: dt.date, end: dt.date) -> list[dict]:
        """
        yfinanceから指定期間のデータを取得する
        Args:
            code (str): 銘柄コード
            market (str | None): Yahoo市場識別コード
            start (dt.date): データ取得開始日
            end (dt.date): データ取得終了日
        Returns:
            list[dict]: 指定期間のOHLCVデータ
        """
        try:
            ticker = self._build_yfinance_ticker(code=code, market=market)
            return get_market_data.get_data_from_yfinance(
                ticker,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
            )
        except Exception as e:
            logger.error(f"Error fetching {code} from yfinance: {e}")
            raise RuntimeError(f"yfinance fetch failed for {code}") from e

    def _build_yfinance_ticker(self, code: str, market: str | None) -> str:
        """
        code と market から yfinance 用ティッカーを構築する
        Args:
            code (str): 銘柄コード
            market (str | None): Yahoo市場識別コード（例: TSE, HKEX, NASDAQ, .T）
        Returns:
            str: yfinance に渡すティッカー
        """
        normalized_code = code.strip()
        if not normalized_code:
            raise ValueError("code is required")

        # 既にサフィックス付きならそのまま使う。
        if "." in normalized_code:
            return normalized_code

        if market is None:
            return normalized_code

        normalized_market = market.strip().upper()
        if not normalized_market:
            return normalized_code

        # ".T" のようなサフィックス直接指定も許可する。
        if normalized_market.startswith("."):
            suffix = normalized_market
        else:
            suffix = YF_MARKET_SUFFIX_MAP.get(normalized_market, f".{normalized_market}")

        if suffix and normalized_code.upper().endswith(suffix):
            return normalized_code

        return f"{normalized_code}{suffix}"

    def _normalize_rows(self, fetched_rows: list[dict]) -> list[dict]:
        """
        yfinanceの返却データをOHLCV形式に正規化する
        Args:
            fetched_rows (list[dict]): yfinanceから取得した生データ
        Returns:
            list[dict]: 正規化済みOHLCVデータ
        """
        normalized_rows: list[dict] = []
        for row in fetched_rows:
            row_date = row.get("date")
            if hasattr(row_date, "date"):
                row_date = row_date.date()
            normalized_rows.append(
                {
                    "date": row_date,
                    "open": row.get("open"),
                    "high": row.get("high"),
                    "low": row.get("low"),
                    "close": row.get("close"),
                    "volume": row.get("volume"),
                }
            )
        return normalized_rows

    def _upsert_trn_stock_price(self, code: str, market: str | None, normalized_rows: list[dict]) -> None:
        """
        trn_stock_priceテーブルへOHLCVデータをUPSERTする
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード（Noneの場合は市場不特定）
            normalized_rows (list[dict]): 正規化済みOHLCVデータ
        Returns:
            None: UPSERT処理のみ行う
        """
        values = [
            {
                "stock_code": code,
                "stock_market": market,
                "date": row["date"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"],
            }
            for row in normalized_rows
            if row["date"] is not None
        ]
        if not values:
            return

        # stock_market が NULL の場合、UNIQUE制約で衝突判定されないため先に削除する。
        if market is None:
            for value in values:
                target_row = self.db_session.execute(
                    select(StockPrice).where(
                        StockPrice.stock_code == code,
                        StockPrice.stock_market.is_(None),
                        StockPrice.date == value["date"],
                    )
                ).scalar_one_or_none()
                if target_row is not None:
                    target_row.open = value["open"]
                    target_row.high = value["high"]
                    target_row.low = value["low"]
                    target_row.close = value["close"]
                    target_row.volume = value["volume"]
                else:
                    self.db_session.add(StockPrice(**value))
            return

        upsert_stmt = insert(StockPrice).values(values)
        upsert_stmt = upsert_stmt.on_conflict_do_update(
            index_elements=["stock_code", "stock_market", "date"],
            set_={
                "open": upsert_stmt.excluded.open,
                "high": upsert_stmt.excluded.high,
                "low": upsert_stmt.excluded.low,
                "close": upsert_stmt.excluded.close,
                "volume": upsert_stmt.excluded.volume,
            },
        )
        self.db_session.execute(upsert_stmt)

    def _fetch_trn_stock_price_rows(
        self,
        code: str,
        market: str | None,
        start: dt.date,
        end: dt.date,
    ) -> list[StockPrice]:
        """
        trn_stock_priceテーブルからORM行データを取得する
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード（Noneの場合は市場不特定）
            start (dt.date): データ取得開始日
            end (dt.date): データ取得終了日
        Returns:
            list[StockPrice]: 指定期間の株価行データ
        """
        stmt = select(StockPrice).where(
            StockPrice.stock_code == code,
            StockPrice.date >= start,
            StockPrice.date <= end,
        )
        if market is not None:
            stmt = stmt.where(StockPrice.stock_market == market)
        return self.db_session.execute(stmt.order_by(StockPrice.date.asc())).scalars().all()

    def _fetch_trn_stock_price(self, code: str, market: str | None, start: dt.date, end: dt.date) -> list[dict]:
        """
        trn_stock_priceテーブルからデータを取得する
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード（Noneの場合は市場不特定）
            start (dt.date): データ取得開始日
            end (dt.date): データ取得終了日
        Returns:
            list[dict]: 指定期間のOHLCVデータ
        """
        try:
            # 呼び出し元へ返すデータは、最終的にDB上の正データを返却する。
            final_rows = self._fetch_trn_stock_price_rows(code, market, start, end)
            return [
                {
                    "code": row.stock_code,
                    "market": row.stock_market,
                    "date": row.date.isoformat(),
                    "open": row.open,
                    "high": row.high,
                    "low": row.low,
                    "close": row.close,
                    "volume": row.volume,
                }
                for row in final_rows
            ]
        except Exception as e:
            logger.error(f"Error fetching {code}: {e}")
            raise RuntimeError(f"stock data fetch failed for {code}") from e

        
