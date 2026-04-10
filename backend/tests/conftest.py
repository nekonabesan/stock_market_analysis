from unittest.mock import MagicMock

import pytest

from app.api.v1.services.stock_data import StockDataService


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def stock_data_service(mock_db):
    return StockDataService(db_session=mock_db)
