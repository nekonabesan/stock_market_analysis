from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.api.v1.services.stocks import StocksService



def _build_service_with_joined_rows(rows: list[tuple[object, str | None]]) -> StocksService:
    db = MagicMock()
    db.execute.return_value.all.return_value = rows
    return StocksService(db_session=db)


def test_get_stock_data_returns_none_when_no_rows() -> None:
    service = _build_service_with_joined_rows([])
    result = service.get_stock_data()
    assert result is None


def test_get_stock_data_returns_dict_list_from_model_columns() -> None:
    row = SimpleNamespace(
        id=1,
        code="7203",
        market="TSE",
        currency_id=2,
        name="TOYOTA",
        sector="AUTO",
        memo="",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    # currency名は"JPY"と仮定
    service = _build_service_with_joined_rows([(row, "JPY")])
    result = service.get_stock_data()
    assert isinstance(result, list)
    assert result[0]["id"] == 1
    assert result[0]["code"] == "7203"
    assert result[0]["market"] == "TSE"
    assert result[0]["currency"] == "JPY"


def test_get_stock_data_returns_currency_none_when_no_currency() -> None:
    row = SimpleNamespace(
        id=2,
        code="XXXX",
        market="FOO",
        currency_id=None,
        name="NOCUR",
        sector="BAR",
        memo="",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    # currencyが紐付かない場合
    service = _build_service_with_joined_rows([(row, None)])
    result = service.get_stock_data()
    assert isinstance(result, list)
    assert result[0]["id"] == 2
    assert result[0]["currency"] is None


def test_to_dict_prefers_model_method_when_available() -> None:
    class RowWithToDict:
        def to_dict(self) -> dict:
            return {"code": "1301", "market": "TSE"}

    service = _build_service_with_joined_rows([])

    result = service._to_dict(RowWithToDict())

    assert result == {"code": "1301", "market": "TSE"}
