import datetime as dt
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.api.v1.infra.get_market_data import GetMarketData
from app.core.logger import logger
from app.models.currency import Currency
from app.models.commodities import Commodities
from app.models.commodity_price import CommodityPrice
from app.db.session import SessionLocal

class CommodityDataService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.get_market_data = GetMarketData(data_path=Path("/tmp"))


    def update_commodity_data(
        self,
        code: str,
        market: str | None,
        start: dt.date | None = None,
        end: dt.date | None = None,
    ) -> bool:
        try:
            if start is None or end is None:
                raise ValueError("start and end are required")
            if start > end:
                raise ValueError("start must be less than or equal to end")
            
            fetch_start = start - dt.timedelta(days=45)
            # TODO: 市場に応じた通貨IDを取得するようにする
            #currency_id = self._get_currency_id(market)
            currency_id = None



            db_rows = self._fetch_trn_commodity_price_rows(code, market, fetch_start, end)
            db_dates = {row.date for row in db_rows}

            commodity_exists = self._exists_commodity(code, market)
            fetched_rows: list[dict] = []
            
            if not commodity_exists:
                fetched_rows = self._fetch_yfinance(code, market, fetch_start, end)
                logger.info(f"[DEBUG] fetch_yfinance({code}, {market}, {fetch_start}, {end}) -> {len(fetched_rows)} rows")
                logger.info(f"[DEBUG] fetch_yfinance sample row: {fetched_rows[0] if fetched_rows else 'no data'}")
                if fetched_rows:
                    logger.info(f"[DEBUG] Upserting commodity: code={code}, market={market}, currency_id={currency_id}")
                    result = self._upsert_commodity(code, market, currency_id)
                    logger.info(f"[DEBUG] _upsert_commodity result: {result}")
                else:
                    logger.warning(f"No market data found for code={code}, market={market}")
                    return False
                
            if not fetched_rows:
                fetched_rows = self._fetch_yfinance(code, market, fetch_start, end)
                logger.info(f"[DEBUG] fetch_yfinance({code}, {market}, {fetch_start}, {end}) -> {len(fetched_rows)} rows (fallback)")
            
            normalized_rows = self._normalize_rows(fetched_rows)
            fetched_dates = {row["date"] for row in normalized_rows if row["date"] is not None}
            missing_dates = fetched_dates - db_dates

            if not db_rows or missing_dates:
                logger.info(f"[DEBUG] upsert_trn_commodity_price({code}, {market}, rows={len(normalized_rows)})")
                self._upsert_trn_commodity_price(code, market, normalized_rows)

            return True
        except ValueError:
            logger.error(f"Invalid input for update_commodity_data: code={code}, market={market}, start={start}, end={end}")
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error fetching {code}: {e}")
            raise RuntimeError(f"commodity data update failed for {code}") from e

    def _exists_commodity(self, code: str, market: str | None) -> bool:
        stmt = select(Commodities.id).where(Commodities.code == code)
        if market is not None:
            stmt = stmt.where(Commodities.market == market)
        return self.db_session.execute(stmt.limit(1)).first() is not None

    def _upsert_commodity(self, code: str, market: str | None, currency_id: int | None) -> bool:
        if self._exists_commodity(code, market):
            return False
        self.db_session.add(Commodities(code=code, market=market, currency_id=currency_id))
        self.db_session.flush()
        return True

    def _fetch_yfinance(self, code: str, market: str | None, start: dt.date, end: dt.date) -> list[dict]:
        try:
            ticker = self._build_yfinance_ticker(code=code, market=market)
            return self.get_market_data.get_data_from_yfinance(
                ticker,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
            )
        except Exception as e:
            logger.error(f"Error fetching {code} from yfinance: {e}")
            raise RuntimeError(f"yfinance fetch failed for {code}") from e

    def _build_yfinance_ticker(self, code: str, market: str | None) -> str:
        normalized_code = code.strip()
        if not normalized_code:
            raise ValueError("code is required")
        if market is None:
            return normalized_code
        normalized_market = market.strip().upper()
        if not normalized_market:
            return normalized_code
        if normalized_code.endswith("=F"):
            return normalized_code
        return f"{normalized_code}=F"

    def _normalize_rows(self, fetched_rows: list[dict]) -> list[dict]:
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
                    "adj_close": row.get("adj_close"),
                    "volume": row.get("volume"),
                }
            )
        return normalized_rows

    def _upsert_trn_commodity_price(
        self,
        code: str,
        market: str | None,
        normalized_rows: list[dict]
    ) -> None:
        """
         PostgreSQL の ON CONFLICT を使用して、trn_commodity_price テーブルに対してバルク UPSERT を行う
        Args:
            code (str): コモディティコード
            market (str | None): 市場コード（省略可）
            normalized_rows (list[dict]): 正規化されたコモディティ価格データのリスト
        Returns:            None: データの挿入/更新のみ行う
        Raises:            ValueError: コモディティが見つからない場合
            RuntimeError: データベース操作に失敗した場合
        """
        # --- 1. commodity_id を取得 ---
        stmt = select(Commodities.id).where(Commodities.code == code)
        if market is not None:
            stmt = stmt.where(Commodities.market == market)

        commodity_id = self.db_session.execute(stmt.limit(1)).scalar_one_or_none()
        if commodity_id is None:
            raise ValueError(f"Commodity not found: code={code}, market={market}")

        # --- 2. INSERT 用の値を整形 ---
        values = [
            {
                "commodity_id": commodity_id,
                "commodity_code": code,
                "date": row["date"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "adj_close": row["adj_close"],
                "volume": row["volume"],
            }
            for row in normalized_rows
            if row["date"] is not None
        ]

        if not values:
            return

        # --- 3. PostgreSQL 専用バルク UPSERT ---
        BATCH_SIZE = 50

        for i in range(0, len(values), BATCH_SIZE):
            batch = values[i:i + BATCH_SIZE]

            stmt = insert(CommodityPrice).values(batch)

            # ★ ここが最重要：正しい UNIQUE 制約名を指定する
            stmt = stmt.on_conflict_do_update(
                constraint="uq_trn_commodity_price_code_market_date",
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "adj_close": stmt.excluded.adj_close,
                    "volume": stmt.excluded.volume,
                },
            )

            self.db_session.execute(stmt)

        # --- 4. コミット ---
        self.db_session.commit()


    def _fetch_trn_commodity_price_rows(
        self,
        code: str,
        market: str | None,
        start: dt.date,
        end: dt.date,
    ) -> list[CommodityPrice]:
        stmt = select(CommodityPrice).join(Commodities, CommodityPrice.commodity_id == Commodities.id).where(
            Commodities.code == code,
            CommodityPrice.date >= start,
            CommodityPrice.date <= end,
        )
        if market is not None:
            stmt = stmt.where(Commodities.market == market)
        return self.db_session.execute(stmt.order_by(CommodityPrice.date.asc())).scalars().all()

    def _fetch_commodity_price(self, code: str, market: str, start: dt.date | None = None, end: dt.date | None = None) -> list[dict] | None:
        try:
            final_rows = self._fetch_trn_commodity_price_rows(code, market, start, end)
            return [
                {
                    "commodity_id": row.commodity_id,
                    "date": row.date.isoformat(),
                    "open": row.open,
                    "high": row.high,
                    "low": row.low,
                    "close": row.close,
                    "adj_close": row.adj_close,
                    "volume": row.volume,
                }
                for row in final_rows
            ]
        except Exception as e:
            logger.error(f"Error fetching {code}: {e}")
            raise RuntimeError(f"commodity data fetch failed for {code}") from e

    def _get_currency_id(self, market: str | None) -> int | None:
        if market is None:
            return None
        row = self.db_session.execute(
            select(Currency.id).where(Currency.market == market)
        ).scalar_one_or_none()
        return row

    def get_commodity_data(
        self, 
        code: str, 
        market: str, 
        start: dt.date | None = None, 
        end: dt.date | None = None
    ) -> list[dict] | None:
        """
        指定されたコードと市場に対して、期間内のコモディティ価格データを取得する
        Args:
            code (str): コモディティコード
            market (str): 市場コード
            start (dt.date | None): 取得開始日（省略時は過去1年）
            end (dt.date | None): 取得終了日（省略時は当日）
        Returns:
            list[dict] | None: 取得したコモディティ価格データ（存在しない場合はNone）
        """
        try:
            data = self._fetch_commodity_price(code=code, market=market, start=start, end=end)
            if not data:
                return None
            return data
        except Exception as e:
            logger.error(f"Error fetching commodity data for {code} in {market}: {e}")
            raise RuntimeError(f"commodity data fetch failed for {code} in {market}") from e
        
    def _fetch_commodity_price(self, code: str, market: str, start: dt.date | None = None, end: dt.date | None = None) -> list[dict] | None:
        try:
            rows = self._fetch_trn_commodity_price_rows(code, market, start, end)
            return [
                {
                    "commodity_id": row.commodity_id,
                    "date": row.date.isoformat(),
                    "open": row.open,
                    "high": row.high,
                    "low": row.low,
                    "close": row.close,
                    "adj_close": row.adj_close,
                    "volume": row.volume,
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error fetching commodity price for {code}: {e}")
            raise RuntimeError(f"commodity price fetch failed for {code}") from e