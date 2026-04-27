import os
import pandas as pd
import numpy as np
import datetime as dt

from Modules.reques_api import RequestApi


class Financial:
    """
    ◆ 2. 財務データ（Financials）
    • 売上高（Revenue）
    • 営業利益（Operating Income）
    • 純利益（Net Income）
    • EBITDA（企業による）
    • 総資産（Total Assets）
    • 総負債（Total Liabilities）
    • 現金（Cash）
    • 営業キャッシュフロー（Operating Cash Flow）
    • フリーキャッシュフロー（Free Cash Flow）
    """
    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.request_api = RequestApi(self.api_base_url)
        pass

    def _first_nonnull(self, row: pd.Series, keys: list) -> any:
        """
        row の中から keys の順番で最初に見つかった非null値を返す。
        すべて null の場合は None を返す。
        """
        for k in keys:
            if k in row and pd.notna(row[k]):
                return row[k]
        return None
    
    def calc_ev(
        self,
        stock_df: pd.DataFrame,
        bs_df: pd.DataFrame,

    ):
        """
        Enterprise Valueを計算して返す
        Args:
            stock_df (pd.DataFrame): 株価の時系列データを含むDataFrame。少なくとも 'date' と 'close' カラムが必要。
            bs_df (pd.DataFrame): バランスシートの時系列データを含むDataFrame。少なくとも 'date' カラムと、発行株式数、負債、現金に関連するカラムが必要。
        Returns:
            pd.DataFrame: 'Date' をインデックスとし、'price', 'shares', 'market_cap', 'total_debt', 'cash', 'EV' カラムを含むDataFrame。
        """
        results = []
        stock_df['date'] = pd.to_datetime(stock_df['date'], errors='coerce')
        stock_df = stock_df.sort_values('date')
        bs_df['date'] = pd.to_datetime(bs_df['date'], errors='coerce')
        bs_df = bs_df.sort_values('date')
        
        for _, row in bs_df.iterrows():
            as_of = row['date']

            # 2) 当該日以下で最も近い株価を取得
            candidate = stock_df[stock_df['date'] <= as_of]
            if candidate.empty or candidate['close'].isna().all():
                results.append({'date': as_of, 'EV': None, 'reason': 'no_price'})
                continue
            price = candidate.sort_values('date', ascending=False).iloc[0]['close']

            # 3) 発行株式数（フォールバック順）
            shares = self._first_nonnull(row, ['share_issued', 'ordinary_shares_number', 'treasury_shares_number'])
            if shares is None:
                results.append({'date': as_of, 'EV': None, 'reason': 'no_shares'})
                continue

            # ※単位チェック: shares の単位（実株数／千株など）を事前に確認してください
            market_cap = price * float(shares)

            # 4) 有利子負債（フォールバック）
            total_debt = self._first_nonnull(row, ['total_debt'])
            if total_debt is None:
                lt = self._first_nonnull(row, ['long_term_debt_and_capital_lease_obligation']) or 0
                ct = self._first_nonnull(row, ['current_debt_and_capital_lease_obligation']) or 0
                total_debt = lt + ct

            # 5) 現金（フォールバック）
            cash = self._first_nonnull(row, ['cash_and_cash_equivalents',
                                    'cash_cash_equivalents_and_short_term_investments',
                                    'restricted_cash']) or 0

            # 6) EV 計算
            try:
                ev = float(market_cap) + float(total_debt or 0) - float(cash or 0)
            except Exception:
                ev = None

            results.append({'date': as_of, 'price': price, 'shares': shares, 'market_cap': market_cap, 'total_debt': total_debt, 'cash': cash, 'EV': ev})

        ev_df = pd.DataFrame(results).set_index('date')
        return ev_df
    
    def calculate_ebitda(
        self,
        financials_df: pd.DataFrame, 
        cash_flow_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        EBITDA を計算するための関数。
        Args:
        - financials_df: 財務諸表データの DataFrame。少なくとも 'operating_income' 列を含むことが望ましい。
        - cash_flow_df: キャッシュフローデータの DataFrame。少なくとも 'depreciation' 列を含むことが望ましい。
        Returns:
        - EBITDA を含む DataFrame。元のインデックス（日付）を維持しつつ、'EBITDA' 列を追加して返す。
        Notes:
        - 可能な限りベクトル化して計算するため、ループは使用しない。
        - 'EBITDA' 列が既に存在する場合は、それを優先して使用する。
        - 'operating_income' や 'depreciation' が欠損している場合は、可能な限り他の情報を利用して補完するロジックを追加することが望ましい。
        """
        # コピー・正規化
        fin = financials_df.copy()
        cf = cash_flow_df.copy()
        fin.columns = [str(c).lower().strip() for c in fin.columns]
        cf.columns = [str(c).lower().strip() for c in cf.columns]

        # date を datetime にしてインデックス化（共通の基準に揃える）
        if 'date' in fin.columns:
            fin['date'] = pd.to_datetime(fin['date'], errors='coerce')
        else:
            fin['date'] = pd.to_datetime(fin.index, errors='coerce')
        fin = fin.set_index('date').sort_index()

        if 'date' in cf.columns:
            cf['date'] = pd.to_datetime(cf['date'], errors='coerce')
        else:
            cf['date'] = pd.to_datetime(cf.index, errors='coerce')
        cf = cf.set_index('date').sort_index()

        # 必要列を抽出して年次等で再索引（fin を基準に揃える）
        left = fin[['operating_income']].copy() if 'operating_income' in fin.columns else pd.DataFrame(index=fin.index)
        left['ebitda_explicit'] = fin.get('ebitda')  # API に ebitda がある場合の優先列

        right = cf[['depreciation']].copy() if 'depreciation' in cf.columns else pd.DataFrame(index=cf.index)
        right = right.reindex(left.index)  # fin の日付を基準に補完（NaN になる箇所あり）

        # 結合
        merged = left.join(right)

        # ベクトル化ロジック：
        # 1) 既定の ebitda があるならそれを使う
        # 2) 無ければ operating_income + depreciation（存在する方のみ使う）
        merged['operating_income'] = pd.to_numeric(merged['operating_income'], errors='coerce')
        merged['depreciation'] = pd.to_numeric(merged['depreciation'], errors='coerce')
        merged['EBITDA'] = pd.to_numeric(merged['ebitda_explicit'], errors='coerce')

        mask_missing = merged['EBITDA'].isna()
        merged.loc[mask_missing, 'EBITDA'] = (
            merged.loc[mask_missing, 'operating_income'].fillna(0) +
            merged.loc[mask_missing, 'depreciation'].fillna(0)
        )

        # 注意：operating_income が NaN で depreciation のみある場合は depreciation が利用される（上の式で OK）
        # 必要に応じて revenue×margin 等の代替ロジックを追加

        # 出力整形：date を列として残す or インデックスを date のまま返す
        merged = merged[['operating_income', 'depreciation', 'EBITDA']]
        return merged
    
    def calc_ev_par_ebitda(
        self,
        ebitda_df: pd.DataFrame,
        ev_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        EV/EBITDA を計算する関数。
        Args:
        - ebitda_df: EBITDA の値またはシリーズ
        - ev_df: EV の値またはシリーズ
        Returns:
        - EV/EBITDA の値またはシリーズ
        Notes:
        - ゼロ割や欠損値には None を返す
        """
        # date
        ebitda_df.reset_index(inplace = True)
        ev_df.reset_index(inplace = True)
        # インデックスを揃えるために 'date' 列を datetime 型に変換
        ebitda_df['date'] = pd.to_datetime(ebitda_df['date'], errors='coerce')
        ev_df['date'] = pd.to_datetime(ev_df['date'], errors='coerce')
        # データフレームを結合
        result_df = pd.merge(ebitda_df, ev_df, on='date', how='left')
        # EV/EBITDA を計算（ゼロ割や欠損値には None を返す）
        result_df['EV_par_EBITDA'] = result_df.apply(lambda row: row['EV'] / row['EBITDA'] if row['EBITDA'] not in [0, None, np.nan] else None, axis=1)
        return result_df
    
    def calc_financial(
        self,
        code: str,
        market: str | None
    ):
        """
        ◆ 2. 財務データ（Financials）
        • 売上高（Revenue）
        • 営業利益（Operating Income）
        • 純利益（Net Income）
        • EBITDA（企業による）
        • 総資産（Total Assets）
        • 総負債（Total Liabilities）
        • 現金（Cash）
        • 営業キャッシュフロー（Operating Cash Flow）
        • フリーキャッシュフロー（Free Cash Flow）
        を計算して返す関数
        Args:
            code (str): 銘柄コード
            market (str | None): 市場コード
        Returns:
            pd.DataFrame: 財務データを含むDataFrame
        """
        # APIからデータを取得する
        # ４年分の財務データ
        financials_data = self.request_api.get_corp_financials_data(code=code, market=market)
        financials_data_df = pd.DataFrame(financials_data['results'])
        # ４年分のバランスシート
        balance_sheet_data = self.request_api.get_corp_balance_sheet_data(code=code, market=market)
        balance_sheet_data_df = pd.DataFrame(balance_sheet_data['results'])
        # ４年分のキャッシュフロー
        cash_flow_data = self.request_api.get_corp_cash_flow_data(code=code, market=market)
        cash_flow_data_df = pd.DataFrame(cash_flow_data['results'])
        # ４年分の収益データ
        earnings_data = self.request_api.get_corp_earnings_data(code=code, market=market)
        earnings_data_df = pd.DataFrame(earnings_data['results'])
        # ４年分の四半期収益データ
        quarterly_earnings_data = self.request_api.get_corp_quarterly_earnings_data(code=code, market=market)
        quarterly_earnings_data_df = pd.DataFrame(quarterly_earnings_data['results'])
        # ４年分の株価データ        
        stock_df = self.request_api.get_stock_time_series_data(
            code="HYMC",
            market=None,
            start="2000-01-01",
            end=dt.datetime.today().strftime("%Y-%m-%d")
        )
        # EV（Enterprise Value）の計算
        ev_df = self.calc_ev(
            stock_df=stock_df, 
            bs_df=balance_sheet_data_df
        )
        ev_df = ev_df.reset_index()
        ev_df['date'] = pd.to_datetime(ev_df['date'], errors='coerce')
        # EBITDAの計算
        ebitda_df = self.calculate_ebitda(
            financials_df=financials_data_df,
            cash_flow_df=cash_flow_data_df
        )
        ebitda_df = ebitda_df.reset_index()
        ebitda_df['date'] = pd.to_datetime(ebitda_df['date'], errors='coerce')
        # earnings_data_dfからdate, revenue, earningsを抽出
        tmp_earnings_df = earnings_data_df[['date', 'revenue', 'earnings']].copy()
        tmp_earnings_df['date'] = pd.to_datetime(tmp_earnings_df['date'], errors='coerce')
        # ebitda_dfからdate, ebitdaを抽出
        tmp_ebitda_df = ebitda_df[['date', 'EBITDA']].copy()
        tmp_ebitda_df['date'] = pd.to_datetime(tmp_ebitda_df['date'], errors='coerce')
        # financials_data_dfからdate, operating_income, basic_eps, diluted_epsを抽出
        tmp_financials_df = financials_data_df[['date', 'operating_income', 'basic_eps', 'diluted_eps']].copy()
        tmp_financials_df['date'] = pd.to_datetime(tmp_financials_df['date'], errors='coerce')
        # balance_sheet_data_dfからdate, total_assets, total_debt, cash_and_cash_equivalentsを抽出
        tmp_balance_sheet_df = balance_sheet_data_df[['date', 'total_assets', 'total_debt', 'cash_and_cash_equivalents']].copy()
        tmp_balance_sheet_df['date'] = pd.to_datetime(tmp_balance_sheet_df['date'], errors='coerce')
        # cash_flow_data_dfからdate, operating_cash_flow, free_cash_flowを抽出
        tmp_cash_flow_df = cash_flow_data_df[['date', 'operating_cash_flow', 'free_cash_flow']].copy()
        tmp_cash_flow_df['date'] = pd.to_datetime(tmp_cash_flow_df['date'], errors='coerce')
        # データフレームを結合
        merged_df = tmp_earnings_df.merge(tmp_balance_sheet_df, on='date', how='outer')
        merged_df = merged_df.merge(tmp_ebitda_df, on='date', how='outer')
        merged_df = merged_df.merge(tmp_financials_df, on='date', how='outer')
        merged_df = merged_df.merge(tmp_cash_flow_df, on='date', how='outer')
        return merged_df
    
    
    def _calc_pbr(
        self, 
        stock_df: pd.DataFrame,
        bs_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        BPS（Book Value Per Share）を計算(純資産/発行済株式数)
        Args:
            stock_df (pd.DataFrame): 株価の時系列データを含むDataFrame
            bs_df (pd.DataFrame): バランスシートのデータを含むDataFrame
        Returns:
            pd.DataFrame: BPSを含むDataFrame
        """
        results = []
        for _, row in bs_df.iterrows():
            as_of = row['date']
            # 1) 当該日以下で最も近い株価を取得
            candidate = stock_df[stock_df['date'] <= as_of]
            if candidate.empty or candidate['close'].isna().all():
                results.append({'date': as_of, 'EV': None, 'reason': 'no_price'})
                continue
            # 2) BPS（Book Value Per Share）を計算(純資産/発行済株式数)
            stockholders_equity = row.get('stockholders_equity')
            share_issued = row.get('share_issued')
            bps = bps = stockholders_equity / share_issued
            price = candidate.sort_values('date', ascending=False).iloc[0]['close']
            # 3) PBR（Price-to-Book Ratio）を計算(株価/BPS)
            pbr = price / bps
            results.append({'date': as_of, 'BPS': bps, 'PBR': pbr})
        pbr_df = pd.DataFrame(results).set_index('date')
        return pbr_df
    
    def calc_roe(
        self,
        financials_df: pd.DataFrame,
        bs_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        ROE（Return on Equity）を計算(純利益/自己資本)
        当期純利益（Net Income）をfinancials_dfから
        自己資本（stockholders_equity）bs_dfから
        Args:
            financials_df (pd.DataFrame): 財務諸表データの DataFrame
            bs_df (pd.DataFrame): バランスシートのデータを含むDataFrame
        Returns:
            pd.DataFrame: ROEを含むDataFrame
        """
        tmp_financials_df = financials_df[['date', 'net_income']].copy()
        tmp_financials_df['date'] = pd.to_datetime(tmp_financials_df['date'], errors='coerce')
        tmp_bs_df = bs_df[['date', 'stockholders_equity']].copy()
        tmp_bs_df['date'] = pd.to_datetime(tmp_bs_df['date'], errors='coerce')
        merged_df = tmp_financials_df.merge(tmp_bs_df, on='date', how='outer')
        # ROE（Return on Equity）を計算(純利益/自己資本)
        # 当期純利益（Net Income）をfinancials_data_dfから
        # 自己資本（stockholders_equity）balance_sheet_data_dfから
        merged_df['ROE'] = merged_df.apply(lambda row: row['net_income'] / row['stockholders_equity'] if row['stockholders_equity'] not in [0, None, np.nan] else None, axis=1)
        return merged_df[['date', 'ROE']]
    
    
    def calc_stock_investment_indicators(
        self,
        code: str,
        market: str | None
    ) -> pd.DataFrame:
        """
        株式投資指標を計算して返す関数
        Args:            code (str): 銘柄コード
            market (str | None): 市場コード
        Returns:
            pd.DataFrame: 株式投資指標を含むDataFrame
        """
        # 株価データの取得
        end = dt.datetime.today().strftime("%Y-%m-%d")
        start = (dt.datetime.today() - dt.timedelta(days=365)).strftime("%Y-%m-%d")
        stock_df = self.request_api.get_stock_time_series_data(
            code=code,
            market=market,
            start=start,
            end=end
        )
        # APIからデータを取得する
        # ４年分の財務データ
        financials_data = self.request_api.get_corp_financials_data(
            code=code,
            market=market
        )
        financials_data_df = pd.DataFrame(financials_data['results'])
        # ４年分のバランスシート
        balance_sheet_data = self.request_api.get_corp_balance_sheet_data(
            code=code,
            market=market
        )
        balance_sheet_data_df = pd.DataFrame(balance_sheet_data['results'])
        # BPS（Book Value Per Share）を計算(純資産/発行済株式数)
        pbr_df = self._calc_pbr(
            stock_df=stock_df,
            bs_df=balance_sheet_data_df
        )
        pbr_df = pbr_df.reset_index()  
        pbr_df['date'] = pd.to_datetime(pbr_df['date'], errors='coerce')
        # ROE（Return on Equity）を計算(純利益/自己資本)
        # 当期純利益（Net Income）をfinancials_data_dfから
        # 自己資本（stockholders_equity）balance_sheet_data_dfから
        roe_df = self.calc_roe(
            financials_df=financials_data_df,
            bs_df=balance_sheet_data_df
        )
        roe_df['date'] = pd.to_datetime(roe_df['date'], errors='coerce')
        # financials_data_dfからdate, operating_income, basic_eps, diluted_epsを抽出
        tmp_financials_df = financials_data_df[['date', 'operating_income', 'basic_eps', 'diluted_eps']].copy()
        tmp_financials_df['date'] = pd.to_datetime(tmp_financials_df['date'], errors='coerce')
        # データフレームを結合
        merged_df = pbr_df.merge(roe_df, on='date', how='outer')
        merged_df = merged_df.merge(tmp_financials_df, on='date', how='outer')
        return merged_df

