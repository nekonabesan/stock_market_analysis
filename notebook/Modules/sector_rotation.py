
import pandas as pd

from Modules.reques_api import RequestApi

class SectorRotation:
    API_BASE_URL = "http://localhost:8000"

    def __init__(
        self, 
        api_base_url: str | None = None
    ):
        self.API_BASE_URL = api_base_url or self.API_BASE_URL
        self.request_api = RequestApi(self.API_BASE_URL)
        pass

    def get_stock_timeseries_data(
            self,
            start_date: str,
            end_date: str,
            code: str,
            market: str | None,
    ) -> pd.DataFrame:
        """
        Fetch stock time series data from the API.
    
        Parameters:
        start_date (str): The start date for the time series data.
        end_date (str): The end date for the time series data.
        code (str): The stock code.
        market (str | None): The market identifier.
    
        Returns:
        pd.DataFrame: A DataFrame containing the stock time series data.
        """
        # Fetch market data from the API based on the provided parameters
        response = self.request_api.update_stock_timeseries_data(
            code=code,
            market=market,
            start=start_date,
            end=end_date
        )
        # Retrieve the time series data from the API
        if response is None:
            return pd.DataFrame()
        # If the response is valid, proceed to fetch the time series data
        df = self.request_api.get_stock_time_series_data(
            code=code,
            market=market,
            start=start_date,
            end=end_date
        )
        df["date"] = pd.to_datetime(df["date"])
        return df
    
    def get_commodity_timeseries_data(
        self,
        start_date: str,
        end_date: str,
        code: str,
        market: str | None,
    ) -> pd.DataFrame:
        """
        Fetch commodity time series data from the API.
    
        Parameters:
        start_date (str): The start date for the time series data.
        end_date (str): The end date for the time series data.
        code (str): The commodity code.
        market (str | None): The market identifier.
    
        Returns:
        pd.DataFrame: A DataFrame containing the commodity time series data.
        """
        response = self.request_api.update_commodity_timeseries_data(
            code=code,
            market=market,
            start=start_date,
            end=end_date
        )
        # Retrieve the time series data from the API
        if response is None:
            return pd.DataFrame()
        # If the response is valid, proceed to fetch the time series data
        df = self.request_api.get_commodity_time_series_data(
            code=code,
            market=market,
            start=start_date,
            end=end_date
        )
        df["date"] = pd.to_datetime(df["date"])
        return df




