
import numpy as np

class MiningEvaluationParameter:
    """
    鉱山評価のためのパラメーター計算クラス
    NI 43-101から以下のパラメータを特定すること
    • metal_price — 金属スポット価格（ドル/オンス）
    • aisc — AISC（操業コスト、ドル/オンス）
    • annual_production — 年間生産量（オンス/年）
    • mine_life_years — 残存マインライフ（年）
    • discount_rate — 割引率（年率）
    • shares_outstanding — 発行済株式数（株）
    • nav_price_per_share — NAV理論株価（ドル/株）
    • discount_factor — 目標株価下限の安全マージン係数
    • premium_factor — 目標株価上限のプレミアム係数
    • base_aisc — 基準となるAISC（ドル/オンス）
    • improvement_ratio — コスト改善率（AISC低下率）
    • cost_increase_ratio — コスト上昇率（AISC上昇率）
    • streaming_royalty_oz — ストリーミング/ロイヤリティ対象オンス
    • total_ounces — 総資源量（オンス）
    • measured_oz — 計測資源量（オンス）
    • indicated_oz — 示測資源量（オンス）
    • inferred_oz — 予測資源量（オンス）
    • include_inferred — 予測資源量を総資源量に含めるか
    • current_nav_ev — 現在のNAV企業価値（ドル）
    • growth_rate — NAV成長率（年率）
    • years — 成長を適用する期間（年）
    • metal_price_mean — Monte Carlo用の金属価格平均（ドル/オンス）
    • metal_price_vol — Monte Carlo用の金属価格ボラティリティ（標準偏差）
    • n_sims — Monte Carloシミュレーション回数
    """
    def __init__(self):
        pass


    # =========================
    # 1. NAV理論株価(ドル/株)
    # =========================
    def calc_nav_price_per_share(
        self,
        metal_price: float,      # 金属スポット価格(ドル/オンス)
        aisc: float,             # AISC(ドル/オンス)
        annual_production: float,# 年間生産量(オンス/年)
        mine_life_years: int,    # 残存マインライフ(年)
        discount_rate: float,    # 割引率(年率, 0.08 など)
        shares_outstanding: float# 発行済株式数(株)
    ) -> float:
        """
        NAV理論株価(ドル/株)を計算
        Args:
            metal_price (float): 金属スポット価格(ドル/オンス)
            aisc (float): AISC(ドル/オンス)
            annual_production (float): 年間生産量(オンス/年)
            mine_life_years (int): 残存マインライフ(年)
            discount_rate (float): 割引率(年率, 0.08 など)
            shares_outstanding (float): 発行済株式数(株)
        Returns:
            float: NAV理論株価(ドル/株)
        """
        cash_flows = []
        margin_per_oz = metal_price - aisc
        annual_cf = margin_per_oz * annual_production
        for t in range(1, mine_life_years + 1):
            cash_flows.append(annual_cf / ((1 + discount_rate) ** t))
        nav_enterprise_value = sum(cash_flows)
        return nav_enterprise_value / shares_outstanding


    # =========================
    # 2. 目標株価下限(ドル)
    # =========================
    def calc_target_price_lower(
        self,
        nav_price_per_share: float, # NAV理論株価(ドル/株)
        discount_factor: float      # 安全マージン係数(例: 0.7 なら 70%)
    ) -> float:
        """
        目標株価下限(ドル)を計算
        Args:
            nav_price_per_share (float): NAV理論株価(ドル/株)
            discount_factor (float): 安全マージン係数(例: 0.7 なら 70%)
        Returns:
            float: 目標株価下限(ドル)
        """
        return nav_price_per_share * discount_factor


    # =========================
    # 3. 目標株価上限(ドル)
    # =========================
    def calc_target_price_upper(
        self,
        nav_price_per_share: float, # NAV理論株価(ドル/株)
        premium_factor: float       # プレミアム係数(例: 1.3 なら 130%)
    ) -> float:
        """
        目標株価上限(ドル)を計算
        Args:
            nav_price_per_share (float): NAV理論株価(ドル/株)
            premium_factor (float): プレミアム係数(例: 1.3 なら 130%)
        Returns:
            float: 目標株価上限(ドル)
        """
        return nav_price_per_share * premium_factor


    # =========================
    # 4. AISC下限(ドル/オンス)
    # =========================
    def calc_aisc_lower(
        self,
        base_aisc: float,       # ベースAISC(ドル/オンス)
        improvement_ratio: float# コスト改善率(例: 0.1 なら 10%低下)
    ) -> float:
        """
        AISC下限(ドル/オンス)を計算
        Args:
            base_aisc (float): ベースAISC(ドル/オンス)
            improvement_ratio (float): コスト改善率(例: 0.1 なら 10%低下)
        Returns:
            float: AISC下限(ドル/オンス)
        """
        return base_aisc * (1 - improvement_ratio)


    # =========================
    # 5. AISC上限(ドル/オンス)
    # =========================
    def calc_aisc_upper(
        self,
        base_aisc: float,       # ベースAISC(ドル/オンス)
        cost_increase_ratio: float # コスト上昇率(例: 0.15 なら 15%上昇)
    ) -> float:
        """
        AISC上限(ドル/オンス)を計算
        Args:
            base_aisc (float): ベースAISC(ドル/オンス)
            cost_increase_ratio (float): コスト上昇率(例: 0.15 なら 15%上昇)
        Returns:
            float: AISC上限(ドル/オンス)
        """
        return base_aisc * (1 + cost_increase_ratio)


    # =========================
    # 6. NAV企業価値(ドル)
    # =========================
    def calc_nav_enterprise_value(
        self,
        metal_price: float,      # 金属スポット価格(ドル/オンス)
        aisc: float,             # AISC(ドル/オンス)
        annual_production: float,# 年間生産量(オンス/年)
        mine_life_years: int,    # 残存マインライフ(年)
        discount_rate: float     # 割引率(年率)
    ) -> float:
        """
        NAV企業価値(ドル)を計算
        Args:
            metal_price (float): 金属スポット価格(ドル/オンス)
            aisc (float): AISC(ドル/オンス)
            annual_production (float): 年間生産量(オンス/年)
            mine_life_years (int): 残存マインライフ(年)
            discount_rate (float): 割引率(年率)
        Returns:
            float: NAV企業価値(ドル)
        """
        cash_flows = []
        margin_per_oz = metal_price - aisc
        annual_cf = margin_per_oz * annual_production
        for t in range(1, mine_life_years + 1):
            cash_flows.append(annual_cf / ((1 + discount_rate) ** t))
        return sum(cash_flows)


    # ==================================
    # 7. ストリーミング・ロイヤリティ控除率(%)
    # ==================================
    def calc_streaming_royalty_deduction_rate(
        self,
        streaming_royalty_oz: float, # ストリーミング/ロイヤリティ対象オンス
        total_ounces: float          # 総資源量(オンス)
    ) -> float:
        """
        ストリーミング・ロイヤリティ控除率(%)を計算
        Args:
            streaming_royalty_oz (float): ストリーミング/ロイヤリティ対象オンス
            total_ounces (float): 総資源量(オンス)
        Returns:
            float: ストリーミング・ロイヤリティ控除率(%)
        """
        if total_ounces == 0:
            return 0.0
        return (streaming_royalty_oz / total_ounces) * 100.0


    # =========================
    # 8. 総資源量(オンス)
    # =========================
    def calc_total_resources_ounces(
        self,
        measured_oz: float,   # 計測資源量(オンス)
        indicated_oz: float,  # 示測資源量(オンス)
        inferred_oz: float,   # 予測資源量(オンス)
        include_inferred: bool# 予測資源量を含めるか
    ) -> float:
        """
        総資源量(オンス)を計算
        Args:
            measured_oz (float): 計測資源量(オンス)
            indicated_oz (float): 示測資源量(オンス)
            inferred_oz (float): 予測資源量(オンス)
            include_inferred (bool): 予測資源量を含めるか
        Returns:
            float: 総資源量(オンス)
        """
        total = measured_oz + indicated_oz
        if include_inferred:
            total += inferred_oz
        return total


    # =========================
    # 9. 5年後NAV企業価値(ドル)
    # =========================
    def calc_nav_enterprise_value_5y(
        self,
        current_nav_ev: float, # 現在のNAV企業価値(ドル)
        growth_rate: float,    # NAV成長率(年率, 0.05 など)
        years: int = 5         # 期間(年)
    ) -> float:
        """
        5年後NAV企業価値(ドル)を計算
        Args:
            current_nav_ev (float): 現在のNAV企業価値(ドル)
            growth_rate (float): NAV成長率(年率, 0.05 など)
            years (int): 期間(年)
        Returns:
            float: 5年後NAV企業価値(ドル)
        """
        return current_nav_ev * ((1 + growth_rate) ** years)


    # =========================
    # 10. 5年後NAV(ドル/株)
    # =========================
    def calc_nav_per_share_5y(
        self,
        nav_ev_5y: float,        # 5年後NAV企業価値(ドル)
        shares_outstanding: float# 発行済株式数(株)
    ) -> float:
        """
        5年後NAV(ドル/株)を計算
        Args:
            nav_ev_5y (float): 5年後NAV企業価値(ドル)
            shares_outstanding (float): 発行済株式数(株)
        Returns:
            float: 5年後NAV(ドル/株)
        """
        return nav_ev_5y / shares_outstanding


    # =========================
    # 11. MC期待値NAV(ドル/株)
    # =========================
    def calc_mc_expected_nav_per_share(
        self,
        metal_price_mean: float,     # 金属価格平均(ドル/オンス)
        metal_price_vol: float,      # 金属価格ボラティリティ(標準偏差, ドル/オンス)
        aisc: float,                 # AISC(ドル/オンス)
        annual_production: float,    # 年間生産量(オンス/年)
        mine_life_years: int,        # 残存マインライフ(年)
        discount_rate: float,        # 割引率(年率)
        shares_outstanding: float,   # 発行済株式数(株)
        n_sims: int = 10000          # シミュレーション回数
    ) -> float:
        """
        Monte Carlo による期待値NAV(ドル/株)を計算
        Args:
            metal_price_mean (float): 金属価格平均(ドル/オンス)
            metal_price_vol (float): 金属価格ボラティリティ(標準偏差, ドル/オンス)
            aisc (float): AISC(ドル/オンス)
            annual_production (float): 年間生産量(オンス/年)
            mine_life_years (int): 残存マインライフ(年)
            discount_rate (float): 割引率(年率)
            shares_outstanding (float): 発行済株式数(株)
            n_sims (int): シミュレーション回数
        Returns:
            float: 期待値NAV(ドル/株)
        """
        navs = []
        for _ in range(n_sims):
            # 単純に「一定価格シナリオ」をランダム生成
            price = np.random.normal(metal_price_mean, metal_price_vol)
            price = max(price, 0.0)  # 負価格はクリップ
            margin_per_oz = price - aisc
            annual_cf = max(margin_per_oz, 0.0) * annual_production
            cash_flows = [
                annual_cf / ((1 + discount_rate) ** t)
                for t in range(1, mine_life_years + 1)
            ]
            nav_ev = sum(cash_flows)
            navs.append(nav_ev / shares_outstanding)
        return float(np.mean(navs))


    # =========================
    # 12. MC中央値NAV(ドル/株)
    # =========================
    def calc_mc_median_nav_per_share(
        self,
        metal_price_mean: float,     
        metal_price_vol: float,      
        aisc: float,                 
        annual_production: float,    
        mine_life_years: int,        
        discount_rate: float,        
        shares_outstanding: float,   
        n_sims: int = 10000          
    ) -> float:
        """
        Monte Carlo による中央値NAV(ドル/株)を計算
        Args:
            metal_price_mean (float): 金属価格平均(ドル/オンス)
            metal_price_vol (float): 金属価格ボラティリティ(標準偏差, ドル/オンス)
            aisc (float): AISC(ドル/オンス)
            annual_production (float): 年間生産量(オンス/年)
            mine_life_years (int): 残存マインライフ(年)
            discount_rate (float): 割引率(年率)
            shares_outstanding (float): 発行済株式数(株)
            n_sims (int): シミュレーション回数
        Returns:
            float: 中央値NAV(ドル/株)
        """
        navs = []
        for _ in range(n_sims):
            price = np.random.normal(metal_price_mean, metal_price_vol)
            price = max(price, 0.0)
            margin_per_oz = price - aisc
            annual_cf = max(margin_per_oz, 0.0) * annual_production
            cash_flows = [
                annual_cf / ((1 + discount_rate) ** t)
                for t in range(1, mine_life_years + 1)
            ]
            nav_ev = sum(cash_flows)
            navs.append(nav_ev / shares_outstanding)
        return float(np.median(navs))


    # =========================
    # 13. MC下方5%(ドル/株)
    # =========================
    def calc_mc_nav_per_share_p5(
        self,
        metal_price_mean: float,     
        metal_price_vol: float,      
        aisc: float,                 
        annual_production: float,    
        mine_life_years: int,        
        discount_rate: float,        
        shares_outstanding: float,   
        n_sims: int = 10000          
    ) -> float:
        """
        Monte Carlo による下方5%NAV(ドル/株)を計算
        Args:
            metal_price_mean (float): 金属価格平均(ドル/オンス)
            metal_price_vol (float): 金属価格ボラティリティ(標準偏差, ドル/オンス)
            aisc (float): AISC(ドル/オンス)
            annual_production (float): 年間生産量(オンス/年)
            mine_life_years (int): 残存マインライフ(年)
            discount_rate (float): 割引率(年率)
            shares_outstanding (float): 発行済株式数(株)
            n_sims (int): シミュレーション回数
        Returns:
            float: 下方5%NAV(ドル/株)
        """
        navs = []
        for _ in range(n_sims):
            price = np.random.normal(metal_price_mean, metal_price_vol)
            price = max(price, 0.0)
            margin_per_oz = price - aisc
            annual_cf = max(margin_per_oz, 0.0) * annual_production
            cash_flows = [
                annual_cf / ((1 + discount_rate) ** t)
                for t in range(1, mine_life_years + 1)
            ]
            nav_ev = sum(cash_flows)
            navs.append(nav_ev / shares_outstanding)
        return float(np.percentile(navs, 5))


    # =========================
    # 14. MC上方95%(ドル/株)
    # =========================
    def calc_mc_nav_per_share_p95(
        self,
        metal_price_mean: float,     
        metal_price_vol: float,      
        aisc: float,                 
        annual_production: float,    
        mine_life_years: int,        
        discount_rate: float,        
        shares_outstanding: float,   
        n_sims: int = 10000          
    ) -> float:
        """
        Monte Carlo による上方95%NAV(ドル/株)を計算
        Args:
            metal_price_mean (float): 金属価格平均(ドル/オンス)
            metal_price_vol (float): 金属価格ボラティリティ(標準偏差, ドル/オンス)
            aisc (float): AISC(ドル/オンス)
            annual_production (float): 年間生産量(オンス/年)
            mine_life_years (int): 残存マインライフ(年)
            discount_rate (float): 割引率(年率)
            shares_outstanding (float): 発行済株式数(株)
            n_sims (int): シミュレーション回数
        Returns:
            float: 上方95%NAV(ドル/株)
        """
        navs = []
        for _ in range(n_sims):
            price = np.random.normal(metal_price_mean, metal_price_vol)
            price = max(price, 0.0)
            margin_per_oz = price - aisc
            annual_cf = max(margin_per_oz, 0.0) * annual_production
            cash_flows = [
                annual_cf / ((1 + discount_rate) ** t)
                for t in range(1, mine_life_years + 1)
            ]
            nav_ev = sum(cash_flows)
            navs.append(nav_ev / shares_outstanding)
        return float(np.percentile(navs, 95))
