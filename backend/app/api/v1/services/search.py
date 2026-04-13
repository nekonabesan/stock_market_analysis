import yfinance as yf

from app.core.logger import logger

# Yahoo Financeの市場識別コード -> ティッカーサフィックス
YF_MARKET_SUFFIX_MAP: dict[str, str] = {
    # 日本
    "TSE": ".T",
    "JPX": ".T",
    # アジア・オセアニア
    "HKEX": ".HK",
    "SSE": ".SS",
    "SZSE": ".SZ",
    "ASX": ".AX",
    # 北米
    "TSX": ".TO",
    # 米国市場はサフィックス無し
    "NYSE": "",
    "NASDAQ": "",
    "AMEX": "",
    # 欧州
    "LSE": ".L",       # ロンドン証券取引所 (London Stock Exchange)
    "CSE": ".CO",      # コペンハーゲン証券取引所 (Nasdaq Copenhagen)
    "FRA": ".DE",      # フランクフルト証券取引所 / Xetra
    "EPA": ".PA",      # ユーロネクスト・パリ (Euronext Paris)
    "AMS": ".AS",      # ユーロネクスト・アムステルダム (Euronext Amsterdam)
    "EBR": ".BR",      # ユーロネクスト・ブリュッセル (Euronext Brussels)
    "STO": ".ST",      # ナスダック・ストックホルム (Nasdaq Stockholm)
    "HEL": ".HE",      # ナスダック・ヘルシンキ (Nasdaq Helsinki)
    "OB": ".OL",       # オスロ証券取引所 (Oslo Børs)
    "SWX": ".SW",      # スイス証券取引所 (SIX Swiss Exchange)
    "MCE": ".MC",      # マドリード証券取引所 (Bolsa de Madrid)
    "BIT": ".MI",      # ボルサ・イタリアーナ (Borsa Italiana / Euronext Milan)
    "VIE": ".VI",      # ウィーン証券取引所 (Wiener Börse)
}


class SearchService:
    def search(self, market: str, name: str | None = None, code: str | None = None) -> dict | None:
        if code:
            symbol = self._build_yfinance_ticker(code=code, market=market)
            return self._resolve_symbol(symbol=symbol, market=market, fallback_name=name)

        if not name:
            raise ValueError("Either name or code is required")

        return self._search_by_name(market=market, name=name)

    def _search_by_name(self, market: str, name: str) -> dict | None:
        search = yf.Search(query=name, max_results=10)
        quotes = getattr(search, "quotes", []) or []

        for quote in quotes:
            symbol = quote.get("symbol")
            if not symbol:
                continue
            if not self._match_market(symbol=symbol, market=market):
                continue

            resolved = self._resolve_symbol(
                symbol=symbol,
                market=market,
                fallback_name=quote.get("shortname") or quote.get("longname") or name,
            )
            if resolved is not None:
                return resolved

        return None

    def _resolve_symbol(self, symbol: str, market: str, fallback_name: str | None = None) -> dict | None:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="5d", interval="1d")
        if history is None or history.empty:
            return None

        info = getattr(ticker, "info", {}) or {}
        return {
            "found": True,
            "market": market,
            "name": info.get("shortName") or info.get("longName") or fallback_name,
            "code": symbol,
        }

    def _build_yfinance_ticker(self, code: str, market: str | None) -> str:
        normalized_code = code.strip()
        if not normalized_code:
            raise ValueError("code is required")

        # 既にサフィックス付きならそのまま使う。
        if "." in normalized_code:
            return normalized_code

        if market is None:
            return normalized_code

        normalized_market = market.strip().upper()
        if not normalized_market:
            return normalized_code

        # ".T" のようなサフィックス直接指定も許可する。
        if normalized_market.startswith("."):
            suffix = normalized_market
        else:
            suffix = YF_MARKET_SUFFIX_MAP.get(normalized_market, f".{normalized_market}")

        if suffix and normalized_code.upper().endswith(suffix):
            return normalized_code

        return f"{normalized_code}{suffix}"

    def _match_market(self, symbol: str, market: str) -> bool:
        normalized_market = market.strip().upper()
        suffix = YF_MARKET_SUFFIX_MAP.get(normalized_market)

        # 未定義市場はフィルタを弱めて候補を許容する。
        if suffix is None:
            return True

        # 米国市場はサフィックス無しを許容する。
        if suffix == "":
            return "." not in symbol

        return symbol.upper().endswith(suffix.upper())
