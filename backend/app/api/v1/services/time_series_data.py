import datetime as dt
import numpy as np
import pandas as pd
import talib as ta

from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.trn_stock_price import StockPrice
from app.api.v1.services.rci import Rci

class TimeSeriesDataService:
    def __init__(self, db_session: Session):
        """
        TimeSeriesDataServiceを初期化する
        Args:
            db_session (Session): DBセッション
        Returns:
            None: 初期化のみ行う
        """
        self.db_session = db_session
        self.rci = Rci()

    def get_time_series_data(
        self,
        code: str,
        market: str | None,
        start: dt.date | None,
        end: dt.date | None,
        db: Session | None = None,
    ) -> list[dict]:
        try:
            if start is None or end is None:
                raise ValueError("start and end are required")
            if start > end:
                raise ValueError("start must be less than or equal to end")

            session = db or self.db_session
            data_acquisition_start_date = start - dt.timedelta(days=300)
            query = (session.query(StockPrice)
                     .filter(StockPrice.stock_code == code)
                     .filter(StockPrice.date >= data_acquisition_start_date)
                     .filter(StockPrice.date <= end))
            if market is not None:
                query = query.filter(StockPrice.stock_market == market)

            data = query.all()
            if not data:
                return []

            df = pd.DataFrame([self._row_to_dict(record) for record in data])
            if df.empty or "date" not in df.columns or "close" not in df.columns:
                return []

            df.sort_values(by="date", inplace=True)
            close = df["close"]

            # 移動平均線を導出
            df["ma5"] = self._calc_sma(close, window=5)
            df["ma25"] = self._calc_sma(close, window=25)

            # RSIを導出
            df["rsi14"] = self._calc_rsi(close, timeperiod=14)
            df['rsi28'] = self._calc_rsi(close, timeperiod=28)

            # MACDを導出
            df["macd"], df["macd_signal"], df["hist"] = self._calc_macd(close, fastperiod=12, 
                                                                        slowperiod=26, signalperiod=9)

            # SMAを導出
            df["sma_20"] = self._calc_sma(close, window=20)

            # EMAを導出
            df["ema_20"] = self._calc_ema(close, window=20)

            # ストキャスティクスを導出
            df['slowK'], df['slowD'] = self._calc_stochastic(df, fastk_period=5, slowk_period=3, slowd_period=3,
                                                                slowk_matype=0, slowd_matype=0)
            
            # ボリンジャーバンド1σを導出
            df["upper1"], _, df["lower1"] = self._calc_bollinger_bands(close, timeperiod=25, 
                                                                    nbdevup=1, nbdevdn=1, matype=ta.MA_Type.SMA)
            # ボリンジャーバンド2σを導出
            df["upper2"], _, df["lower2"] = self._calc_bollinger_bands(close, timeperiod=25, 
                                                                    nbdevup=2, nbdevdn=2, matype=ta.MA_Type.SMA)

            # RCIを導出
            df["rci9"] = self._calc_rci(close, window=9)
            df["rci26"] = self._calc_rci(close, window=26)

            # 移動平均線のゴールデンクロスとデッドクロスを導出
            df["gc"], df["dc"] = self._calc_gc(df)

            # MACDのゴールデンクロスとデッドクロスを導出
            df["macd_gc"], df["macd_dc"] = self._calc_macd_cross(df)

            # RCIのゴールデンクロスとデッドクロスを導出
            df["rci_gc"], df["rci_dc"] = self._calc_rci_cross(df)

            # 上昇条件を導出
            df["rising_condition"] = self._check_rising_condition(df)

            # 指定された期間でフィルタリング
            df = df[(df["date"] >= start) & (df["date"] <= end)]

            return df.to_dict(orient="records")

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching time series data: {e}")
            raise RuntimeError("time series data fetch failed") from e

    def _calc_rsi(self, close: pd.Series, timeperiod: int) -> pd.Series:
        """
        RSIを計算する関数
        Args:
            close (pd.Series): 株価データの終値のSeries。
            timeperiod (int): RSIの期間
        Returns:
            pd.Series: 計算されたRSIの値を含むSeries
        """
        return ta.RSI(close, timeperiod=timeperiod)

    def _calc_macd(
        self,
        close: pd.Series,
        fastperiod: int,
        slowperiod: int,
        signalperiod: int,
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACDを計算する関数
        Args:
            close (pd.Series): 株価データの終値のSeries。
            fastperiod (int): 短期EMAの期間
            slowperiod (int): 長期EMAの期間
            signalperiod (int): シグナル線の期間
        Returns:
            tuple[pd.Series, pd.Series, pd.Series]: macd, signal, hist
        """
        return ta.MACD(close, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        

    def _calc_sma(self, close: pd.Series, window: int) -> pd.Series:
        """
        SMAを計算する関数
        Args:
            close (pd.Series): 株価データの終値のSeries。
            window (int): SMAの期間
        Returns:
            pd.Series: 計算されたSMAの値を含むSeries
        """        
        return ta.SMA(close, timeperiod=window)

    def _calc_ema(self, close: pd.Series, window: int) -> pd.Series:
        """
        EMAを計算する関数
        Args:
            close (pd.Series): 株価データの終値のSeries。
            window (int): EMAの期間
        Returns:
            pd.Series: 計算されたEMAの値を含むSeries
        """        
        return ta.EMA(close, timeperiod=window)

    def _calc_stochastic(
            self, 
            df: pd.DataFrame, 
            fastk_period: int, 
            slowk_period: int, 
            slowd_period: int,
            slowk_matype: int,
            slowd_matype: int
        ) -> pd.DataFrame:
        """
        ストキャスティクスを計算する関数
        Args:
            df (pd.DataFrame): 株価データのDataFrame。'high'、'low'、'close'列が必要。
            fastk_period (int): FastKの期間
            slowk_period (int): SlowKの期間
            slowd_period (int): SlowDの期間
        Returns:
            pd.DataFrame: 計算されたストキャスティクスの値を含むDataFrame。'slowK'と'slowD'列が必要。
        """        
        return ta.STOCH(df["high"], df["low"], df["close"], 
                        fastk_period=fastk_period, 
                        slowk_period=slowk_period, 
                        slowk_matype=slowk_matype,
                        slowd_period=slowd_period,
                        slowd_matype=slowd_matype)

    def _calc_bollinger_bands(self, close: pd.Series, timeperiod: int,
                              nbdevup: int = 2, nbdevdn: int = 2, matype: int = ta.MA_Type.SMA) -> pd.DataFrame:
        """
        ボリンジャーバンドを計算する関数
        Args:
            close (pd.Series): 株価データの終値のSeries。
            timeperiod (int): ボリンジャーバンドの期間
        Returns:
            pd.DataFrame: 計算されたボリンジャーバンドの値を含むDataFrame。'upper_band'、'lower_band'、'middle_band'列が必要。
        """        
        return ta.BBANDS(close, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=matype)

    def _calc_rci(self, close: pd.Series, window: int) -> pd.Series:
        """
        RCIを計算する関数
        Args:
            close (pd.Series): 株価データの終値のSeries。
            window (int): RCIの期間
        Returns:
            pd.Series: 計算されたRCIの値を含むSeries
        """        
        return self.rci.RCI(close.to_numpy(), timeperiod=window)

    def _row_to_dict(self, row: StockPrice) -> dict:
        """ORM row を dict に変換する。to_dict 実装が無いモデルにも対応する。"""
        if hasattr(row, "to_dict") and callable(row.to_dict):
            return row.to_dict()

        mapper = inspect(StockPrice)
        return {column.key: getattr(row, column.key) for column in mapper.columns}
    
    def _calc_gc(self, df: pd.DataFrame) -> pd.Series:
        """
        5日移動平均線と25日移動平均線のゴールデンクロスを計算する関数
        Args:
            df (pd.DataFrame): 株価データのDataFrame。'close'列が必要。
        Returns:
            pd.Series: ゴールデンクロスのシグナルを含むSeries。
        """
        # ゴールデンクロス
        cross = df["ma5"] > df["ma25"]
        df["cross"] = cross
        cross_shift = df["cross"].shift(1)
        # ゴールデンクロスの発生日
        temp_gc = (cross != cross_shift) & (cross == True)
        # デッドクロスの発生日
        temp_dc = (cross != cross_shift) & (cross == False)
        # ゴールデンクロスの発生日であればMA5の値、それ以外はNaN
        gc = [m if g == True else np.nan for g, m in zip(temp_gc, df["ma5"])]
        # デッドクロスの発生日であればMA25の値、それ以外はNaN
        dc = [m if d == True else np.nan for d, m in zip(temp_dc, df["ma25"])]
        return pd.Series(gc), pd.Series(dc)

    def _calc_macd_cross(self, df: pd.DataFrame) -> pd.Series:
        """
        MACDとシグナル線のゴールデンクロスを計算する関数
        Args:
            df (pd.DataFrame): 株価データのDataFrame。'macd'列と'macd_signal'列が必要。
        Returns:
            pd.Series: ゴールデンクロスのシグナルを含むSeries。
        """
        cross = df["macd"] > df["macd_signal"]
        cross_shift = cross.shift(1)
        temp_gc = (cross != cross_shift) & (cross == True)
        temp_dc = (cross != cross_shift) & (cross == False)
        gc = [m if g == True else np.nan for g, m in zip(temp_gc, df["macd"])]
        dc = [m if d == True else np.nan for d, m in zip(temp_dc, df["macd_signal"])]
        return pd.Series(gc), pd.Series(dc)
    
    def _calc_rci_cross(self, df: pd.DataFrame) -> pd.Series:
        """
        rci9とrci26のゴールデンクロスを計算する関数
        Args:
            df (pd.DataFrame): 株価データのDataFrame。'rci9'列と'rci26'列が必要。
        Returns:
            pd.Series: ゴールデンクロスのシグナルを含むSeries。
        """
        cross = df["rci9"] > df["rci26"]
        cross_shift = cross.shift(1)
        temp_gc = (cross != cross_shift) & (cross == True)
        temp_dc = (cross != cross_shift) & (cross == False)
        gc = [m if g == True else np.nan for g, m in zip(temp_gc, df["rci9"])]
        dc = [m if d == True else np.nan for d, m in zip(temp_dc, df["rci26"])]
        return pd.Series(gc), pd.Series(dc)
    
    def _check_rising_condition(self, df: pd.DataFrame) -> pd.Series:
        """
        ・MACDがシグナルより下でゴールデンクロス前
        ・MACDが日々上昇しつつある
        ・長期RCIが-50未満
        Args:
            df (pd.DataFrame): 株価データのDataFrame。'macd'列、'macd_signal'列、'rci26'列が必要。
        Returns:
            pd.Series: 条件を満たす場合はTrue、そうでない場合はFalseを含む時系列 Series。
        """
        # 条件1: MACDがシグナルより下（ゴールデンクロス前）
        condition1 = df["macd"] < df["macd_signal"]
        
        # 条件2: MACDが日々上昇している（前日より上昇）
        condition2 = df["macd"].diff() > 0
        
        # 条件3: 長期RCIが-50未満
        condition3 = df["rci26"] < -50
        
        return condition1 & condition2 & condition3
        
