import os
import datetime as dt
import json
import time
import numpy as np
import pandas as pd 
from pathlib import Path

from Modules.sector_rotation import SectorRotation

class CommoditySectorRotation(SectorRotation):
    """
    Commodity Sector Rotation v2
    """

    OUTPUT_DIR = Path("/workspace/data/")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    # Define sector ETFs, benchmarks, and commodities for analysis
    SECTOR_ETFS = {
        "oil": "XOP",
        "uranium": "URNM",
        "gold": "GDX",
        "silver": "SIL",
        "copper": "COPX",
        "critical_minerals": "REMX",
    }
    # Define benchmarks for analysis
    BENCHMARKS = {
        "SP500": "SPY",
        "NASDAQ100": "QQQ",
        "RUSSELL2000": "IWM"
    }
    # Define commodities for analysis
    COMMODITIES = {
        "WTI": "CL=F",
        "BRENT": "BZ=F",
        "NATGAS": "NG=F",
        "GOLD": "GC=F",
        "SILVER": "SI=F",
        "COPPER": "HG=F",
        "URANIUM": "SRUUF"
    }

    def __init__(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        api_base_url: str | None = None,
        output_dir: Path | None = None,
    ):
        super().__init__()
        self.start = start_date or (dt.datetime.now() - dt.timedelta(days=365)).strftime("%Y-%m-%d")
        self.end = end_date or dt.datetime.now().strftime("%Y-%m-%d")
        #self.API_BASE_URL = api_base_url or self.API_BASE_URL
        self.OUTPUT_DIR = output_dir or self.OUTPUT_DIR
        # Ensure the output directory exists
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        #self.request_api = RequestApi(self.API_BASE_URL)

    def sector_rotation(self) -> dict[str, pd.DataFrame]:
        """
        
        """
        sector_dfs, benchmark_dfs, commodity_dfs = self._get_dataframe()
        #### No.1 データ統合
        all_data, sector_close, benchmark_close, commodity_close = self._to_all_data(
            sector_dfs
            ,benchmark_dfs
            ,commodity_dfs
        )
        #### No.2 リターン作成
        returns, returns_20d, returns_60d = self._create_return(sector_close)
        #### No.3 ベンチマーク比較
        relative_perf = self._benchmark_comparison(
            sector_close, 
            benchmark_close
        )
        #### No.4 Relative Strength作成
        relative_strength = self._create_relative_strength(
            sector_close
            ,benchmark_close
        )
        #### No.5 20日ランキング
        latest_20d_rank = self._create_latest_20d_rank(returns_20d)
        #### No.6 60日ランキング
        latest_60d_rank = self._create_latest_60d_rank(returns_60d)
        #### No.7 セクターローテーションスコア
        rotation_score = self._create_rotation_score(
            sector_close 
            ,returns_20d
            ,returns_60d
        )
        #### No.9 現在の買い候補セクター抽出
        
        #### No.10 sectorスクリーニング

        return {
            "all_data": all_data
            ,"sector_close": sector_close
            ,"returns": returns
            ,"returns_20d": returns_20d
            ,"returns_60d": returns_60d
            ,"relative_perf": relative_perf
            ,"relative_strength": relative_strength
            ,"latest_20d_rank": latest_20d_rank
            ,"latest_60d_rank": latest_60d_rank
            ,"rotation_score": rotation_score
        }

    def _get_dataframe(self) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[str, pd.DataFrame], pd.DataFrame]:
        """
        Fetch sector, benchmark, and commodity time series data as DataFrames.

        Returns:
        tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[str, pd.DataFrame], pd.DataFrame]: 
            A tuple containing dictionaries of DataFrames for sectors, benchmarks, and commodities, and a DataFrame for sector close prices .
        """
        sector_dfs: dict[str, pd.DataFrame] = {
            name: super().get_stock_timeseries_data(
                start_date=self.start,
                end_date=self.end,
                code=code,
                market=None,
            )
            for name, code in self.SECTOR_ETFS.items()
        }

        benchmark_dfs: dict[str, pd.DataFrame] = {
            name: super().get_stock_timeseries_data(
                start_date=self.start,
                end_date=self.end,
                code=code,
                market=None,
            )
            for name, code in self.BENCHMARKS.items()
        }
    
        commodity_dfs: dict[str, pd.DataFrame] = {
            name: super().get_commodity_timeseries_data(
                start_date=self.start,
                end_date=self.end,
                code=code,
                market=None,
            )
            for name, code in self.COMMODITIES.items()
        }

        return sector_dfs, benchmark_dfs, commodity_dfs

    def _to_all_data(
        self, 
        sector_dfs: dict[str, pd.DataFrame], 
        benchmark_dfs: dict[str, pd.DataFrame], 
        commodity_dfs: dict[str, pd.DataFrame]
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        No.1 データ統合

        Args:
            sector_dfs (dict[str, pd.DataFrame]): Dictionary of sector DataFrames.
            benchmark_dfs (dict[str, pd.DataFrame]): Dictionary of benchmark DataFrames.
            commodity_dfs (dict[str, pd.DataFrame]): Dictionary of commodity DataFrames.

        Returns:
            pd.DataFrame: Combined DataFrame with all close prices, forward-filled and sorted by date.
            pd.DataFrame: DataFrame containing only sector close prices, forward-filled and sorted by date.
            pd.DataFrame: DataFrame containing only benchmark close prices, forward-filled and sorted by date.
            pd.DataFrame: DataFrame containing only commodity close prices, forward-filled and sorted by date.
        """
        sector_close = pd.DataFrame({
            name: df.set_index("date")["close"]
            for name, df in sector_dfs.items()
        })

        benchmark_close = pd.DataFrame({
            name: df.set_index("date")["close"]
            for name, df in benchmark_dfs.items()
        })

        commodity_close = pd.DataFrame({
            name: df.set_index("date")["close"]
            for name, df in commodity_dfs.items()
        })

        sector_close = sector_close.sort_index()
        benchmark_close = benchmark_close.sort_index()
        commodity_close = commodity_close.sort_index()

        # 日付ソート
        sector_close = sector_close.sort_index()
        benchmark_close = benchmark_close.sort_index()
        commodity_close = commodity_close.sort_index()

        # 前方補完
        sector_close = sector_close.ffill()
        benchmark_close = benchmark_close.ffill()
        commodity_close = commodity_close.ffill()

        # 全列で欠損のある行を除去
        sector_close = sector_close.dropna()
        benchmark_close = benchmark_close.dropna()
        commodity_close = commodity_close.dropna()

        all_data = pd.concat(
            [
                sector_close.add_prefix("sector_"),
                benchmark_close.add_prefix("benchmark_"),
                commodity_close.add_prefix("commodity_")
            ],
            axis=1
        )

        all_data = all_data.ffill()

        return all_data, sector_close, benchmark_close, commodity_close


    def _create_return(
        self, 
        sector_close: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        No.2 リターン作成
        Args:
            sector_close (pd.DataFrame): DataFrame containing sector close prices with dates as the index.
        Returns:
            tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Daily, 20-day, and 60-day returns.
        """
        returns = sector_close.pct_change()

        returns_20d = sector_close.pct_change(20)
        returns_60d = sector_close.pct_change(60)

        returns.columns = [f"{c}_ret" for c in returns.columns]
        returns_20d.columns = [f"{c}_20d" for c in returns_20d.columns]
        returns_60d.columns = [f"{c}_60d" for c in returns_60d.columns]

        return returns, returns_20d, returns_60d


    def _benchmark_comparison (
        self,
        sector_close: pd.DataFrame,
        benchmark_close: pd.DataFrame
    ) -> pd.DataFrame:
        """
        No.3 ベンチマーク比較
        Args:
            sector_close (pd.DataFrame): DataFrame containing sector close prices with dates as the index.
            benchmark_close (pd.DataFrame): DataFrame containing benchmark close prices with dates as the index.

        Returns:
            pd.DataFrame: Relative performance of each sector against the benchmark.
        """
        benchmark_ret = benchmark_close["SP500"].pct_change(20)

        relative_perf = pd.DataFrame(index=sector_close.index)

        for sector in sector_close.columns:

            sector_ret = sector_close[sector].pct_change(20)

            relative_perf[sector] = (
                sector_ret - benchmark_ret
            )

        return relative_perf

    
    def _create_relative_strength(
        self,
        sector_close: pd.DataFrame,
        benchmark_close: pd.DataFrame
    ) -> pd.DataFrame:
        """
        No.4 Relative Strength作成
        Args:
            sector_close (pd.DataFrame): DataFrame containing sector close prices with dates as the index.
            benchmark_close (pd.DataFrame): DataFrame containing benchmark close prices with dates as the index.

        Returns:
            pd.DataFrame: Relative strength of each sector against the benchmark.
        """
        relative_strength = pd.DataFrame(index=sector_close.index)

        for sector in sector_close.columns:

            rs = (
                sector_close[sector]
                .div(benchmark_close["SP500"], fill_value=np.nan)
            )

            relative_strength[sector] = rs

        relative_strength = relative_strength.dropna()

        relative_strength = (
            relative_strength /
            relative_strength.iloc[0]
        ) * 100

        return relative_strength
    

    def _create_latest_20d_rank(
        self,
        returns_20d: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        No.5 20日ランキング
        Args:
            returns_20d (pd.DataFrame): DataFrame containing 20-day returns with dates as the index.

        Returns:
            pd.DataFrame: Latest 20-day return rank of each sector.
        """
        latest_20d_rank = (
            returns_20d.iloc[-1]
            .sort_values(ascending=False)
            .to_frame("return_20d")
        )

        latest_20d_rank["rank"] = range(
            1,
            len(latest_20d_rank) + 1
        )

        return latest_20d_rank

    def _create_latest_60d_rank(
        self,
        returns_60d: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        No.6 60日ランキング
        Args:
            returns_60d (pd.DataFrame): DataFrame containing 60-day returns with dates as the index.

        Returns:
            pd.DataFrame: Latest 60-day return rank of each sector.
        """

        latest_60d_rank = (
            returns_60d.iloc[-1]
            .sort_values(ascending=False)
            .to_frame("return_60d")
        )

        latest_60d_rank["rank"] = range(
            1,
            len(latest_60d_rank) + 1
        )

        latest_60d_rank = latest_60d_rank.dropna()

        return latest_60d_rank




    def _create_rotation_score(
        self,
        sector_close: pd.DataFrame,
        returns_20d: pd.DataFrame,
        returns_60d: pd.DataFrame
    ) -> pd.DataFrame:
        """
        No.7 セクターローテーションスコア

        Args:
            sector_close (pd.DataFrame): DataFrame containing sector closing prices with dates as the index.
            returns_20d (pd.DataFrame): DataFrame containing 20-day returns with dates as the index.
            returns_60d (pd.DataFrame): DataFrame containing 60-day returns with dates as the index.

        Returns:
            pd.DataFrame: Rotation score of each sector.
        """
        # ============================================================
        # No.7 セクターローテーションスコア
        # ============================================================
        rotation_score = pd.DataFrame(
            index=sector_close.columns
        )
        # ------------------------------------------------------------
        # Momentum
        # ------------------------------------------------------------
        rotation_score["score20"] = (
            returns_20d.iloc[-1]
            .rename(lambda x: x.replace("_20d", ""))
        )
        rotation_score["score60"] = (
            returns_60d.iloc[-1]
            .rename(lambda x: x.replace("_60d", ""))
        )
        # ------------------------------------------------------------
        # Acceleration
        # ------------------------------------------------------------
        rotation_score["acceleration"] = (
            rotation_score["score20"]
            - rotation_score["score60"]
        )
        # ------------------------------------------------------------
        # 欠損除去
        # ------------------------------------------------------------
        rotation_score = rotation_score.dropna()
        # ------------------------------------------------------------
        # Z Score
        # ------------------------------------------------------------
        for col in [
            "score20",
            "score60",
            "acceleration"
        ]:
            std = rotation_score[col].std()

            if std > 0:

                rotation_score[f"z_{col}"] = (
                    rotation_score[col]
                    - rotation_score[col].mean()
                ) / std

            else:

                rotation_score[f"z_{col}"] = 0
        # ------------------------------------------------------------
        # Composite Score
        # ------------------------------------------------------------
        rotation_score["rotation_score"] = (

            0.50 * rotation_score["z_score20"]
            + 0.20 * rotation_score["z_score60"]
            + 0.30 * rotation_score["z_acceleration"]

        )
        # ------------------------------------------------------------
        # Rank
        # ------------------------------------------------------------
        rotation_score = rotation_score.sort_values(
            "rotation_score",
            ascending=False
        )

        return rotation_score


    
