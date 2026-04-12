from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.api.v1.services.stocks import StocksService


def _build_service_with_rows(rows: list[object]) -> StocksService:
    db = MagicMock()
    db.execute.return_value.scalars.return_value.all.return_value = rows
    return StocksService(db_session=db)


def test_get_stock_data_returns_none_when_no_rows() -> None:
    service = _build_service_with_rows([])

    result = service.get_stock_data()

    assert result is None


def test_get_stock_data_returns_dict_list_from_model_columns() -> None:
    row = SimpleNamespace(
        id=1,
        code="7203",
        market="TSE",
        name="TOYOTA",
        sector="AUTO",
        memo="",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    service = _build_service_with_rows([row])

    result = service.get_stock_data()

    assert isinstance(result, list)
    assert result[0]["id"] == 1
    assert result[0]["code"] == "7203"
    assert result[0]["market"] == "TSE"


def test_to_dict_prefers_model_method_when_available() -> None:
    class RowWithToDict:
        def to_dict(self) -> dict:
            return {"code": "1301", "market": "TSE"}

    service = _build_service_with_rows([])

    result = service._to_dict(RowWithToDict())

    assert result == {"code": "1301", "market": "TSE"}
