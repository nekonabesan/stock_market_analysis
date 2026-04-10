import os
from dotenv import load_dotenv
from pathlib import Path
import datetime
import pandas as pd
import yfinance as yf
import numpy as np


class GetMarketData:
    def __init__(self, data_path: Path):
        self.data_path = data_path

    def get_csv_data(self, filepath) -> pd.DataFrame:
        # CSVファイルから株価を読み込み
        df = pd.read_csv(self.data_path / filepath, index_col=0, parse_dates=True)
        return df
    
    def get_data_from_yfinance(self, tickers: list[str], start: str = None, end: str = None) -> pd.DataFrame:
        # yfinanceから株価を取得
        df = yf.download(tickers, start=start, end=end)
        return df
    
    def convert_prices_to_returns(self, price_df, method='simple'):
        if method == 'simple':
             returns = price_df.pct_change()
        elif method == 'log':
            returns = np.log(price_df / price_df.shift(1))
        else:
            raise ValueError("method must be 'simple' or 'log'")
        return returns.dropna()