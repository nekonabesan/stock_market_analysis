import datetime as dt
import plotly.graph_objects as go
import talib as ta
import pandas as pd
from pathlib import Path
from typing import List, Optional
from Modules.get_market_data import GetMarketData

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
    
    def show_chart(self, code: str, name: str, start: str, end: str) -> None:
        """
        指定された株価データを使用して、移動平均、ボリンジャーバンド、
        MACD、RSI、RCIを含むチャートを表示する関数

        Args:
            code (str): 銘柄コード
            name (str): 銘柄名
            start (str): 表示するデータの開始日（'YYYY-MM-DD'形式）
            end (str): 表示するデータの終了日（'YYYY-MM-DD'形式）
        """
        # 開始日を文字列からdatetime型に変換
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        # データ取得開始日を開始日の約300日前に設定
        data_acquisition_start_date = (start_date - dt.timedelta(days=300)).strftime('%Y-%m-%d')
        
        # GetMarketDataインスタンスを作成してyfinanceからデータを取得
        get_market_data = GetMarketData(Path('/workspace/data'))
        df = get_market_data.get_data_from_yfinance(
            tickers=code,
            start=data_acquisition_start_date,
            end=end,
        )

        # yfinanceがMultiIndexを返すケースに対応
        if isinstance(df.columns, pd.MultiIndex):
            df = df.droplevel(level=1, axis=1)

        close = df['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        close_values = close.to_numpy(dtype=float)
        high_values = df['High'].to_numpy(dtype=float)
        low_values = df['Low'].to_numpy(dtype=float)

        # 移動平均線の算出
        df["ma5"] = ta.SMA(close_values, timeperiod=5)
        df["ma25"] = ta.SMA(close_values, timeperiod=25)

        # パラボリックの計算
        df['SAR'] = ta.SAR(high_values, low_values, acceleration=0.02, maximum=0.2)

        # ボリンジャーバンドの算出
        upper2, _, lower2 = ta.BBANDS(close_values, timeperiod=25, nbdevup=2, nbdevdn=2, matype=0)
        df["upper2"], df["lower2"] = upper2, lower2

        # RSIの算出
        rsi14 = ta.RSI(close_values, timeperiod=14)
        rsi28 = ta.RSI(close_values, timeperiod=28)
        df["rsi14"], df["rsi28"] = rsi14, rsi28

        # MACDの算出
        macd, macdsignal, macdhist = ta.MACD(close_values, fastperiod=12, slowperiod=26, signalperiod=9)
        df["macd"], df["macdsignal"], df["macdhist"] = macd, macdsignal, macdhist

        # RCIの算出
        rci9 = self.RCI(close_values.tolist(), timeperiod=9)
        rci26 = self.RCI(close_values.tolist(), timeperiod=26)
        df["rci9"], df["rci26"] = rci9, rci26

        df = df[start:end]
        df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')

        # ハッシュ形式でレイアウトを指定 ----(1)
        layout = {
            "height": 1000,
            "width": 1000,
            "xaxis": { "rangeslider": { "visible": False }, "type": "category" },
            "yaxis": { "domain": [.36, 1.0], "title": "価格（円）", "side": "left", "tickformat": "," },
            "yaxis2": { "domain": [.30, .36] },
            # MACD
            "yaxis3": { "domain": [.20, .295], "title": "MACD", "side": "right" },
            # RSI
            "yaxis4": { "domain": [.10, .195], "title": "RSI", "side": "right" },
            # RCI
            "yaxis5": { "domain": [.0, .095], "title": "RCI", "side": "right" },
            "plot_bgcolor":"light blue"
        }

        # データの設定
        data = [
            go.Candlestick(yaxis="y", x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                increasing_line_color='red',
                decreasing_line_color='gray',
                name=name,
            ),
            # 5日移動平均線
            go.Scatter(yaxis="y", x=df.index, y=df["ma5"], name="MA5", line={ "color": "royalblue", "width": 1.2 } ),
        
            # 25日移動平均線
            go.Scatter(yaxis="y", x=df.index, y=df["ma25"], name="MA25", line={ "color": "lightseagreen", "width": 1.2 } ),

            # パラボリックSAR
            go.Scatter(
                yaxis="y",
                x=df.index,
                y=df["SAR"],
                name="SAR",
                mode="markers",
                marker={ "color": "orange", "size": 6 }
            ),
        
            # ボリンジャーバンド
            go.Scatter(yaxis="y", x=df.index ,y=df["upper2"], name= "", line={ "color": "lavender", "width": 0 }),
            go.Scatter(yaxis="y", x=df.index ,y=df["lower2"], name= "BB", line={ "color": "lavender", "width": 0 }, 
                    fill="tonexty", fillcolor="rgba(170,170,170,.2)"),

            # MACD
            go.Scatter(yaxis="y3" ,x=df.index ,y=df["macd"], name= "macd", line={ "color": "magenta", "width": 1 } ),
            go.Scatter(yaxis="y3" ,x=df.index ,y=df["macdsignal"], name= "signal", line={ "color": "green", "width": 1 } ),
            go.Bar(yaxis="y3" ,x=df.index, y=df["macdhist"], name= "histgram", marker={ "color": "slategray" } ) ,
        
            # RSI
            go.Scatter(yaxis="y4" ,x=df.index ,y=df["rsi14"], name= "RSI14",line={ "color": "magenta", "width": 1 } ),
            go.Scatter(yaxis="y4" ,x=df.index ,y=df["rsi28"], name= "RSI28",line={ "color": "green", "width": 1 } ),

            # RCI
            go.Scatter(yaxis="y5" ,x=df.index ,y=df["rci9"], name= "RCI9",line={ "color": "magenta", "width": 1 } ),
            go.Scatter(yaxis="y5" ,x=df.index ,y=df["rci26"], name= "RCI26",line={ "color": "green", "width": 1 } ),
        ]

        # Figure作成
        fig = go.Figure(data=data, layout=go.Layout(layout))

        # 日付表示
        fig.update_layout({
            "xaxis":{
                "range": [df.index.min(), df.index.max()],  
                "tickvals": df.index[::4],
                "ticktext": ["{}-{}".format(x.split("-")[1], x.split("-")[2]) for x in df.index[::4]]
                }
        })

        # グラフを表示
        fig.show()

