from typing import Any, Dict
import math
import numpy as np
from sqlalchemy import inspect as sa_inspect


class OrmSerializer:
    """ORM オブジェクトを安全に dict に変換するユーティリティ。

    - カラム名/属性名の差分に耐える
    - numpy / numpy.scalar / float NaN を None に置換
    - 可能な限り Python ネイティブ型に変換する
    """

    @staticmethod
    def to_dict(row: Any) -> Dict[str, Any]:
        mapper = sa_inspect(type(row))
        result: Dict[str, Any] = {}
        for col in mapper.columns:
            try:
                val = getattr(row, col.key)
            except Exception:
                try:
                    val = getattr(row, col.name)
                except Exception:
                    val = None

            if val is not None:
                try:
                    if isinstance(val, float) and math.isnan(val):
                        val = None
                    else:
                        if hasattr(val, "item"):
                            try:
                                v_item = val.item()
                                if isinstance(v_item, float) and math.isnan(v_item):
                                    val = None
                                else:
                                    val = v_item
                            except Exception:
                                pass
                        else:
                            try:
                                if np.isnan(val):
                                    val = None
                            except Exception:
                                pass
                except Exception:
                    pass

            result[col.key] = val

        return result
