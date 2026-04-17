from sqlalchemy import select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.stocks import Stock
from app.models.currency import Currency

class StocksService:
    def __init__(self, db_session: Session):
        """
        StocksServiceを初期化する
        Args:
            db_session (Session): DBセッション
        Returns:
            None: 初期化のみ行う
        """
        self.db_session = db_session

    def get_stock_data(self) -> list[dict] | None:
        """
        mst_stockテーブルに登録済みの全銘柄をDBから取得する

        Returns:
            list[dict] | None: 取得した株価データ（存在しない場合はNone）
        """
        try:
            data = self._fetch_stocks()
            if not data:
                return None
            return data
        except Exception as e:
            logger.error(f"Error fetching stock data: {e}")
            raise RuntimeError("stock data fetch failed") from e
        
    def _fetch_stocks(self) -> list[dict] | None:
        """
        DBから全銘柄を取得し、通貨名も付与する内部メソッド

        Returns:
            list[dict] | None: 取得した株価データ（存在しない場合はNone）
        """
        stmt = (
            select(Stock, Currency.currency)
            .join(Currency, Stock.currency_id == Currency.id, isouter=True)
        )
        result = self.db_session.execute(stmt).all()
        if not result:
            return None
        stocks = []
        for stock, currency in result:
            stock_dict = self._to_dict(stock)
            stock_dict["currency"] = currency
            stocks.append(stock_dict)
        return stocks

    def _to_dict(self, stock: Stock) -> dict:
        """Stockモデルをdictへ変換する。"""
        if hasattr(stock, "to_dict") and callable(stock.to_dict):
            return stock.to_dict()

        mapper = inspect(Stock)
        return {column.key: getattr(stock, column.key) for column in mapper.columns}