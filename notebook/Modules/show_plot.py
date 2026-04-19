import plotly.graph_objs as go
import datetime as dt
import talib as ta
import pandas as pd
from pathlib import Path
from typing import List, Optional
from Modules.get_market_data import GetMarketData

class ShowPlot:
    def __init__(self):
        pass

    def show_ichimoku(
        self,
        code: str, 
        name: str, 
        start: str, 
        end: str
    ) -> None:
        """
        一目均衡表を作成する関数。

        Args:
            code (str): 株式コード。
            name (str): 銘柄名。
            start (str): 表示するデータの開始日。
            end (str): 表示するデータの終了日。

        Returns:
            None: グラフを表示するため戻り値はなし。
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

        high = df['High']
        low = df['Low']
        close = df['Close']

        if isinstance(high, pd.DataFrame):
            high = high.iloc[:, 0]
        if isinstance(low, pd.DataFrame):
            low = low.iloc[:, 0]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        high_values = high.to_numpy(dtype=float)
        low_values = low.to_numpy(dtype=float)
        close_values = close.to_numpy(dtype=float)

        # 転換線: 9期間の最高値と最安値の平均
        conversion_high = ta.MAX(high_values, timeperiod=9)
        conversion_low = ta.MIN(low_values, timeperiod=9)
        df["conversion_line"] = (conversion_high + conversion_low) / 2

        # 基準線: 26期間の最高値と最安値の平均
        base_high = ta.MAX(high_values, timeperiod=26)
        base_low = ta.MIN(low_values, timeperiod=26)
        df["base_line"] = (base_high + base_low) / 2

        # 先行スパン1: 転換線と基準線の平均を26期間先行させたもの
        df["leading_span1"] = ((df['conversion_line'] + df['base_line']) / 2).shift(26)

        # 先行スパン2: 52期間の最高値と最安値の平均を26期間先行させたもの
        senkou_span_2_high = ta.MAX(high_values, timeperiod=52)
        senkou_span_2_low = ta.MIN(low_values, timeperiod=52)
        senkou_span_2 = pd.Series((senkou_span_2_high + senkou_span_2_low) / 2, index=df.index)
        df["leading_span2"] = senkou_span_2.shift(26)

        # 遅行スパン: 終値を26期間遅行させたもの
        df["lagging_span"] = close.shift(-26)
        
        # チャートに表示する期間
        rdf = df[start:end]
        # インデックスを文字列型に
        rdf.index = pd.to_datetime(rdf.index).strftime("%Y-%m-%d")

        # レイアウト設定
        layout = {
                "height": 700,
                "title"  : { "text": name, "x":0.5 },
                "xaxis" : { "rangeslider": { "visible": False }, "type": "category" },
            "yaxis": { "domain": [.05, 1.0], "title": "価格（円）", "side": "left", "tickformat": "," },
                "yaxis2": { "domain": [.0, .05] }, # X軸日付表示 
                }

        # データの設定
        data =  [
            go.Candlestick(yaxis="y", x=rdf.index,
                                        open=rdf['Open'],
                                        high=rdf['High'],
                                        low=rdf['Low'],
                                        close=rdf['Close'],
                                        increasing_line_color="red", 
                                        decreasing_line_color="gray",
                                        name=name),

            # 各線を表示
            go.Scatter(x=rdf.index, y=rdf["base_line"], name="基準線", mode="lines", line=dict(color='green', width=1)),

            go.Scatter(x=rdf.index, y=rdf["conversion_line"], name="転換線", mode="lines", line=dict(color='darkviolet', width=1)),


            go.Scatter(x=rdf.index, y=rdf["leading_span1"], name="先行スパン1", mode="lines", line=dict(color="gainsboro", width=1)),
            go.Scatter(x=rdf.index, y=rdf["leading_span2"], name="先行スパン2", mode="lines", line=dict(color="gainsboro", width=1)),
            
            go.Scatter(x=rdf.index, y=rdf["lagging_span"], name="遅行スパン", mode="lines", line=dict(color='cornflowerblue', width=1)),

            # 先行スパン1と先行スパン2の間を塗りつぶす
            go.Scatter(x=rdf.index, y=rdf["leading_span1"], name="先行スパン1", mode="lines", 
                        fill=None, line=dict(width=1, color="gainsboro"), showlegend=False),
            go.Scatter(x=rdf.index, y=rdf["leading_span2"], name="先行スパン2", mode="lines", 
                        fill='tonexty', line=dict(width=1, color="gainsboro"), fillcolor="rgba(170,170,170,.3)", showlegend=False),
        ]

        # Figure作成
        fig = go.Figure(data=data, layout=go.Layout(layout))

        # 日付表示
        fig.update_layout({
        "xaxis":{
            "showgrid": False,
            "tickvals": rdf.index[::10],
            "ticktext": ["{}-{}".format(x.split("-")[1], x.split("-")[2]) for x in rdf.index[::10]]
            }
        })

        # グラフを表示
        fig.show()

    def create_basic_chart(
            self,
            df: pd.DataFrame, 
            name: str | None = None,
            code: str | None = None,
            start: str | None = None,
            end: str | None = None
        ) -> go.Figure:
        """
        APIから取得したデータをもとに基本的なローソク足チャートを作成する
        /api/v1/time_series_data/stock/
        /api/v1/time_series_data/commodity/

        Args:
            df (pd.DataFrame): 株価データを含むDataFrame。'Open'、'High'、'Low'、'Close'列が必要。
            name (str): 銘柄名。
            code (str): 銘柄コード。
            start (str): 開始日（YYYY-MM-DD形式）。
            end (str): 終了日（YYYY-MM-DD形式）。
        Returns:
        """
        # date列をインデックスに設定してスライス
        df = df.set_index(pd.to_datetime(df["date"])).sort_index()
        df = df[start:end]

        # レイアウト設定
        layout = {
                "height": 900,
                "title": {"x": 0.5, "text": f"{name or code} {code}"},
                "xaxis": {"rangeslider": {"visible": False}, "type": "category"},
                "yaxis1": {"domain": [.36, 1.0], "title": "価格（円）", "side": "left", "tickformat": ","},
                "yaxis2": {"domain": [.30, .36]},
                "yaxis3": {"domain": [.20, .295], "title": "MACD", "side": "right"},
                "yaxis4": {"domain": [.10, .195], "title": "RCI", "side": "right"},
                "yaxis5": {"domain": [.0, .095], "title": "Volume", "side": "right"},
                "plot_bgcolor": "light blue",
        }

        # データの設定
        data = [
                go.Candlestick(
                    yaxis="y1",
                    x=df.index,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    increasing_line_color="red",
                    decreasing_line_color="gray",
                    name=code,
                ),
                go.Scatter(yaxis="y1", x=df.index, y=df["ma5"], name="MA5", line={"color": "royalblue", "width": 1.2}),
                go.Scatter(yaxis="y1", x=df.index, y=df["ma25"], name="MA25", line={"color": "lightseagreen", "width": 1.2}),
                go.Scatter(yaxis="y1", x=df.index, y=df["upper2"], name="", line={"color": "lavender", "width": 0}),
                go.Scatter(
                    yaxis="y1",
                    x=df.index,
                    y=df["lower2"],
                    name="BB",
                    line={"color": "lavender", "width": 0},
                    fill="tonexty",
                    fillcolor="rgba(170,170,170,.2)",
                ),
                go.Scatter(yaxis="y3", x=df.index, y=df["macd"], name="macd", line={"color": "magenta", "width": 1}),
                go.Scatter(yaxis="y3", x=df.index, y=df["macd_signal"], name="signal", line={"color": "green", "width": 1}),
                go.Bar(yaxis="y3", x=df.index, y=df["hist"], name="histgram", marker={"color": "slategray"}),
                go.Scatter(yaxis="y4", x=df.index, y=df["rci9"], name="RCI9", line={"color": "magenta", "width": 1}),
                go.Scatter(yaxis="y4", x=df.index, y=df["rci26"], name="RCI26", line={"color": "green", "width": 1}),
                go.Bar(yaxis="y5", x=df.index, y=df["volume"], name="Volume", marker=dict(color="slategray")),
        ]

        # Figure作成
        fig = go.Figure(data=data, layout=go.Layout(layout))

        # 日付表示
        fig.update_layout(
                {
                    "xaxis": {
                        "tickvals": df.index[::4],
                        "ticktext": [x.strftime("%m-%d") for x in df.index[::4]],
                    }
                }
        )
        return fig