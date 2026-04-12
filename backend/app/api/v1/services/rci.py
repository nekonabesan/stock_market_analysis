import pandas as pd
from pathlib import Path
from typing import List, Optional

class Rci:
    def __init__(self, timeperiod: int = 9):
        self.timeperiod = timeperiod

    def RCI(self, close: List[float], timeperiod: int = 9) -> Optional[List[float]]:
        """
        RCI (Rank Correlation Index) を計算する関数

        Args:
            close (List[float]): 終値のリスト
            timeperiod (int): 計算期間（デフォルトは9）
        Returns:
            List[Optional[float]]: 計算されたRCI値のリスト、計算期間に満たない場合はNone
        """
        self.timeperiod = timeperiod
        # RCIの値を格納するリスト
        rci = []

        # データフレームを作成し、列名を"Close"に設定
        df = pd.DataFrame(close, columns=["Close"])
        
        for i in range(len(close)):
            if i < self.timeperiod - 1:
                # 期間に満たない場合はNone
                rci.append(None)  # 計算期間に満たない場合はNoneを追加
                continue
            d = 0
            # 期間の終値に対応するランクを計算
            # (i - timeperiod + 1)行から(i + 1)行までの期間の終値を取得
            sliced_df = df.iloc[i - self.timeperiod + 1:i + 1]

            # Rankを計算してCloseの列を取得
            rank_proce = sliced_df.rank(method='min', ascending=False)['Close'].values

            # 日付のランクと終値のランクの差を2乗して合計
            for j in range(self.timeperiod):
                d += ((self.timeperiod - j) - rank_proce[j]) ** 2

            # RCI計算式に適用
            rci_value = (1 - (6 * d) / (self.timeperiod * (self.timeperiod ** 2 - 1))) * 100
            rci.append(rci_value)

        return rci