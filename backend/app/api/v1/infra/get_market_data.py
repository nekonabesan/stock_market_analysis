from pathlib import Path
import pandas as pd
import yfinance as yf

from app.core.logger import logger

class GetMarketData:
    def __init__(self, data_path: Path):
        self.data_path = data_path
    
    def get_data_from_yfinance(self, ticker: str, start: str, end: str) -> list[dict]:
        """
        yfinance から OHLCV を取得し、辞書リストで返却。
        
        Args:
            ticker (str): 銘柄コード（例: "7203.T"）
            start (str): データ取得開始日（例: "2024-01-01"）
            end (str): データ取得終了日（例: "2024-01-31"）
        Returns:
            list[dict]: OHLCV データの辞書リスト
        """
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)
            
            # インデックスをリセット（日付をカラム化）
            df = df.reset_index()
            
            # 列名を統一（yfinance が大文字で返す場合）
            df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            
            # 辞書リストに変換
            return df.to_dict('records')
        
        except Exception as e:
            logger.error(f"Error fetching {ticker}: {e}")
            raise RuntimeError(f"yfinance fetch failed for {ticker}") from e
