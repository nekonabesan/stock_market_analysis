from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from urllib import error as url_error
from urllib import request as url_request

from dotenv import dotenv_values
from sqlalchemy import select

from app.api.v1.services.corp_finance_data import CorporateFinanceDataService
from app.api.v1.services.stock_data import StockDataService
from app.core.logger import logger
from app.db.session import SessionLocal
from app.models.white_list import WhiteList

ENV_LOCAL_PATH = Path("/app/app/.env.local")
API_BASE_URL = os.getenv("INIT_API_BASE_URL", "http://127.0.0.1:8000")
API_PREFIX = "/api/v1"


def _load_init_period() -> tuple[date, date]:
    env_values = dotenv_values(ENV_LOCAL_PATH) if ENV_LOCAL_PATH.exists() else {}

    start_raw = os.getenv("INIT_START") or env_values.get("INIT_START")
    end_raw = os.getenv("INIT_END") or env_values.get("INIT_END")

    if not start_raw or not end_raw:
        raise ValueError("INIT_START and INIT_END must be defined in app/.env.local")

    try:
        start = date.fromisoformat(str(start_raw))
        end = date.fromisoformat(str(end_raw))
    except ValueError as e:
        raise ValueError("INIT_START and INIT_END must be YYYY-MM-DD format") from e

    if start > end:
        raise ValueError("INIT_START must be less than or equal to INIT_END")

    return start, end


def _fetch_targets() -> list[tuple[str, str | None]]:
    with SessionLocal() as db:
        rows = db.execute(
            select(WhiteList.code, WhiteList.market).order_by(WhiteList.market.asc(), WhiteList.code.asc())
        ).all()

    return [(row.code, row.market) for row in rows]


def _post_json(url: str, payload: dict) -> bool:
    req = url_request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with url_request.urlopen(req, timeout=60) as response:
            return 200 <= response.getcode() < 300
    except url_error.HTTPError as e:
        logger.error(f"API request failed: url={url}, status={e.code}, reason={e.reason}")
    except url_error.URLError as e:
        logger.error(f"API request failed: url={url}, reason={e.reason}")

    return False


def _fallback_stock_update(code: str, market: str | None, start: date, end: date) -> bool:
    url = f"{API_BASE_URL}{API_PREFIX}/stock_price/"
    payload = {
        "code": code,
        "market": market,
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
    return _post_json(url, payload)


def _fallback_finance_update(code: str, market: str | None) -> bool:
    url = f"{API_BASE_URL}{API_PREFIX}/corp_finance_data/"
    payload = {
        "code": code,
        "market": market,
    }
    return _post_json(url, payload)


def _update_stock(code: str, market: str | None, start: date, end: date) -> bool:
    try:
        with SessionLocal() as db:
            service = StockDataService(db)
            return service.update_stock_data(code=code, market=market, start=start, end=end)
    except Exception as e:
        logger.warning(f"stock update failed, fallback to API: code={code}, market={market}, error={e}")

    api_ok = _fallback_stock_update(code, market, start, end)
    if not api_ok:
        logger.error(f"stock update failed by service and API: code={code}, market={market}")
    return api_ok


def _update_finance(code: str, market: str | None) -> bool:
    try:
        with SessionLocal() as db:
            service = CorporateFinanceDataService(db_session=db)
            return service.update_corp_finance_data(code=code, market=market)
    except Exception as e:
        logger.warning(f"finance update failed, fallback to API: code={code}, market={market}, error={e}")

    api_ok = _fallback_finance_update(code, market)
    if not api_ok:
        logger.error(f"finance update failed by service and API: code={code}, market={market}")
    return api_ok


def main() -> None:
    try:
        start, end = _load_init_period()
    except ValueError as e:
        logger.error(str(e))
        raise SystemExit(2) from e

    targets = _fetch_targets()
    if not targets:
        logger.warning("No targets found in trn_white_list")
        return

    logger.info(f"init start: targets={len(targets)}, period={start}..{end}")

    success_count = 0
    failed_symbols: list[str] = []

    for code, market in targets:
        stock_ok = _update_stock(code, market, start, end)
        finance_ok = _update_finance(code, market)

        if stock_ok and finance_ok:
            success_count += 1
            continue

        failed_symbols.append(f"{market}:{code}")
        logger.warning(
            "init failed for symbol "
            f"code={code}, market={market}, stock_ok={stock_ok}, finance_ok={finance_ok}"
        )

    failed_count = len(failed_symbols)
    logger.info(
        "init completed "
        f"(total={len(targets)}, success={success_count}, failed={failed_count})"
    )

    if failed_symbols:
        logger.warning(f"failed symbols: {', '.join(failed_symbols)}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
