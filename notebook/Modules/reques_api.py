import os
import sys
import json
import requests
import datetime as dt
import pandas as pd


class RequestApi:
    def __init__(self, api_base_url: str) -> json:
        self.api_base_url = api_base_url
        pass

    def _post_request(self, url: str, payload: dict) -> json:
        """
        APIにPOSTリクエストを送る共通関数

        """
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json()
            else:
                print("POST response:", response.json())
                return json.loads("{}")
        except requests.exceptions.RequestException as e:
            print(f"API request failed: url={url}, error={e}")
            return json.loads("{}")
        
    def _get_request(self, url: str, params: dict) -> json:
        """
        APIにGETリクエストを送る共通関数

        """
        try:
            response = requests.get(url, params=params, timeout=60)
            if response.status_code == 200:
                return response.json()
            else:
                print("GET response:", response.json())
                return json.loads("{}")
        except requests.exceptions.RequestException as e:
            print(f"API request failed: url={url}, error={e}")
            return json.loads("{}")

    def update_stock_timeseries_data(self, code: str, market: str, start: str, end: str) -> json:
        """
        APIにPOSTリクエストを送って株価データを更新する関数。
        返却されるDataFrameは、日付をインデックスとし、終値（close）を含む。
        """
        post_payload = {
            "code": code,
            "market": market,
            "start": start,
            "end": end
        }
        # /api/v1/stock_price/
        post_url = f"{self.api_base_url}/api/v1/stock_price/"
        return self._post_request(post_url, post_payload)

    def update_commodity_timeseries_data(self, code: str, market: str, start: str, end: str) -> json:
        """
        APIにPOSTリクエストを送って商品データを更新する関数。
        返却されるDataFrameは、日付をインデックスとし、終値（close）を含む。
        """
        # validate ISO date strings (YYYY-MM-DD)

        try:
            if start is not None:
                dt.date.fromisoformat(start)
            if end is not None:
                dt.date.fromisoformat(end)
        except Exception as e:
            print(f"Invalid date format for start/end: start={start}, end={end}, error={e}")
            return json.loads("{}")

        post_payload = {
            "code": code,
            "market": market,
            "start": start,
            "end": end
        }
        # correct endpoint: /api/v1/commodity_data/
        post_url = f"{self.api_base_url}/api/v1/commodity_data/"
        return self._post_request(post_url, post_payload)
    
    def update_corp_finance_data(self, code: str, market: str) -> json:
        """
        APIにPOSTリクエストを送って直近４年分の財務データを更新する関数。
        - 直近４年分の財務諸表
        - 直近４年分のバランスシート
        - 直近４年分のキャッシュフロー
        - 直近４年分の収益
        - 直近４年分の四半期収益
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        post_payload = {
            "code": code,
            "market": market,
        }
        # /api/v1/corp_finance_data/
        post_url = f"{self.api_base_url}/api/v1/corp_finance_data/"
        return self._post_request(post_url, post_payload)
    

    def get_stock_time_series_data(self, code: str, market: str, start: str, end: str) -> pd.DataFrame:
        """
        APIから株価データを取得する関数。
        返却されるDataFrameは、日付をインデックスとし、終値（close）を含む。
        """
        df = pd.DataFrame()
        get_url = f"{self.api_base_url}/api/v1/time_series_data/stock/"
        get_params = {
            "code": code,
            "market": market,
            "start": start,
            "end": end
        }
        # /api/v1/time_series_data/stock/
        get_response = self._get_request(get_url, get_params)

        if get_response is not None:
            results = get_response.get("results", [])
            df = pd.DataFrame(results)
            print("取得件数:", len(df))
        else:
            print("GET response:", get_response)

        return df
    
    def get_commodity_time_series_data(self, code: str, market: str, start: str, end: str) -> pd.DataFrame:
        """
        APIから商品データを取得する関数。
        返却されるDataFrameは、日付をインデックスとし、終値（close）を含む。
        """
        df = pd.DataFrame()
        get_url = f"{self.api_base_url}/api/v1/time_series_data/commodity/"
        get_params = {
            "code": code,
            "market": market,
            "start": start,
            "end": end
        }
        # /api/v1/time_series_data/commodity/
        get_response = self._get_request(get_url, get_params)

        if get_response is not None:
            results = get_response.get("results", [])
            df = pd.DataFrame(results)
            print("取得件数:", len(df))
        else:
            print("GET response:", get_response)

        return df
    
    def get_corp_financials_data(self, code: str, market: str) -> json:
        """
        APIから直近４年分の財務諸表データを取得する関数。
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        # /api/v1/corp_finance_data/financials/
        get_url = f"{self.api_base_url}/api/v1/corp_finance_data/financials/"
        get_params = {
            "code": code,
            "market": market,
        }
        # /api/v1/corp_finance_data/financials/
        return self._get_request(get_url, get_params)
    
    def get_corp_balance_sheet_data(self, code: str, market: str) -> json:
        """
        APIから直近４年分のバランスシートデータを取得する関数。
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        # /api/v1/corp_finance_data/balance_sheet/
        get_url = f"{self.api_base_url}/api/v1/corp_finance_data/balance_sheet/"
        get_params = {
            "code": code,
            "market": market,
        }
        # /api/v1/corp_finance_data/balance_sheet/
        return self._get_request(get_url, get_params)
    
    def get_corp_cash_flow_data(self, code: str, market: str) -> json:
        """
        APIから直近４年分のキャッシュフローデータを取得する関数。
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        # /api/v1/corp_finance_data/cash_flow/
        get_url = f"{self.api_base_url}/api/v1/corp_finance_data/cash_flow/"
        get_params = {
            "code": code,
            "market": market,
        }
        # /api/v1/corp_finance_data/cash_flow/
        return self._get_request(get_url, get_params)
    
    def get_corp_earnings_data(self, code: str, market: str) -> json:
        """
        APIから直近４年分の収益データを取得する関数。
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        # /api/v1/corp_finance_data/earnings/
        get_url = f"{self.api_base_url}/api/v1/corp_finance_data/earnings/"
        get_params = {
            "code": code,
            "market": market,
        }
        # /api/v1/corp_finance_data/earnings/
        return self._get_request(get_url, get_params)
    
    def get_corp_quarterly_earnings_data(self, code: str, market: str) -> json:
        """
        APIから直近４年分の四半期収益データを取得する関数。
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        # /api/v1/corp_finance_data/quarterly_earnings/
        get_url = f"{self.api_base_url}/api/v1/corp_finance_data/quarterly_earnings/"
        get_params = {
            "code": code,
            "market": market,
        }
        # /api/v1/corp_finance_data/quarterly_earnings/
        return self._get_request(get_url, get_params)
    
    def search_stock_data(self, code: str, name: str, market: str) -> json:
        """
        APIにPOSTリクエストを送って銘柄コードを検索する関数。
        Args:
            code (str): 銘柄コード
            name (str): 銘柄名
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        post_payload = {
            "code": code,
            "name": name,
            "market": market
        }
        # /api/v1/search/
        post_url = f"{self.api_base_url}/api/v1/search/"
        return self._post_request(post_url, post_payload)