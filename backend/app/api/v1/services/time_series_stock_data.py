import datetime as dt
import pandas as pd
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.trn_stock_price import StockPrice
from .time_series_data import TimeSeriesDataService



class TimeSeriesStockDataService(TimeSeriesDataService):
    def __init__(self, db_session: Session):
        """
        TimeSeriesDataServiceを初期化する
        Args:
            db_session (Session): DBセッション
        Returns:
            None: 初期化のみ行う
        """
        super().__init__(db_session)

    def get_time_series_data(
        self,
        code: str,
        market: str | None,
        start: dt.date | None,
        end: dt.date | None,
        db: Session | None = None,
    ) -> list[dict]:
        """
        指定されたコードと市場に対して、期間内の株価データを取得する
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード（省略可）
            start (dt.date | None): 取得開始日（省略時は過去1年）
            end (dt.date | None): 取得終了日（省略時は当日）
            db (Session | None): DBセッション（省略時はインスタンスのセッションを使用）
        Returns:
            list[dict]: 取得した株価データのリスト
        """
        try:
            if start is None or end is None:
                raise ValueError("start and end are required")
            if start > end:
                raise ValueError("start must be less than or equal to end")

            # DBからデータを取得する
            session = db or self.db_session
            data_acquisition_start_date = start - dt.timedelta(days=300)
            query = (session.query(StockPrice)
                        .filter(StockPrice.stock_code == code)
                        .filter(StockPrice.date >= data_acquisition_start_date)
                        .filter(StockPrice.date <= end))
            if market is not None:
                query = query.filter(StockPrice.stock_market == market)

            data = query.all()
            if not data:
                return []
            # 取得したデータをDataFrameに変換し、時系列データを生成する
            df = pd.DataFrame([self._row_to_dict(record) for record in data])
            if df.empty or "date" not in df.columns or "close" not in df.columns:
                return []
            # superクラスのget_time_series_dataを呼び出して、時系列データを生成する
            return super().get_time_series_data(df)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching time series data: {e}")
            raise RuntimeError("time series data fetch failed") from e