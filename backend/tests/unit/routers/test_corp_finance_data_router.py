from datetime import date

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app

# ---------------------------------------------------------------------------
# DB 依存性オーバーライド
# ---------------------------------------------------------------------------

def _override_db():
    yield object()


# ---------------------------------------------------------------------------
# UPSERT 用モックサービス
# ---------------------------------------------------------------------------

class _UpsertSuccess:
    def __init__(self, db_session):
        pass

    def update_corp_finance_data(self, code, market):
        return True


class _UpsertNotFound:
    def __init__(self, db_session):
        pass

    def update_corp_finance_data(self, code, market):
        return False


class _UpsertValueError:
    def __init__(self, db_session):
        pass

    def update_corp_finance_data(self, code, market):
        raise ValueError("code is required")


class _UpsertUnexpectedError:
    def __init__(self, db_session):
        pass

    def update_corp_finance_data(self, code, market):
        raise RuntimeError("unexpected")


# ---------------------------------------------------------------------------
# GET 共通: サンプル dict
# ---------------------------------------------------------------------------

_SAMPLE_FINANCIALS = {"date": date(2024, 3, 31), "market": "T", "code": "7203"}
_SAMPLE_BALANCE_SHEET = {"date": date(2024, 3, 31), "market": "T", "code": "7203"}
_SAMPLE_CASHFLOW = {"date": date(2024, 3, 31), "market": "T", "code": "7203"}
_SAMPLE_EARNINGS = {"date": date(2024, 3, 31), "market": "T", "code": "7203"}
_SAMPLE_QUARTERLY = {"date": date(2024, 3, 31), "market": "T", "code": "7203"}


# ---------------------------------------------------------------------------
# GET /financials/ 用モックサービス
# ---------------------------------------------------------------------------

class _GetFinancialsSuccess:
    def __init__(self, db_session):
        pass

    def get_financial_statements(self, code, market, start, end):
        return [_SAMPLE_FINANCIALS]


class _GetFinancialsEmpty:
    def __init__(self, db_session):
        pass

    def get_financial_statements(self, code, market, start, end):
        return []


class _GetFinancialsValueError:
    def __init__(self, db_session):
        pass

    def get_financial_statements(self, code, market, start, end):
        raise ValueError("code is required")


class _GetFinancialsUnexpectedError:
    def __init__(self, db_session):
        pass

    def get_financial_statements(self, code, market, start, end):
        raise RuntimeError("unexpected")


# ---------------------------------------------------------------------------
# GET /balance_sheet/ 用モックサービス
# ---------------------------------------------------------------------------

class _GetBalanceSheetSuccess:
    def __init__(self, db_session):
        pass

    def get_balance_sheet(self, code, market, start, end):
        return [_SAMPLE_BALANCE_SHEET]


class _GetBalanceSheetEmpty:
    def __init__(self, db_session):
        pass

    def get_balance_sheet(self, code, market, start, end):
        return []


class _GetBalanceSheetValueError:
    def __init__(self, db_session):
        pass

    def get_balance_sheet(self, code, market, start, end):
        raise ValueError("code is required")


class _GetBalanceSheetUnexpectedError:
    def __init__(self, db_session):
        pass

    def get_balance_sheet(self, code, market, start, end):
        raise RuntimeError("unexpected")


# ---------------------------------------------------------------------------
# GET /cash_flow/ 用モックサービス
# ---------------------------------------------------------------------------

class _GetCashFlowSuccess:
    def __init__(self, db_session):
        pass

    def get_cashflow(self, code, market, start, end):
        return [_SAMPLE_CASHFLOW]


class _GetCashFlowEmpty:
    def __init__(self, db_session):
        pass

    def get_cashflow(self, code, market, start, end):
        return []


class _GetCashFlowValueError:
    def __init__(self, db_session):
        pass

    def get_cashflow(self, code, market, start, end):
        raise ValueError("code is required")


class _GetCashFlowUnexpectedError:
    def __init__(self, db_session):
        pass

    def get_cashflow(self, code, market, start, end):
        raise RuntimeError("unexpected")


# ---------------------------------------------------------------------------
# GET /earnings/ 用モックサービス
# ---------------------------------------------------------------------------

class _GetEarningsSuccess:
    def __init__(self, db_session):
        pass

    def get_earnings(self, code, market, start, end):
        return [_SAMPLE_EARNINGS]


class _GetEarningsEmpty:
    def __init__(self, db_session):
        pass

    def get_earnings(self, code, market, start, end):
        return []


class _GetEarningsValueError:
    def __init__(self, db_session):
        pass

    def get_earnings(self, code, market, start, end):
        raise ValueError("code is required")


class _GetEarningsUnexpectedError:
    def __init__(self, db_session):
        pass

    def get_earnings(self, code, market, start, end):
        raise RuntimeError("unexpected")


# ---------------------------------------------------------------------------
# GET /quarterly_earnings/ 用モックサービス
# ---------------------------------------------------------------------------

class _GetQuarterlyEarningsSuccess:
    def __init__(self, db_session):
        pass

    def get_quarterly_earnings(self, code, market, start, end):
        return [_SAMPLE_QUARTERLY]


class _GetQuarterlyEarningsEmpty:
    def __init__(self, db_session):
        pass

    def get_quarterly_earnings(self, code, market, start, end):
        return []


