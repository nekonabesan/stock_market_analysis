import pandas as pd
import matplotlib.pyplot as plt

from typing import Tuple

class FibonacciRetracement:

    def __init__(self):
        pass

    def _fibonacci_retracement(
            self,
            df: pd.DataFrame,
            price_col: str = "close",
            lookback: int = 120,
            trend_direction: str = "auto"
    ) -> Tuple[str, float, int, float, int, dict, pd.DataFrame, pd.DataFrame]:
        work_df = (df[df[price_col] > 0].tail(lookback).copy())
        # 欠損値や0の株価を除外
        work_df = work_df.dropna(subset=[price_col])
        # 0以下の株価を除外
        work_df = work_df[work_df[price_col] > 0]
        # 高値と安値を取得
        top = work_df[price_col].max()
        bottom = work_df[price_col].min()
        # 高値と安値のインデックスを取得
        top_idx = work_df[price_col].idxmax()
        bottom_idx = work_df[price_col].idxmin()
        # 値幅を計算
        diff = top - bottom
        # トレンド自動判定
        if trend_direction == "auto":
            if bottom_idx < top_idx:
                trend_direction = "upward"
            else:
                trend_direction = "downward"
        # 上昇トレンド
        if trend_direction == "upward":
            fib_levels = {
                "0.000": top,
                "0.236": top - diff * 0.236,
                "0.382": top - diff * 0.382,
                "0.500": top - diff * 0.500,
                "0.618": top - diff * 0.618,
                "0.786": top - diff * 0.786,
                "1.000": bottom,
            }
        # 下降トレンド
        else:
            fib_levels = {
                "0.000": bottom,
                "0.236": bottom + diff * 0.236,
                "0.382": bottom + diff * 0.382,
                "0.500": bottom + diff * 0.500,
                "0.618": bottom + diff * 0.618,
                "0.786": bottom + diff * 0.786,
                "1.000": top,
            }
        # DataFrame追加
        result_df = work_df.copy()
        # 各フィボナッチレベルをDataFrameに追加
        for level_name, level_value in fib_levels.items():
            col_name = (f"fib_retracement_{level_name}")
            result_df[col_name] = level_value
        return (trend_direction, top, top_idx, bottom, bottom_idx, fib_levels, result_df, work_df)
        

    def fibonacci_retracement(
            self,
            df: pd.DataFrame,
            price_col: str = "close",
            lookback: int = 120,
            trend_direction: str = "auto"
    ) -> Tuple[str, float, int, float, int, dict, pd.DataFrame, pd.DataFrame]:
        """
        Fibonacci Retracement

        Parameters
        ----------
        df : pd.DataFrame
        price_col : str
            価格列名
        lookback : int
            参照期間
        trend_direction : str
            auto / upward / downward

        Returns
        -------
        Tuple[str, float, int, float, int, dict, pd.DataFrame, pd.DataFrame]
        """
        return self._fibonacci_retracement(
            df=df,
            price_col=price_col,
            lookback=lookback,
            trend_direction=trend_direction
        )
    

    def fibonacci_retracement_technical_chart (
        self,
        df: pd.DataFrame,
        price_col: str = "close",
        lookback: int = 120,
        trend_direction: str = "auto"
    ) -> dict:
        """
        Fibonacci Retracement

        Parameters
        ----------
        df : pd.DataFrame

        price_col : str
            価格列名

        lookback : int
            参照期間

        trend_direction : str
            auto / upward / downward

        Returns
        -------
        dict
        """
        trend_direction, top, top_idx, bottom, bottom_idx, fib_levels, result_df, work_df = self._fibonacci_retracement(
            df=df,
            price_col=price_col,
            lookback=lookback,
            trend_direction=trend_direction
        )
        # グラフ
        fig, ax = plt.subplots(figsize=(14, 6))

        ax.plot(
            work_df["date"],
            work_df[price_col],
            color="black",
            label="Close"
        )

        colors = {
            "0.236": "orange",
            "0.382": "gold",
            "0.500": "blue",
            "0.618": "green",
            "0.786": "purple"
        }

        for level_name, level_value in fib_levels.items():

            color = colors.get(level_name, "gray")

            ax.hlines(
                level_value,
                xmin=work_df["date"].min(),
                xmax=work_df["date"].max(),
                linestyle="dashed",
                color=color,
                label=f"Fib {level_name}"
            )

        ax.scatter(
            work_df.loc[top_idx, "date"],
            top,
            color="green",
            s=100,
            label="Top"
        )

        ax.scatter(
            work_df.loc[bottom_idx, "date"],
            bottom,
            color="red",
            s=100,
            label="Bottom"
        )

        ax.set_title(
            "Fibonacci Retracement"
        )

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

    def fibonacci_retracement_for_timeseries(
        self,
        df: pd.DataFrame,
        price_col: str = "close",
        lookback: int = 120,
        trend_direction: str = "auto"
    ) -> pd.DataFrame:
        """
        各日時点のFib水準をローリング計算
        """
        results = []
        # lookback本確保してから計算開始
        for i in range(lookback, len(df)):
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
            ) = self._fibonacci_retracement(
                df=current_df,
                price_col=price_col,
                lookback=lookback,
                trend_direction=trend_direction
            )
            # 現在のローリングウィンドウに対してFib水準を計算
            row = {
                "date": current_df.iloc[-1]["date"],
                "close": current_df.iloc[-1][price_col],
                "fib_trend": trend,
                "fib_top": top,
                "fib_bottom": bottom,
            }
            # 各Fib水準を行に追加
            for level_name, level_value in fib_levels.items():

                row[
                    f"fib_retracement_{level_name}"
                ] = level_value

            results.append(row)

        return pd.DataFrame(results)