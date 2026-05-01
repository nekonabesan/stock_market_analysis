# 株式市場分析システム向け Copilot Instructions

## 1. このディレクトリで使う前提
`https://github.com/nekonabesan/data_analysis/tree/main/finance/notebook` の実装をベースに、株価分析・因子分析・バックテスト・予測を行う。
Copilot は以下を優先すること。

- ノートブック既存実装と整合する API・パラメータ名を使う
- 分析手法を説明する際は、定義式と実装上の列名/引数を対応付ける
- 可視化と統計結果を切り分け、再現可能なコードを優先する

---

## 2. Notebook で使用されている主要パッケージ（冒頭要件）
`https://github.com/nekonabesan/data_analysis/tree/main/finance/notebook` の実コードから確認された主要パッケージの役割は次のとおり。

### データ取得・前処理
- `yfinance`: 株価 OHLCV の取得
- `pandas`: 時系列整形、欠損処理、結合、リサンプリング
- `numpy`: ベクトル計算、対数収益率、数値変換
- `python-dotenv`: 環境変数ロード
- `pathlib`: パス管理

### テクニカル分析・チャート
- `talib` (TA-Lib): SMA, EMA, MACD, RSI, STOCH, BBANDS, Candlestick Pattern
- `mplfinance`: ローソク足可視化
- `plotly` / `plotly.graph_objects`: インタラクティブチャート
- `matplotlib`: 静的可視化
- `seaborn`: 統計可視化

### 統計モデル・機械学習
- `statsmodels.api`: OLS 回帰（CAPM/FF3 の推定）
- `sklearn.linear_model`: 線形回帰
- `getFamaFrenchFactors`: Fama-French 因子取得

### バックテスト・予測・デリバティブ
- `backtesting`: 戦略実行 (`Backtest`, `Strategy`, `optimize`)
- `prophet`: 時系列予測
- `optionprice`: オプション価格評価（欧州型）

---

## 3. TA-Lib の詳細ガイド（公式 Functions List を反映）
参照: https://ta-lib.org/functions/

TA-Lib は関数群が広く、以下カテゴリで整理して使う。

### 3.1 Overlap Studies（トレンド平滑）
- `SMA`, `EMA`, `WMA`, `DEMA`, `TEMA`, `KAMA`, `BBANDS`, `MA`

代表式:

- SMA:
	$$
	SMA_t(N)=\frac{1}{N}\sum_{i=0}^{N-1}P_{t-i}
	$$

- EMA:
	$$
	EMA_t=\alpha P_t+(1-\alpha)EMA_{t-1},\quad \alpha=\frac{2}{N+1}
	$$

- ボリンジャーバンド:
	$$
		\text{Middle}_t=SMA_t(N),\quad
		\text{Upper}_t=\text{Middle}_t+k\sigma_t,\quad
		\text{Lower}_t=\text{Middle}_t-k\sigma_t
	$$

### 3.2 Momentum Indicators（モメンタム）
- `RSI`, `MACD`, `MACDEXT`, `MACDFIX`, `MOM`, `ROC`, `ROCP`, `ROCR`, `PPO`, `STOCH`, `STOCHRSI`, `WILLR`, `CCI`, `ADX`, `ADXR`, `CMO`, `MFI`

代表式:

- RSI:
	$$
	RS_t=\frac{\text{AvgGain}_t}{\text{AvgLoss}_t},\quad
	RSI_t=100-\frac{100}{1+RS_t}
	$$

- MACD:
	$$
	MACD_t=EMA_t(\text{fast})-EMA_t(\text{slow})
	$$
	$$
	Signal_t=EMA_t(MACD,\,\text{signal}),\quad Hist_t=MACD_t-Signal_t
	$$

- ストキャスティクス:
	$$
	\%K_t=100\cdot\frac{C_t-L_t^{(N)}}{H_t^{(N)}-L_t^{(N)}},\quad
	\%D_t=SMA(\%K,m)
	$$

### 3.3 Volatility Indicators（ボラティリティ）
- `ATR`, `NATR`, `TRANGE`, `STDDEV`, `VAR`

代表式:

- True Range:
	$$
	TR_t=\max(H_t-L_t,\ |H_t-C_{t-1}|,\ |L_t-C_{t-1}|)
	$$

- ATR:
	$$
	ATR_t=SMA(TR_t,N)\ \text{(または Wilder smoothing)}
	$$

### 3.4 Volume Indicators（出来高系）
- `OBV`, `AD`, `ADOSC`

### 3.5 Price Transform / Statistic / Math / Cycle
- Price Transform: `AVGPRICE`, `MEDPRICE`, `TYPPRICE`, `WCLPRICE`
- Statistic: `BETA`, `CORREL`, `LINEARREG`, `LINEARREG_SLOPE`, `TSF`
- Hilbert Transform: `HT_*`

### 3.6 Pattern Recognition（ローソク足パターン）
公式一覧には多数の `CDL*` があり、ノートブック実装では以下を利用。

- `CDLMARUBOZU`
- `CDLBELTHOLD`
- `CDLENGULFING`
- `CDLHARAMI`
- `CDL3OUTSIDE`
- `CDL3INSIDE`

注意:
- `CDL*` は通常、`+100/-100/0` の整数シグナルを返す
- 実売買シグナルに使う際は、トレンドフィルタ（例: 長期EMA）と併用する

---

## 4. `GetMarketData` を使った yfinance 取得方法
参照: `finance/notebook/Modules/get_market_data.py`

クラス仕様:

- `get_data_from_yfinance(tickers, start=None, end=None) -> DataFrame`
- 内部で `yf.download(tickers, start=start, end=end)` を実行

