import os
import pandas as pd

from Modules.request_api_v2 import RequestApi

class Later1Alert:
    """
    Later1アラート判定クラス

    Yahoo Financeから市場データを取得し、
    SVXY出来高に関する特徴量を計算して
    アラート判定を行う。

    処理内容

    - 市場データ取得
    - 特徴量計算
    - アラート判定
    - 判定結果返却

    execute() は判定結果を dict 形式で返却する。
    """
    ALERT_LEVEL_LOW = "LOW"
    ALERT_LEVEL_CRITICAL = "CRITICAL"
    SIGNAL_NAME = "SVXY_LEVEL_MOMENTUM"
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    def __init__(
        self,
        api_base_url: str = API_BASE_URL
    ):
        self.request_api = RequestApi(api_base_url=api_base_url)

    def execute(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> dict:
        """
        Later1アラートを実行する

        Args:
            start_date (str, optional): 開始日
            end_date (str, optional): 終了日

        Returns:
            dict: アラート結果
        """
        try:
            # データを取得
            data = self.fetch(start_date=start_date, end_date=end_date)
            # 特徴量を計算
            signal = self.calculate(data)
            # シグナルを評価
            return self.evaluate(signal)
        except Exception as e:
            return {"message": str(e)}

    def _fetch(
        self,
        start_date: str = None,
        end_date: str = None,
        code: str = None,
        market: str = None,
    ) -> pd.DataFrame:
        """
        Yahoo Financeから指定された銘柄のデータを取得する

        Args:
            code (str): 銘柄コード
            market (str, optional): 市場コード
            start_date (str, optional): 開始日
            end_date (str, optional): 終了日

        Returns:
            pd.DataFrame: 取得したデータ
        """
        return self.request_api.fetch_stock_timeseries_data(
            start_date=start_date,
            end_date=end_date,
            code=code,
            market=market,
        )

    def fetch(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> pd.DataFrame:
        """
        Yahoo Financeから
        
        - QQQ
        - SVXY
        - VXX
        を取得する

        Args:
            start_date (str, optional): 開始日
            end_date (str, optional): 終了日

        Returns:
            pd.DataFrame: 取得したデータ
        """
        # QQQのデータを取得
        df_qqq = self._fetch(
            start_date=start_date,
            end_date=end_date,
            code="QQQ",
            market=None
        )
        # SVXYのデータを取得
        df_svxy = self._fetch(
            start_date=start_date,
            end_date=end_date,
            code="SVXY",
            market=None,
        )
        # VXXのデータを取得
        df_vxx = self._fetch(
            start_date=start_date,
            end_date=end_date,
            code="VXX",
            market=None,
        )
        # データ整形
        qqq_work = (
            df_qqq[["date", "close"]]
            .rename(columns={"close": "qqq"})
        )
        # SVXYのデータ整形
        svxy_work = (
            df_svxy[["date", "close", "volume"]]
            .rename(
                columns={
                    "close": "svxy",
                    "volume": "svxy_volume"
                }
            )
        )
        # VXXのデータ整形   
        vxx_work = (
            df_vxx[["date", "close", "volume"]]
            .rename(
                columns={
                    "close": "vxx",
                    "volume": "vxx_volume"
                }
            )
        )
        # データ結合
        research_df = (
            qqq_work
            .merge(svxy_work, on="date", how="left")
            .merge(vxx_work, on="date", how="left")
        )
        # 日付をdatetime型に変換
        research_df["date"] = pd.to_datetime(research_df["date"])
        return research_df

    def calculate(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Later1で利用する特徴量を計算
        Args:
            data (pd.DataFrame): 取得したデータ

        Returns:
            pd.DataFrame: 計算結果を含むデータ
        """
        df = data.copy()
        # SVXY Volume Z-score
        volume_mean = (df["svxy_volume"].rolling(60).mean())
        # SVXY Volumeの標準偏差を計算
        volume_std = (df["svxy_volume"].rolling(60).std().replace(0, pd.NA))
        # SVXY Volume Z-scoreを計算
        df["svxy_volume_z"] = ((df["svxy_volume"] - volume_mean) / volume_std)
        # SVXY Volume ROC 10D
        df["svxy_volume_roc_10d"] = (df["svxy_volume"] - df["svxy_volume"].shift(10))
        # Decile
        df["svxy_volume_roc_10d_decile"] = pd.qcut(
            df["svxy_volume_roc_10d"],
            q=10,
            labels=False,
            duplicates="drop"
        )
        return df

    def evaluate(
        self,
        signal: pd.DataFrame
    ) -> dict:
        """
        Later1のシグナルを評価

        Args:
            signal (pd.DataFrame): 計算済みの特徴量を含むデータ

        Returns:
            dict: アラート情報
        """
        # 最新の有効行を取得
        latest_df = (
            signal
            .dropna(subset=["svxy_volume_z", "svxy_volume_roc_10d_decile"])
        )
        # データが不足している場合はアラートを出さない
        if latest_df.empty:
            # データが不足しているためアラートを出さない
            return {
                "alert": False,
                "level": self.ALERT_LEVEL_LOW,
                "signal": self.SIGNAL_NAME,
                "reason": "insufficient_data"
            }
        # 最新のデータを取得
        latest = latest_df.iloc[-1]
        # 最新のSVXY Volume Z-scoreとROC Decileを取得
        svxy_z = float(latest["svxy_volume_z"])
        # SVXY ROC Decileを取得
        svxy_decile = int(latest["svxy_volume_roc_10d_decile"])
        #
        # Later1 Rule
        #
        # V5検証結果
        #
        # SVXY_Z >= 3
        # AND
        # SVXY_ROC_10D Top Decile
        alert = (svxy_z >= 3 and svxy_decile == 9)
        # アラートレベルを設定
        level = self.ALERT_LEVEL_LOW
        # デフォルトのアラートレベルを設定
        if alert:
            level = self.ALERT_LEVEL_CRITICAL
        # アラート情報を返す
        return {
            # =============================================== #
            # アラート判定結果
            #
            # V5検証において統計的有意性が確認された
            # Later1シグナルの発火有無
            # =============================================== #
            "alert": alert,
            # =============================================== #
            # リスクレベル
            #
            # LOW:
            #     通常状態
            #
            # CRITICAL:
            #     SVXY_Z >= 3
            #     AND
            #     SVXY_ROC_10D Decile == 9
            # =============================================== #
            "level": level,
            # 適用されたシグナル名
            "signal": self.SIGNAL_NAME,
            # 判定対象日
            "date": latest["date"].strftime(
                "%Y-%m-%d"
            ),
            # =============================================== #
            # 現在値
            #
            # current は実際の市場データから
            # 計算された最新特徴量。
            #
            # svxy_volume_z
            #     過去60営業日を基準とした
            #     SVXY出来高のZ-score。
            #
            # svxy_volume_roc_decile
            #     SVXY出来高ROC(10営業日)
            #     のデシル順位。
            # =============================================== #
            "current": {

                "svxy_volume_z": round(
                    svxy_z,
                    2
                ),

                "svxy_volume_roc_decile":
                    svxy_decile
            },
            # =============================================== #
            # 閾値
            # 
            # threshold は V5 の研究結果から
            # 採用した固定値。
            #
            # 下記条件で
            #
            #     Lift = 29.14
            #     Odds Ratio = 67.67
            #     p-value = 8.9e-10
            #
            # が確認された。
            #
            # SVXY_Z >= 3
            # AND
            # SVXY_ROC_10D Top Decile
            # =============================================== #
            "threshold": {
                "svxy_volume_z": 3.0,
                "svxy_volume_roc_decile": 9
            }
        }