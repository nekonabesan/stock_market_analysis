from types import SimpleNamespace

from app.api.v1.services.search import SearchService


class _DummyHistory:
    def __init__(self, empty: bool):
        self.empty = empty


class _DummyTicker:
    def __init__(self, symbol: str, has_data: bool = True):
        self.symbol = symbol
        self.info = {"shortName": f"NAME-{symbol}"}
        self._has_data = has_data

    def history(self, period: str, interval: str):
        return _DummyHistory(empty=not self._has_data)


def test_build_yfinance_ticker_with_market_suffix() -> None:
    service = SearchService()

    result = service._build_yfinance_ticker(code="7203", market="TSE")

    assert result == "7203.T"


def test_build_yfinance_ticker_keeps_suffix_when_already_exists() -> None:
    service = SearchService()

    result = service._build_yfinance_ticker(code="AAPL", market="NASDAQ")

    assert result == "AAPL"


def test_search_by_code_returns_result_when_history_exists(monkeypatch) -> None:
    service = SearchService()

    monkeypatch.setattr("app.api.v1.services.search.yf.Ticker", lambda symbol: _DummyTicker(symbol, has_data=True))

    result = service.search(market="TSE", code="7203")

    assert result is not None
    assert result["found"] is True
    assert result["code"] == "7203.T"


def test_search_by_code_returns_none_when_history_empty(monkeypatch) -> None:
    service = SearchService()

    monkeypatch.setattr("app.api.v1.services.search.yf.Ticker", lambda symbol: _DummyTicker(symbol, has_data=False))

    result = service.search(market="TSE", code="7203")

    assert result is None


def test_search_by_name_returns_first_market_match(monkeypatch) -> None:
    service = SearchService()

    dummy_search_result = SimpleNamespace(
        quotes=[
            {"symbol": "AAPL", "shortname": "Apple"},
            {"symbol": "7203.T", "shortname": "Toyota"},
        ]
    )

    monkeypatch.setattr("app.api.v1.services.search.yf.Search", lambda query, max_results=10: dummy_search_result)
    monkeypatch.setattr("app.api.v1.services.search.yf.Ticker", lambda symbol: _DummyTicker(symbol, has_data=True))

    result = service.search(market="TSE", name="トヨタ自動車")

    assert result is not None
    assert result["code"] == "7203.T"
    assert result["name"] == "NAME-7203.T"
