import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import requests

import plotly.graph_objs as go
import talib as ta
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
import mplfinance as mpf
import matplotlib.dates as mdates
from backtesting import Backtest, Strategy
from Modules.rci import Rci

class metrics:
    def __init__(self, utility):
        self.utility = utility
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

    def _get_stocks_datas(
            self, 
            company_names: list[dict], 
            start: str, 
            end: str
    ) -> pd.DataFrame:
        get_url = f"{self.api_base_url}/api/v1/stock/get"

        # データ取得期間を作成
        end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()
        start_date = dt.datetime.strptime(start, "%Y-%m-%d").date() - dt.timedelta(days=365 * 2)

        # 空のリストを用意
        data_frames = []

        for company in company_names:
            code = company["code"]
            market = company["market"]

            # APIへRequestしデータを取得
            get_params = {
                "code": code,
                "market": market,
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
            }

            response = requests.get(get_url, params=get_params, timeout=60)
            if response.status_code != 200:
                print(f"GET failed: code={code}, status={response.status_code}, body={response.text}")
                continue

            payload = response.json()
            rows = payload.get("results", [])
            if not rows:
                print(f"No rows returned: code={code}")
                continue

            # APIレスポンス(list[dict])からDataFrameを作成
            df = pd.DataFrame(rows)

            # date列を日付型に揃える
            df["date"] = pd.to_datetime(df["date"]).dt.date

            # 銘柄コードを追加
            df["Stock"] = str(code)

            # 統合用のリストに追加
            data_frames.append(df)

        if not data_frames:
            raise ValueError("対象期間のデータが1件も取得できませんでした")

        # 全データを連結
        df = pd.concat(data_frames, ignore_index=True)

        # インデックスを設定（マルチインデックス化）
        df = df.set_index(["Stock", "date"])

        # 指定した期間のデータを抽出
        filter_start = dt.datetime.strptime(start, "%Y-%m-%d").date()
        filter_end = dt.datetime.strptime(end, "%Y-%m-%d").date()

        filtered_df = df.loc[
            (df.index.get_level_values("date") >= filter_start)
            & (df.index.get_level_values("date") <= filter_end)
        ]

        return filtered_df
        
    def calc_daily_returns_and_cumulative(
        self, 
        initial_investment: int,
        filtered_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        日次リターン・累積資産額の計算
            Args:
                initial_investment (int): 初期投資額
                filtered_df (pd.DataFrame): 銘柄コードと日付をインデックスとするDataFrame
            Returns:
                pd.DataFrame: 日次リターンと累積資産額を含むDataFrame
        """
        # 結果を格納する空のリスト
        result_list = []

        # filtered_dfから銘柄コードを取得
        codes = filtered_df.index.get_level_values("Stock").unique()

        for ticker in codes:
            # 銘柄ごとにデータを抽出
            ticker_data = filtered_df.loc[ticker].copy()  # コピーを作成
            ticker_data = ticker_data.reset_index()
            
            # 日次リターンを計算
            ticker_data["Daily Return"] = ticker_data["close"].pct_change()
        
            # 累積リターンを考慮した資産額を算出
            ticker_data["Asset Value"] = initial_investment * (1 + ticker_data["Daily Return"]).cumprod()

            # データフレームをリストに格納
            ticker_data["Stock"] = ticker
            result_list.append(ticker_data)

        # 全データを連結
        df = pd.concat(result_list)
        df = df.set_index(["Stock", "date"]) 

        return df
        
    
    