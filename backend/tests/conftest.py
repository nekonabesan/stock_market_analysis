import sys
import types
from unittest.mock import MagicMock

import pytest

from app.api.v1.services.stock_data import StockDataService

# ---------------------------------------------------------------------------
# ノートブック専用ライブラリ スタブ
# API コンテナのテスト環境には plotly / Modules が存在しないため、
# pytest の収集フェーズより前に sys.modules を埋めておく。
# ---------------------------------------------------------------------------
# plotly stub
if "plotly" not in sys.modules:
    _fake_plotly = types.ModuleType("plotly")
    _fake_plotly_go = types.ModuleType("plotly.graph_objects")
    _fake_plotly_go.Figure = MagicMock
    _fake_plotly.graph_objects = _fake_plotly_go
    sys.modules["plotly"] = _fake_plotly
    sys.modules["plotly.graph_objects"] = _fake_plotly_go

# Modules stub (notebook-only package)
if "Modules" not in sys.modules:
    _fake_modules = types.ModuleType("Modules")
    _fake_get_market_data = types.ModuleType("Modules.get_market_data")
    _fake_get_market_data.GetMarketData = MagicMock
    _fake_modules.get_market_data = _fake_get_market_data
    sys.modules["Modules"] = _fake_modules
    sys.modules["Modules.get_market_data"] = _fake_get_market_data


# rci.py stub（テスト用 FakeRci）
if "app.api.v1.services.rci" not in sys.modules:
    _fake_rci_module = types.ModuleType("app.api.v1.services.rci")

    class FakeRci:
        def RCI(self, close, timeperiod=9):
            # テスト用: リストの長さに合わせて値を返す
            # 計算期間までは NaN を返す
            result = []
            for i in range(len(close)):
                if i < timeperiod - 1:
                    # 計算期間に満たない場合は NaN を返す
                    result.append(float('nan'))
                else:
                    # テスト用の値: iの位置によって -40 から 40 の値を返す
                    result.append(-40.0 + (i % 80))
            return result

    _fake_rci_module.Rci = FakeRci
    sys.modules["app.api.v1.services.rci"] = _fake_rci_module


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def stock_data_service(mock_db):
    return StockDataService(db_session=mock_db)
