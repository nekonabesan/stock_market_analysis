import matplotlib.pyplot as plt
import pandas as pd

class ComputeFibonacciExtension:
    def __init__(self):
        pass

    def compute_fibonacci_extension(
        self,
        df: pd.DataFrame, 
        price_col: str = "close", 
        high: float = None, 
        low: float = None, 
        lookback: int = 120
    ):
        """
        フィボナッチ・エクステンションを計算し、グラフ描画オブジェクトとともに返すメソッド。
        下方向（安値側）と上方向（高値側）の両方のターゲットを計算する。

        Returns
        -------
        dict
            {
                "fib_levels_down": dict,
                "fib_levels_up": dict,
                "swing_high": float,
                "swing_low": float,
                "df_with_fib": pandas.DataFrame,
                "plot_obj": matplotlib.figure.Figure
            }
        """

        # --- 1. スイング高値・安値の決定 ---
        if high is None:
            swing_high = df["high"].tail(lookback).max()
        else:
            swing_high = high

        if low is None:
            swing_low = df["low"].tail(lookback).min()
        else:
            swing_low = low

        # --- 2. フィボナッチ・エクステンション計算 ---
        diff = swing_high - swing_low

        # 下方向（安値側）
        fib_levels_down = {
            "1.000": swing_low,
            "1.272": swing_low - 0.272 * diff,
            "1.382": swing_low - 0.382 * diff,
            "1.618": swing_low - 0.618 * diff,
        }

        # 上方向（高値側）
        fib_levels_up = {
            "1.272": swing_high + 0.272 * diff,
            "1.382": swing_high + 0.382 * diff,
            "1.618": swing_high + 0.618 * diff,
            "2.000": swing_high + 1.000 * diff,  # 強いトレンド用
        }

        # --- 3. DataFrame にフィボナッチ値を追加 ---
        df = df.copy()
        for name, value in fib_levels_down.items():
            df[f"fib_down_{name}"] = value
        for name, value in fib_levels_up.items():
            df[f"fib_up_{name}"] = value

        # --- 4. グラフ描画 ---
        fig, ax = plt.subplots(figsize=(14, 6))

        # 時系列価格
        ax.plot(df["date"], df[price_col], label="Price", color="black")

        # 下方向エクステンション
        for name, value in fib_levels_down.items():
            ax.hlines(
                value,
                xmin=df["date"].min(),
                xmax=df["date"].max(),
                linestyles="dashed",
                colors="red",
                label=f"Fib Down {name}"
            )

        # 上方向エクステンション
        for name, value in fib_levels_up.items():
            ax.hlines(
                value,
                xmin=df["date"].min(),
                xmax=df["date"].max(),
                linestyles="dashed",
                colors="blue",
                label=f"Fib Up {name}"
            )

        # スイング高値・安値のマーカー
        ax.scatter(df["date"].iloc[-1], swing_low, color="red", label="Swing Low")
        ax.scatter(df["date"].iloc[-1], swing_high, color="green", label="Swing High")

        ax.set_title("Fibonacci Extension Projection (Up & Down)")
        ax.legend()
        ax.grid(True)
        fig.autofmt_xdate()

        # --- 5. 結果を返す ---
        return {
            "fib_levels_down": fib_levels_down,
            "fib_levels_up": fib_levels_up,
            "swing_high": swing_high,
            "swing_low": swing_low,
            "df_with_fib": df,
            "plot_obj": fig
        }
