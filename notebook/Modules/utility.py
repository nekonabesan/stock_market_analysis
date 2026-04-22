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