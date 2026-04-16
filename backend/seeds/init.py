from __future__ import annotations

import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"


def _load_json_records(filename: str) -> list[dict]:
	path = DATA_DIR / filename
	if not path.exists():
		return []

	with path.open("r", encoding="utf-8") as f:
		data = json.load(f)

	if not isinstance(data, list):
		raise ValueError(f"{filename} must contain a JSON array")

	return [row for row in data if isinstance(row, dict)]


def load_sector_records() -> list[dict]:
	return _load_json_records("mst_sector.json")


def load_white_list_records() -> list[dict]:
	return _load_json_records("trn_white_list.json")
