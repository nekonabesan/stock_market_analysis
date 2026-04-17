from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal
from app.models.sector import Sector
from app.models.white_list import WhiteList
from app.models.currency import Currency
from seeds.init import load_sector_records, load_white_list_records, load_currency_records
def _upsert_currency_records(records: list[dict]) -> tuple[int, int]:
	inserted = 0
	updated = 0

	deduped: dict[str, dict] = {}
	for record in records:
		market = record.get("market")
		if not market:
			continue
		deduped[market] = record

	with SessionLocal() as db:
		for market, record in deduped.items():
			market = record.get("market")
			currency = record.get("currency")
			if not market:
				continue

			row = db.query(Currency).filter_by(market=market).first()
			if row is None:
				db.add(Currency(market=market, currency=currency))
				inserted += 1
				continue

			changed = False
			if row.currency != currency:
				row.currency = currency
				changed = True

			if changed:
				updated += 1

		db.commit()

	return inserted, updated


def _upsert_sector_records(records: list[dict]) -> tuple[int, int]:
	inserted = 0
	updated = 0

	with SessionLocal() as db:
		for record in records:
			sector_id = record.get("id")
			name = record.get("name")
			if sector_id is None or not name:
				continue

			row = db.get(Sector, sector_id)
			if row is None:
				db.add(Sector(id=sector_id, name=name))
				inserted += 1
				continue

			if row.name != name:
				row.name = name
				updated += 1

		db.commit()

	return inserted, updated


def _upsert_white_list_records(records: list[dict]) -> tuple[int, int]:
	inserted = 0
	updated = 0

	deduped: dict[tuple[str, str], dict] = {}
	for record in records:
		market = record.get("market")
		code = record.get("code")
		if not market or not code:
			continue
		deduped[(market, code)] = record

	with SessionLocal() as db:
		for (market, code), record in deduped.items():
			market = record.get("market")
			code = record.get("code")
			name = record.get("name")
			if not market or not code or not name:
				continue

			pk = (market, code)
			row = db.get(WhiteList, pk)
			if row is None:
				db.add(
					WhiteList(
						market=market,
						code=code,
						name=name,
						sector_id=record.get("sector_id"),
						summary=record.get("summary"),
						currency=record.get("currency"),
						is_etf=record.get("is_etf"),
						trading_unit=record.get("trading_unit"),
					)
				)
				inserted += 1
				continue

			changed = False
			for key in ("name", "sector_id", "summary", "currency", "is_etf", "trading_unit"):
				value = record.get(key)
				if getattr(row, key) != value:
					setattr(row, key, value)
					changed = True

			if changed:
				updated += 1

		db.commit()

	return inserted, updated


def main() -> None:
	try:
		sector_records = load_sector_records()
		white_list_records = load_white_list_records()
		currency_records = load_currency_records()

		sector_inserted, sector_updated = _upsert_sector_records(sector_records)
		wl_inserted, wl_updated = _upsert_white_list_records(white_list_records)
		currency_inserted, currency_updated = _upsert_currency_records(currency_records)
	except SQLAlchemyError as e:
		raise RuntimeError("seed execution failed") from e

	print(
		"seed completed "
		f"(mst_sector: +{sector_inserted} / ~{sector_updated}, "
		f"trn_white_list: +{wl_inserted} / ~{wl_updated}, "
		f"mst_currency: +{currency_inserted} / ~{currency_updated})"
	)


if __name__ == "__main__":
	main()
