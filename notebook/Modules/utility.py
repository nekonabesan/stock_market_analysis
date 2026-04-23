import os
import math
import requests
import pandas as pd

class Utility:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    def calc_tax(self, total_profit: int) -> int:
        """
        税金を計算する関数
        :param total_profit: 総利益
        :return: 税金額
        """
        if total_profit < 0:
            return 0
        return int(total_profit * 0.20315)

    def calc_fee(self, total: int)-> int:
        """
        手数料を計算する関数
        :param total: 総取引額
        :return: 手数料額
        """
        if total <= 50000:
            return 54
        elif total <= 100000:
            return 97
        elif total <= 200000:
            return 113
        elif total <= 500000:
            return 270
        elif total <= 1000000:
            return 525
        elif total <= 1500000:
            return 628
        elif total <= 3000000:
            return 994
        else:
            return 1050
        
    def calc_cost_of_buying(self, count: int, price: int) -> int:
        """
        買いのコストを計算する関数
        :param count: 株数
        :param price: 株価
        :return: 買いのコスト
        """
        subtotal = int(count * price)
        fee = self.calc_fee(subtotal)
        return subtotal + fee, fee

    def calc_cost_of_selling(self, count: int, price: int) -> int:
        """
        売りのコストを計算する関数
        :param count: 株数
        :param price: 株価
        :return: 売りのコスト
        """
        subtotal = int(count * price)
        fee = self.calc_fee(subtotal)
        return fee, fee
    
    def tse_date_range(self, start_date: str, end_date: str) -> list:
        """
        japandas を使わず、土日を除く平日のみを返す。
        返却型は元の関数と同じ DatetimeIndex。
        """
        # pandas の標準 BusinessDay（＝土日を除く平日）
        business_days = pd.offsets.BusinessDay()
        return pd.date_range(start=start_date, end=end_date, freq=business_days)
    
    def get_stock_time_series_data(self, code: str, market: str, start: str, end: str) -> pd.DataFrame:
        """
        APIから株価データを取得する関数。
        返却されるDataFrameは、日付をインデックスとし、終値（close）を含む。
        """
        df = pd.DataFrame()
        get_url = f"{self.API_BASE_URL}/api/v1/time_series_data/stock/"
        get_params = {
            "code": code,
            "market": market,
            "start": start,
            "end": end
        }

        get_response = requests.get(get_url, params=get_params, timeout=60)

        if get_response.status_code == 200:
            get_json = get_response.json()
            results = get_json.get("results", [])
            df = pd.DataFrame(results)
            print("取得件数:", len(df))
        else:
            print("GET response:", get_response.json())

        return df
    
    def calc_max_drawdown(self, prices):
        """
        最大ドローダウンを計算して返す
        """
        cummax_ret = prices.cummax()
        drawdown = cummax_ret - prices
        max_drawdown_date = drawdown.idxmax()
        return drawdown[max_drawdown_date] / cummax_ret[max_drawdown_date]


    def calc_sharp_ratio(self, returns):
        """
        シャープレシオを計算して返す
        """
        # .meanは平均値(=期待値)を求めるメソッド
        return returns.mean() / returns.std()


    def calc_information_ratio(self, returns, benchmark_retruns):
        """
        インフォメーションレシオを計算して返す
        """
        excess_returns = returns - benchmark_retruns
        return excess_returns.mean() / excess_returns.std()



    def calc_sortino_ratio(self, returns):
        """
        ソルティノレシオを計算して返す
        """
        tdd = math.sqrt(returns.clip_upper(0).pow(2).sum() / returns.size)
        return returns.mean() / tdd

    def calc_sortino_bench(self, returns, benchmark_retruns):
        excess_returns = returns - benchmark_retruns
        return self.calc_sortino_ratio(excess_returns)

    def calc_calmar_ratio(self, prices, returns):
        """
        カルマ―レシオを計算して返す
        """
        return returns.mean() / self.calc_max_drawdown(prices)