推奨コード例:

```python
from pathlib import Path
from Modules.get_market_data import GetMarketData

get_market_data = GetMarketData(data_path=Path("../data/data-main"))

# 単一銘柄
df = get_market_data.get_data_from_yfinance(
		tickers="7203.T",
		start="2022-01-01",
		end="2024-12-31",
)

# 複数銘柄
multi_df = get_market_data.get_data_from_yfinance(
		tickers=["7203.T", "6758.T", "9984.T"],
		start="2022-01-01",
		end="2024-12-31",
)
```

返却データの取り扱い:
- 単一銘柄: 列は通常 `Open/High/Low/Close/Adj Close/Volume`
- 複数銘柄: MultiIndex 列になるため `stack/unstack` か `xs` で整形する

収益率変換（同モジュール）:

- 単純収益率:
	$$
	r_t=\frac{P_t}{P_{t-1}}-1
	$$

- 対数収益率:
	$$
	r_t^{(\log)}=\ln\left(\frac{P_t}{P_{t-1}}\right)
	$$

---

## 5. Notebook に実装された株価分析手法一覧（数式・モデル付き）

### 5.1 テクニカル分析

#### 5.1.1 移動平均（SMA/EMA）
- 目的: トレンド抽出、ノイズ低減
- 実装: `ta.SMA`, `ta.EMA`
- 利用例: 短期/長期クロス、200EMA フィルタ

#### 5.1.2 ゴールデンクロス / デッドクロス
- 条件:
	$$
		\text{Buy if } MA_s \uparrow MA_l,\quad
		\text{Sell/Close if } MA_s \downarrow MA_l
	$$
- 実装: `Modules/sma_cross.py` (`backtesting.lib.crossover`)

#### 5.1.3 MACD 戦略
- 指標:
	$$
	MACD_t=EMA_{12}(P_t)-EMA_{26}(P_t),\quad
	Signal_t=EMA_9(MACD_t)
	$$
- 売買:
	$$
		\text{Buy if } MACD \uparrow Signal,\quad
		\text{Close if } MACD \downarrow Signal
	$$
- 実装: `Modules/macd_cross.py`

#### 5.1.4 RSI 戦略
- 指標:
	$$
	RSI_t=100-\frac{100}{1+RS_t}
	$$
- 実装: 14期間と28期間のRSIクロス
- 売買:
	$$
		\text{Buy if } RSI_{14} \uparrow RSI_{28},\quad
		\text{Close if } RSI_{14} \downarrow RSI_{28}
	$$
- 実装: `Modules/rsi_cross.py`

#### 5.1.5 ボリンジャーバンド
- 指標:
	$$
	Upper=MA+k\sigma,\quad Lower=MA-k\sigma
	$$
- 解釈: バンド拡大=ボラ上昇、収束=ボラ低下

#### 5.1.6 ストキャスティクス
- 指標:
	$$
	\%K=100\cdot\frac{C-L_N}{H_N-L_N},\quad \%D=SMA(\%K,m)
	$$
- 解釈: 高値/安値レンジ内での終値位置

#### 5.1.7 ローソク足パターン認識（TA-Lib CDL）
- 1本足: `CDLMARUBOZU`, `CDLBELTHOLD`
- 2本足: `CDLENGULFING`, `CDLHARAMI`
- 3本足: `CDL3OUTSIDE`, `CDL3INSIDE`
- 使い方: `signal = ta.CDLxxxx(open, high, low, close)`

### 5.2 バックテスト / パラメータ最適化

#### 5.2.1 Backtesting.py による戦略検証
- 形式:
	$$
		\text{result}=Backtest(data, Strategy).run(\theta)
	$$
- 指標: Return, Sharpe, Max Drawdown, #Trades 等

#### 5.2.2 グリッド最適化
- 形式:
	$$
		heta^*=\arg\max_{\theta\in\Theta} J(\theta)
	$$
	ここで $J$ は `maximize='Return [%]'` など
- 注意: `constraint` は picklable な named function を使う

### 5.3 ファクターモデル / 回帰分析

#### 5.3.1 CAPM（単一因子）
$$
R_i-R_f=\alpha_i+\beta_i(R_m-R_f)+\varepsilon_i
$$

- $\beta$: 市場感応度
- $\alpha$: 超過収益（Jensen's alpha）

#### 5.3.2 Fama-French 3因子モデル
$$
R_i-R_f=\alpha_i+\beta_m(Mkt-RF)+\beta_s SMB+\beta_h HML+\varepsilon_i
$$

- `Mkt-RF`: 市場超過収益
- `SMB`: 小型株プレミアム
- `HML`: バリュープレミアム
- 実装: `statsmodels.OLS`

### 5.4 時系列予測

#### 5.4.1 Prophet
加法モデル:
$$
y(t)=g(t)+s(t)+h(t)+\varepsilon_t
$$

- $g(t)$: トレンド
- $s(t)$: 季節性
- $h(t)$: 休日効果

### 5.5 デリバティブ / FX 応用

#### 5.5.1 欧州オプション（Black-Scholes 系）
標準形（コール）:
$$
C=S_0N(d_1)-Ke^{-rT}N(d_2)
$$

#### 5.5.2 FX フォワード（カバード金利平価）
$$
F=S\cdot\frac{1+r_d T_d}{1+r_f T_f}
$$

---

## 6. 実装時のルール（このプロジェクト向け）
### python コードのユニットテストについて
- pytest を使用すること
- venv環境は使用しないこと
- テストコードはコンテナ上で実行すること
- テストには`container/Makefile`に定義された`make test`を使用すること
- テストを正常終了させる目的でテスト対象のソースコードを修正する事は禁止とする