class _GetQuarterlyEarningsValueError:
    def __init__(self, db_session):
        pass

    def get_quarterly_earnings(self, code, market, start, end):
        raise ValueError("code is required")


class _GetQuarterlyEarningsUnexpectedError:
    def __init__(self, db_session):
        pass

    def get_quarterly_earnings(self, code, market, start, end):
        raise RuntimeError("unexpected")


# ---------------------------------------------------------------------------
# POST / (UPSERT) テスト
# ---------------------------------------------------------------------------

def test_upsert_corp_finance_data_returns_200_on_success(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _UpsertSuccess)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post("/api/v1/corp_finance_data/", json={"code": "7203", "market": "T"})

    assert response.status_code == 200
    assert response.json() == {"result": True}

    app.dependency_overrides.clear()


def test_upsert_corp_finance_data_returns_404_when_service_returns_false(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _UpsertNotFound)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post("/api/v1/corp_finance_data/", json={"code": "7203", "market": "T"})

    assert response.status_code == 404
    assert "could not be fetched" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_upsert_corp_finance_data_returns_400_on_value_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _UpsertValueError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post("/api/v1/corp_finance_data/", json={"code": "7203", "market": "T"})

    assert response.status_code == 400
    assert response.json()["detail"] == "code is required"

    app.dependency_overrides.clear()


def test_upsert_corp_finance_data_returns_500_on_unexpected_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _UpsertUnexpectedError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.post("/api/v1/corp_finance_data/", json={"code": "7203", "market": "T"})

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred"

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /financials/ テスト
# ---------------------------------------------------------------------------

def test_get_financials_returns_200_on_success(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetFinancialsSuccess)
    monkeypatch.setattr(router_module, "_orm_to_dict", lambda r: r)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/financials/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1

    app.dependency_overrides.clear()


def test_get_financials_returns_404_when_empty(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetFinancialsEmpty)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/financials/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_get_financials_returns_400_on_value_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetFinancialsValueError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/financials/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "code is required"

    app.dependency_overrides.clear()


def test_get_financials_returns_500_on_unexpected_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetFinancialsUnexpectedError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/financials/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred"

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /balance_sheet/ テスト
# ---------------------------------------------------------------------------

def test_get_balance_sheet_returns_200_on_success(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetBalanceSheetSuccess)
    monkeypatch.setattr(router_module, "_orm_to_dict", lambda r: r)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/balance_sheet/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1

    app.dependency_overrides.clear()


def test_get_balance_sheet_returns_404_when_empty(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetBalanceSheetEmpty)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/balance_sheet/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_get_balance_sheet_returns_400_on_value_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetBalanceSheetValueError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/balance_sheet/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "code is required"

    app.dependency_overrides.clear()


def test_get_balance_sheet_returns_500_on_unexpected_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetBalanceSheetUnexpectedError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/balance_sheet/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred"

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /cash_flow/ テスト
# ---------------------------------------------------------------------------

def test_get_cash_flow_returns_200_on_success(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetCashFlowSuccess)
    monkeypatch.setattr(router_module, "_orm_to_dict", lambda r: r)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/cash_flow/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1

    app.dependency_overrides.clear()


def test_get_cash_flow_returns_404_when_empty(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetCashFlowEmpty)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/cash_flow/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_get_cash_flow_returns_400_on_value_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetCashFlowValueError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/cash_flow/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "code is required"

    app.dependency_overrides.clear()


def test_get_cash_flow_returns_500_on_unexpected_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetCashFlowUnexpectedError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/cash_flow/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred"

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /earnings/ テスト
# ---------------------------------------------------------------------------

def test_get_earnings_returns_200_on_success(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetEarningsSuccess)
    monkeypatch.setattr(router_module, "_orm_to_dict", lambda r: r)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/earnings/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1

    app.dependency_overrides.clear()


def test_get_earnings_returns_404_when_empty(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetEarningsEmpty)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/earnings/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_get_earnings_returns_400_on_value_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetEarningsValueError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/earnings/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "code is required"

    app.dependency_overrides.clear()


def test_get_earnings_returns_500_on_unexpected_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetEarningsUnexpectedError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/earnings/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred"

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /quarterly_earnings/ テスト
# ---------------------------------------------------------------------------

def test_get_quarterly_earnings_returns_200_on_success(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetQuarterlyEarningsSuccess)
    monkeypatch.setattr(router_module, "_orm_to_dict", lambda r: r)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/quarterly_earnings/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1

    app.dependency_overrides.clear()


def test_get_quarterly_earnings_returns_404_when_empty(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetQuarterlyEarningsEmpty)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/quarterly_earnings/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_get_quarterly_earnings_returns_400_on_value_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetQuarterlyEarningsValueError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/quarterly_earnings/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "code is required"

    app.dependency_overrides.clear()


def test_get_quarterly_earnings_returns_500_on_unexpected_error(monkeypatch):
    from app.api.v1.routers import corp_finance_data as router_module

    monkeypatch.setattr(router_module, "CorporateFinanceDataService", _GetQuarterlyEarningsUnexpectedError)
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/corp_finance_data/quarterly_earnings/",
        params={"code": "7203", "market": "T"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred"

    app.dependency_overrides.clear()
