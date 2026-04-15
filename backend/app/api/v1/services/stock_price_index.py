import datetime as dt

from sqlalchemy.orm import Session

from app.api.v1.services.time_series_data import TimeSeriesDataService
from app.api.v1.services.stock_data import StockDataService
from app.core.config import IndexDefinition, INDICES
from app.core.logger import logger


class StockPriceIndexService(TimeSeriesDataService):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.indices: list[IndexDefinition] = INDICES

    def update_index_data(
        self,
        code: str,
        market: str | None,
        start: dt.date,
        end: dt.date,
    ) -> bool:
        """
        指定されたシンボルの株価インデクスデータを更新する
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
            start (datetime.date | None): データ取得開始日
            end (datetime.date | None): データ取得終了日
        Returns:
            bool: 更新が成功したかどうか
        """
        return self._update_index_data(code, market, start, end)

    def update_all_index_data(
        self,
        start: dt.date,
        end: dt.date,
    ) -> bool:
        """
        全てのインデクスの時系列データを更新する
        Args:
            code (str): 銘柄コード("ALL"固定)
            market (str | None): 市場コード（"ALL"固定）
            start (datetime.date | None): データ取得開始日
            end (datetime.date | None): データ取得終了日
        Returns:
            bool: 更新が成功したかどうか
        """
        try:
            for index in self.indices:
                self._update_index_data(index.code, index.market, start, end)
            return True
        except Exception as e:
            logger.error(f"Error updating all indices: {e}")
            raise RuntimeError("Failed to update all indices") from e

    def _update_index_data(
            self,
            code: str,
            market: str | None,
            start: dt.date,
            end: dt.date,
    ) -> bool:
        """
        指定されたシンボルの株価インデクスデータを更新する
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
            start (datetime.date | None): データ取得開始日
            end (datetime.date | None): データ取得終了日
        Returns:
            bool: 更新が成功したかどうか
        """
        try:
            stock_data_service = StockDataService(self.db_session)
            stock_data_service.update_stock_data(code, market, start, end)
            return True
        except Exception as e:
            logger.error(f"Error fetching {code}: {e}")
            raise RuntimeError(f"stock data update failed for {code}") from e

    def get_index_data(
            self,
            code: str,
            market: str | None,
            start: dt.date,
            end: dt.date,
    ) -> list[dict] | None:
        """
        指定されたシンボルの株価インデクスデータを返す
        """
        stock_data_service = StockDataService(self.db_session)
        return stock_data_service.get_stock_data(code, market, start, end)

