import os
import datetime as dt
import pandas as pd
import numpy as np
from Modules.reques_api import RequestApi

class ClassStockPricesMarketData:
    """
    ◆ 1. 株価・市場データを導出するクラス
    • 現在株価（Price）
    • 時価総額（Market Cap）
    • 出来高（Volume）
    • 52週高値・安値
    • Beta（ボラティリティ指標）
    """
    def __init__(self):
        self.sp500_code = "^GSPC"
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.request_api = RequestApi(self.api_base_url)

    def _safe_beta(
        self,
        tmp: pd.DataFrame, 
        bench: pd.DataFrame, 
        method='log'
    ) -> float | None:
        """
        Betaを安全に計算する関数。株価データとベンチマークデータを受け取り、Betaを計算して返す
        Args:
            tmp (pd.DataFrame): 株価データのDataFrame。少なくとも 'date' と 'close' 列を含む必要がある。
            bench (pd.DataFrame): ベンチマークデータのDataFrame。少なくとも 'date' と 'close' 列を含む必要がある。
            method (str): リターンの計算方法。'log' なら対数リターン、その他なら単純リターンを使用。
        Returns:
            float | None: 計算されたBeta値。計算できない場合はNoneを返す。
        """
        if tmp.empty or bench.empty:
            return None
        tmp = tmp.copy()
        bench = bench.copy()
        tmp['date'] = pd.to_datetime(tmp['date'], errors='coerce')
        bench['date'] = pd.to_datetime(bench['date'], errors='coerce')
        tmp = tmp.sort_values('date').set_index('date')
        bench = bench.sort_values('date').set_index('date')
        a = pd.to_numeric(tmp['close'], errors='coerce')
        b = pd.to_numeric(bench['close'], errors='coerce')
        if method == 'log':
            ra = np.log(a).diff()
            rb = np.log(b).diff()
        else:
            ra = a.pct_change()
            rb = b.pct_change()
        df = pd.concat([ra.rename('ra'), rb.rename('rb')], axis=1).dropna()
        if df.empty:
            return None
        var_rb = df['rb'].var()
        if var_rb == 0 or pd.isna(var_rb):
            return None
        return float(df['ra'].cov(df['rb']) / var_rb)


    def stock_prices_and_market_data(
        self,
        code: str,
        market: str | None,
        bs_df: pd.DataFrame,

    ) -> pd.DataFrame:
        """
        株価・市場データを導出するメソッド
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
            bs_df (pd.DataFrame): バランスシートのDataFrame。少なくとも 'date' と 'share_issued' 列を含む必要がある。
        Returns:
            pd.DataFrame: 株価・市場データを含むDataFrame
        """
        market_list = []
        # dateとshare_issuedを抽出して新しいDataFrameを作成
        bs_df['date'] = pd.to_datetime(bs_df['date'], errors='coerce')
        bs_df = bs_df.sort_values('date')
        bs_df = bs_df[['date', 'share_issued']]
        bs_df.head()
        # 行毎に株価・市場データを導出
        for index, row in bs_df.iterrows():
            end = row['date']
            # APIから52週分の株価データを取得end = dt.datetime.now()
            start = end - dt.timedelta(days=365)
            stock_df = self.request_api.get_stock_time_series_data(
                code=code,
                market=market,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d")
            )
            # APIからS＆P500の52週分のデータを取得
            sp_timeseries_df = self.request_api.get_stock_time_series_data(
                code=self.sp500_code,
                market=None,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d")
            )
            # 株価：
            price = stock_df['close'].iloc[index]
            # 時価総額（Market Cap）：
            market_cap = bs_df['share_issued'].iloc[index] * price
            # 発行済株式数：
            shares_outstanding = bs_df['share_issued'].iloc[index]
            # 52週高値：
            higher_rate_par_52_weeks = stock_df['high'].max()
            # 52週安値：
            lower_rate_par_52_weeks = stock_df['low'].min()
            # Beta（ボラティリティ指標）：
            beta = self._safe_beta(stock_df, sp_timeseries_df, method='log')

            market_row = {
                'close': price,
                'market_cap': market_cap,
                'shares_outstanding': shares_outstanding,
                'higher_rate_par_52_weeks': float(higher_rate_par_52_weeks),
                'lower_rate_par_52_weeks': float(lower_rate_par_52_weeks),
                'beta': beta,
            }
            market_list.append(market_row)
        market_df = pd.DataFrame(market_list)
        return market_df