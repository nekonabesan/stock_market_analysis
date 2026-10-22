import pandas as pd
import matplotlib.pyplot as plt

from typing import Tuple

class FibonacciExtension:
    """
    extension_direction : str, default "auto"
    フィボナッチ・エクステンションを算出する方向を指定する。

    auto
        trend_direction に従って方向を自動決定する。

        upward の場合:
            高値(top)を基準として上方向の
            エクステンションを算出する。

        downward の場合:
            安値(bottom)を基準として下方向の
            エクステンションを算出する。

    up
        trend_direction の値に関係なく、
        高値(top)を基準として上方向の
        エクステンションを算出する。

        主に以下の用途を想定する。

        - VIX指数の急騰シナリオ分析
        - ブレイクアウト後の上値目標算出
        - レジスタンス候補の推定

    down
        trend_direction の値に関係なく、
        安値(bottom)を基準として下方向の
        エクステンションを算出する。

        主に以下の用途を想定する。

        - 下落トレンド継続時の目標価格算出
        - サポート候補の推定
    """
    def __init__(self):
        pass

    def _fibonacci_extension(
        self,
        df: pd.DataFrame,
        price_col: str = "close",
        lookback: int = 20,
        trend_direction: str = "auto",
        extension_direction: str = "auto"
    ) -> Tuple[str, float, int, float, int, dict, pd.DataFrame, pd.DataFrame]:
        """
        各日時点のFib拡張水準をローリング計算
        Parameters
        ----------
        df : pd.DataFrame
            株価データを含むデータフレーム
        price_col : str, default "close"
            株価列の名前
        lookback : int, default 20
            過去何期間を対象に計算するか
        trend_direction : str, default "auto"
            トレンド方向の指定 ("auto" で自動判定)
        extension_direction : str, default "auto"
            Extension方向の指定 ("auto" で自動判定)
        """
        work_df = (df[df[price_col] > 0].tail(lookback).copy())
        # 欠損値や0の株価を除外
        work_df = work_df.dropna(subset=[price_col])
        # 0以下の株価を除外
        work_df = work_df[work_df[price_col] > 0]
        # 過去lookback期間のデータを取得
        top = work_df[price_col].max()
        bottom = work_df[price_col].min()
        # 高値・安値のインデックスを取得
        top_idx = work_df[price_col].idxmax()
        bottom_idx = work_df[price_col].idxmin()
        # 高値・安値の差分を計算
        diff = top - bottom
        # トレンド判定
        if trend_direction == "auto":
            # 自動判定の場合、安値が先に来れば上昇トレンド、そうでなければ下降トレンドとする
            if bottom_idx < top_idx:
                trend_direction = "upward"
            else:
                trend_direction = "downward"
        # Extension方向決定
        if extension_direction == "auto":
            # Extension方向を自動判定
            if trend_direction == "upward":
                extension_direction = "up"
            else:
                extension_direction = "down"
        # 上方向Extension
        if extension_direction == "up":
            fib_levels = {
                "1.000": top,
                "1.272": top + diff * 0.272,
                "1.618": top + diff * 0.618,
                "2.000": top + diff * 1.000,
                "2.618": top + diff * 1.618,
                "4.236": top + diff * 3.236,
            }
        # 下方向Extension
        else:
            fib_levels = {
                "1.000": bottom,
                "1.272": bottom - diff * 0.272,
                "1.618": bottom - diff * 0.618,
                "2.000": bottom - diff * 1.000,
                "2.618": bottom - diff * 1.618,
                "4.236": bottom - diff * 3.236,
            }
        # 結果用のデータフレームを作成
        result_df = work_df.copy()
        # 各Fib拡張水準を結果データフレームに追加
        for level_name, level_value in fib_levels.items():
            result_df[f"fib_extension_{level_name}"] = level_value
        # 結果を返す
        return (
            trend_direction,
            top,
            top_idx,
            bottom,
            bottom_idx,
            fib_levels,
            result_df,
            work_df
        )

    def fibonacci_extension(
        self,
        df: pd.DataFrame,
        price_col: str = "close",
        lookback: int = 20,
        trend_direction: str = "auto",
        extension_direction: str = "auto"
    ) -> Tuple[str, float, int, float, int, dict, pd.DataFrame, pd.DataFrame]:
        """
        各日時点のFibを計算
        Parameters
        ----------
        df : pd.DataFrame
            株価データを含むデータフレーム
        price_col : str, default "close"
            株価列の名前
        lookback : int, default 20
            過去何期間を対象に計算するか
        trend_direction : str, default "auto"
            トレンド方向の指定 ("auto" で自動判定)
        extension_direction : str, default "auto"
            Extension方向の指定 ("auto" で自動判定)
        Returns
        -------
        Tuple[str, float, int, float, int, dict, pd.DataFrame, pd.DataFrame]
            計算結果を含むタプル
        """
        return self._fibonacci_extension(
            df=df,
            price_col=price_col,
            lookback=lookback,
            trend_direction=trend_direction,
            extension_direction=extension_direction
        )

    def fibonacci_extension_technical_chart(
        self,
        df: pd.DataFrame,
        price_col: str = "close",
        lookback: int = 120,
        trend_direction: str = "auto",
        extension_direction: str = "auto"
    ) -> dict:
        """
        Fibを用いたテクニカルチャート用のデータを取得
        Parameters
        ----------
        df : pd.DataFrame
            株価データを含むデータフレーム
        price_col : str, default "close"
            株価列の名前
        lookback : int, default 120
            過去何期間を対象に計算するか
        trend_direction : str, default "auto"
            トレンド方向の指定 ("auto" で自動判定)
        extension_direction : str, default "auto"
            Extension方向の指定 ("auto" で自動判定)
        Returns
        -------
        dict
            テクニカルチャート用のデータを含む辞書
        """

        # Fibonacci Extensionを計算
        (
            trend_direction,
            top,
            top_idx,
            bottom,
            bottom_idx,
            fib_levels,
            result_df,
            work_df
        ) = self._fibonacci_extension(
            df=df,
            price_col=price_col,
            lookback=lookback,
            trend_direction=trend_direction,
            extension_direction=extension_direction
        )
        # プロットの準備
        fig, ax = plt.subplots(figsize=(14, 6))
        # 株価のプロット
        ax.plot(
            work_df["date"],
            work_df[price_col],
            color="black",
            label="Close"
        )
        # Fibonacci Extensionレベルのプロット
        colors = {
            "1.272": "orange",
            "1.618": "green",
            "2.000": "blue",
            "2.618": "purple",
            "4.236": "red"
        }
        # 各Fibonacci Extensionレベルをプロット
        for level_name, level_value in fib_levels.items():
            color = colors.get(level_name, "gray")
            # Fibonacci Extensionレベルを水平線としてプロット
            ax.hlines(
                level_value,
                xmin=work_df["date"].min(),
                xmax=work_df["date"].max(),
                linestyle="dashed",
                color=color,
                label=f"Ext {level_name}"
            )
        # トップとボトムのプロット
        ax.scatter(
            work_df.loc[top_idx, "date"],
            top,
            color="green",
            s=100,
            label="Top"
        )
        # ボトムのプロット
        ax.scatter(
            work_df.loc[bottom_idx, "date"],
            bottom,
            color="red",
            s=100,
            label="Bottom"
        )
        # チャートタイトルの設定
        ax.set_title("Fibonacci Extension")
        ax.grid(True)
        ax.legend()
        fig.autofmt_xdate()
        return {
            "trend_direction": trend_direction,
            "top": top,
            "bottom": bottom,
            "fib_levels": fib_levels,
            "df_with_fib": result_df,
            "plot_obj": fig
        }

    def fibonacci_extension_for_timeseries(
        self,
        df: pd.DataFrame,
        price_col: str = "close",
        lookback: int = 120,
        trend_direction: str = "auto",
        extension_direction: str = "auto"
    ) -> pd.DataFrame:
        """
        各日時点のFib水準をローリング計算

        Parameters
        ----------
        df : pd.DataFrame
            株価データを含むデータフレーム

        price_col : str, default "close"
            株価列名

        lookback : int, default 120
            過去何期間を対象に計算するか

        trend_direction : str, default "auto"
            トレンド方向

        extension_direction : str, default "auto"
            Extension方向

        Returns
        -------
        pd.DataFrame
            各日時点のFib Extension水準
        """
        results = []
        # lookback本確保してから計算開始
        for i in range(lookback, len(df)):
            # 現在のローリングウィンドウのデータを取得
            current_df = df.iloc[: i + 1]
            (
                trend,
                top,
                top_idx,
                bottom,
                bottom_idx,
                fib_levels,
                _,
                _
            ) = self._fibonacci_extension(
                df=current_df,
                price_col=price_col,
                lookback=lookback,
                trend_direction=trend_direction,
                extension_direction=extension_direction
            )
            # 現在時点の結果
            row = {
                "date": current_df.iloc[-1]["date"],
                "close": current_df.iloc[-1][price_col],
                "fib_trend": trend,
                "fib_top": top,
                "fib_bottom": bottom,
            }
            # Extensionレベル追加
            for level_name, level_value in fib_levels.items():
                # Extensionレベルを行に追加
                row[f"fib_extension_{level_name}"] = level_value
            # 上方向Extensionとの差分
            if extension_direction == "up":
                # 上方向Extensionとの差分を計算
                row["distance_ext_1272"] = (
                    row["close"]
                    - fib_levels["1.272"]
                )
                row["distance_ext_1618"] = (
                    row["close"]
                    - fib_levels["1.618"]
                )
                row["distance_ext_2000"] = (
                    row["close"]
                    - fib_levels["2.000"]
                )
                row["distance_ext_2618"] = (
                    row["close"]
                    - fib_levels["2.618"]
                )
                row["distance_ext_4236"] = (
                    row["close"]
                    - fib_levels["4.236"]
                )
            results.append(row)
        return pd.DataFrame(results)