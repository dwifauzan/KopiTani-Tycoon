"""Baca data permainan yang sudah diproses dan validasi satuan/provenansinya."""
from __future__ import annotations

import json
from dataclasses import dataclass
from math import isfinite
from pathlib import Path

from game.formulas import Config


@dataclass(frozen=True)
class RegionMonth:
    region_id: str
    month: int
    rain_mm: float
    temp_c: float
    production_kg: float
    area_ha: float
    price_idr_per_kg: float
    sources: dict[str, str]

    @property
    def yield_kg_per_ha(self) -> float:
        return self.production_kg / self.area_ha


def load_records(path: str | Path) -> dict[tuple[str, int], RegionMonth]:
    """Format: JSON array objek RegionMonth; sumber tiap kelompok data wajib ada."""
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"gagal membaca data {path}: {exc}") from exc
    if not isinstance(raw, list) or not raw:
        raise ValueError("data harus berupa array JSON yang tidak kosong")
    records = {}
    required = set(RegionMonth.__dataclass_fields__)
    for row_number, row in enumerate(raw, 1):
        if not isinstance(row, dict) or required - row.keys():
            missing = required - row.keys() if isinstance(row, dict) else required
            raise ValueError(f"baris {row_number}: kolom hilang {sorted(missing)}")
        try:
            record = RegionMonth(**{name: row[name] for name in required})
            if (not isinstance(record.region_id, str) or not record.region_id.strip()
                    or type(record.month) is not int or not 1 <= record.month <= 12):
                raise ValueError("region_id/bulan tidak valid")
            for name in ("rain_mm", "temp_c", "production_kg", "area_ha", "price_idr_per_kg"):
                value = getattr(record, name)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                    raise ValueError(f"{name} harus angka hingga")
            if min(record.rain_mm, record.production_kg, record.price_idr_per_kg) < 0 or record.area_ha <= 0:
                raise ValueError("hujan, produksi, harga >= 0 dan luas areal > 0")
            if (not isinstance(record.sources, dict) or any(
                    not isinstance(record.sources.get(k), str)
                    or not record.sources[k].strip()
                    for k in ("climate", "production", "price"))):
                raise ValueError("sumber climate, production, price wajib dicatat")
        except (TypeError, ValueError) as exc:
            raise ValueError(f"baris {row_number}: {exc}") from exc
        key = (record.region_id, record.month)
        if key in records:
            raise ValueError(f"baris {row_number}: wilayah/bulan duplikat {key}")
        records[key] = record
    return records


def load_config(path: str | Path) -> Config:
    """Baca parameter yang harus disertai sumber sebelum game produksi dijalankan."""
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"gagal membaca konfigurasi {path}: {exc}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("sources"), dict):
        raise ValueError("konfigurasi wajib mencatat sources")
    for name in ("agronomy", "postharvest", "economy"):
        source = raw["sources"].get(name)
        if not isinstance(source, str) or not source.strip():
            raise ValueError(f"sumber {name} wajib dicatat")
    keys = set(Config.__dataclass_fields__)
    missing = keys - raw.keys() - {"season_days"}
    if missing:
        raise ValueError(f"parameter hilang: {sorted(missing)}")
    try:
        return Config(**{key: raw[key] for key in keys if key in raw})
    except (TypeError, ValueError) as exc:
        raise ValueError(f"konfigurasi tidak valid: {exc}") from exc
