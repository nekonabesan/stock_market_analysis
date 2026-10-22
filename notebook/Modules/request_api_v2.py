import requests
import json
import pandas as pd

from typing import Any
from typing import override
from Modules.reques_api import RequestApi

class RequestApi(RequestApi):
    """
    RequestAPI不具合対応移行版
    """
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        super().__init__(api_base_url)

    def _safe_json(
        self, 
        response: requests.Response
    ) -> dict[str, Any] | list[Any] | None:
        """
        Safely parse JSON response and return None when body is not JSON.
        Args:
            response (requests.Response): The HTTP response object to parse.
        Returns:
            dict[str, Any] | list[Any] | None: Parsed JSON data or None if parsing fails.
        """
        try:
            return response.json()
        except ValueError:
            return None

    def _extract_results(
        self, 
        data: dict[str, Any] | list[Any] | None
    ) -> list[Any]:
        """
        Normalize API payload into list-like results for compatibility.

        Args:
            data (dict[str, Any] | list[Any] | None): The API response data to normalize.

        Returns:
            list[Any]: A list of results extracted from the API response.
        """
        if isinstance(data, dict):
            results = data.get("results", [])
            return results if isinstance(results, list) else []
        if isinstance(data, list):
            return data
        return []

    @override
    def _post_request(
        self, 
        url: str, 
        payload: dict
    ) -> dict[str, Any]:
        """
        APIにPOSTリクエストを送る共通関数

        """
        try:
            response = requests.post(url, json=payload, timeout=60)
            data = self._safe_json(response)
            if 200 <= response.status_code < 300:
                return {
                    "status_code": response.status_code,
                    "message": response.reason,
                    "results": self._extract_results(data)
                }
            else:
                error_body = data if data is not None else response.text
                print("POST response:", error_body)
                return {
                    "status_code": response.status_code,
                    "message": response.reason,
                    "results": []
                }
        except requests.exceptions.RequestException as e:
            print(f"API request failed: url={url}, error={e}")
            return {
                "status_code": None,
                "message": str(e),
                "results": []
            }

    @override
    def _get_request(
        self, 
        url: str, 
        params: dict
    ) -> dict[str, Any]:
        """
        APIにGETリクエストを送る共通関数

        """
        try:
            response = requests.get(url, params=params, timeout=60)
            data = self._safe_json(response)
            if 200 <= response.status_code < 300:
                return {
                    "status_code": response.status_code,
                    "message": response.reason,
                    "results": self._extract_results(data)
                }
            else:
                error_body = data if data is not None else response.text
                print("GET response:", error_body)
                return {
                    "status_code": response.status_code,
                    "message": response.reason,
                    "results": []
                }
        except requests.exceptions.RequestException as e:
            print(f"API request failed: url={url}, error={e}")
            return {
                "status_code": None,
                "message": str(e),
                "results": []
            }

    @override
    def update_stock_timeseries_data(
        self,
        code: str,
        market: str,
        start: str,
        end: str,
    ) -> json:
        """
        super classのラッパ
        Args:
            code (str): The stock code to update.
            market (str): The market of the stock.
            start (str): The start date of the timeseries data.
            end (str): The end date of the timeseries data.

        Returns:
            json: The JSON response from the API request.
        """
        return super().update_stock_timeseries_data(
            code=code,
            market=market,
            start=start,
            end=end
        )

    @override
    def update_commodity_timeseries_data(
         self, 
         code: str, 
         market: str, 
         start: str, 
         end: str
    ) -> json:
        """
        super classのラッパ
        Args:
            code (str): The commodity code to update.
            market (str): The market of the commodity.
            start (str): The start date of the timeseries data.
            end (str): The end date of the timeseries data.

        Returns:
            json: The JSON response from the API request.
        """
        return super().update_commodity_timeseries_data(
            code=code,
            market=market,
            start=start,
            end=end
        )
    
    @override
    def update_corp_finance_data(
        self, 
        code: str, 
        market: str
    ) -> json:
        """
        super classのラッパ
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        return super().update_corp_finance_data(
            code=code,
            market=market
        )
        
    
    @override
    def get_stock_time_series_data(
         self, 
         code: str, 
         market: str, 
         start: str, 
         end: str
    ) -> pd.DataFrame:
        """
        APIから株価データを取得する関数。
        返却されるDataFrameは、日付をインデックスとし、終値（close）を含む。
        Args:
            code (str): The stock code to retrieve.
            market (str): The market of the stock.
            start (str): The start date of the timeseries data.
            end (str): The end date of the timeseries data.

        Returns:
            pd.DataFrame: The DataFrame containing the stock timeseries data.
        """
        return super().get_stock_time_series_data(
            code=code,
            market=market,
            start=start,
            end=end
        )
        
    @override
    def get_commodity_time_series_data(
         self, 
         code: str, 
         market: str, 
         start: str, 
         end: str
    ) -> pd.DataFrame:
        """
        APIから商品データを取得する関数。
        返却されるDataFrameは、日付をインデックスとし、終値（close）を含む。
        Args:
            code (str): The commodity code to retrieve.
            market (str): The market of the commodity.
            start (str): The start date of the timeseries data.
            end (str): The end date of the timeseries data.

        Returns:
            pd.DataFrame: The DataFrame containing the commodity timeseries data.
        """
        return super().get_commodity_time_series_data(
            code=code,
            market=market,
            start=start,
            end=end
        )
        
    @override
    def get_corp_financials_data(self, code: str, market: str) -> json:
        """
        super classのラッパ
        APIから直近4年分の財務諸表データを取得する関数。
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        return super().get_corp_financials_data(
            code=code,
            market=market
        )
    
    @override
    def get_corp_balance_sheet_data(self, code: str, market: str) -> json:
        """
        APIから直近4年分のバランスシートデータを取得する関数。
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        return super().get_corp_balance_sheet_data(
            code=code,
            market=market
        )
        
    @override
    def get_corp_cash_flow_data(self, code: str, market: str) -> json:
        """
        APIから直近4年分のキャッシュフローデータを取得する関数。
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        return super().get_corp_cash_flow_data(
            code=code,
            market=market
        )
        
    @override
    def get_corp_earnings_data(
        self, 
        code: str, 
        market: str
    ) -> json:
        """
        super classのラッパ
        APIから直近4年分の収益データを取得する関数。
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        return super().get_corp_earnings_data(
            code=code,
            market=market
        )
        
    @override
    def get_corp_quarterly_earnings_data(
        self, 
        code: str, 
        market: str
    ) -> json:
        """
        super classのラッパ
        APIから直近4年分の四半期収益データを取得する関数。
        Args:
            code (str): 銘柄コード
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        return super().get_corp_quarterly_earnings_data(
            code=code,
            market=market
        )
        
    @override
    def search_stock_data(
        self, 
        code: str, 
        name: str, 
        market: str
    ) -> json:
        """
        super classのラッパ
        APIにPOSTリクエストを送って銘柄コードを検索する関数。
        Args:
            code (str): 銘柄コード
            name (str): 銘柄名
            market (str): 市場コード
        Returns:
            json: APIからのレスポンス
        """
        return super().search_stock_data(
            code=code,
            name=name,
            market=market
        )

    def fetch_stock_timeseries_data(
        self,
        start_date: str,
        end_date: str,
        code: str,
        market: str | None,
    ) -> pd.DataFrame:
        """
        Request Yahoo Api and fetch stock market data from the API
        
        Parameters:
        start_date (str): The start date for the time series data.
        end_date (str): The end date for the time series data.
        code (str): The stock code.
        market (str | None): The market identifier.

        Returns:
        pd.DataFrame: A DataFrame containing the stock time series data.
        """
        response = self.update_stock_timeseries_data(
            code=code,
            market=market,
            start=start_date,
            end=end_date
        )
        # Retrieve the time series data from the API
        if response is None:
            return pd.DataFrame()
        # If the response is valid, proceed to fetch the time series data
        df = self.get_stock_time_series_data(
            code=code,
            market=market,
            start=start_date,
            end=end_date
        )
        df["date"] = pd.to_datetime(df["date"])
        return df

    def fetch_commodity_timeseries_data(
        self,
        start_date: str,
        end_date: str,
        code: str,
        market: str | None,
    ) -> pd.DataFrame:
        """
        Request Yahoo Api and fetch commodity market data from the API
        
        Parameters:
        start_date (str): The start date for the time series data.
        end_date (str): The end date for the time series data.
        code (str): The commodity code.
        market (str | None): The market identifier.

        Returns:
        pd.DataFrame: A DataFrame containing the commodity time series data.
        """
        response = self.update_commodity_timeseries_data(
            code=code,
            market=market,
            start=start_date,
            end=end_date
        )
        # Retrieve the time series data from the API
        if response is None:
            return pd.DataFrame()
        # If the response is valid, proceed to fetch the time series data
        df = self.get_commodity_time_series_data(
            code=code,
            market=market,
            start=start_date,
            end=end_date
        )
        df["date"] = pd.to_datetime(df["date"])
        return df


    def fetch_stock_timeseries_data_fred_format(
        self,
        start_date: str,
        end_date: str,
        code: str,
        series_name: str,
        market: str | None = None,
    ) -> pd.DataFrame:
        """
        Yahoo由来の時系列データをFRED側のIFに変換して返す。

        Parameters:
        start_date (str): The start date for the time series data.
        end_date (str): The end date for the time series data.
        code (str): The stock code.
        series_name (str): The series name for FRED format.
        market (str | None): The market identifier.

        Returns:
            pd.DataFrame: index=date, columns=[realtime_start, realtime_end,
            value, interest_rate_type]
        """
        df = self.fetch_stock_timeseries_data(
            start_date=start_date,
            end_date=end_date,
            code=code,
            market=market,
        )
        if df.empty:
            return pd.DataFrame(
                columns=["realtime_start", "realtime_end", "value", "interest_rate_type"],
                index=pd.DatetimeIndex([], name="date"),
            )

        today = pd.Timestamp.today().normalize()
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()

        return pd.DataFrame(
            {
                "realtime_start": today,
                "realtime_end": today,
                "value": pd.to_numeric(df["close"], errors="coerce"),
                "interest_rate_type": series_name,
            },
            index=df.index,
        )
