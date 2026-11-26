"""Rumus permainan. Semua angka agronomi dan ekonomi harus datang dari data/sumber."""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite


@dataclass(frozen=True)
class Config:
    # TODO: sumber untuk rentang ideal, faktor grade/roasting, durasi, biaya, dan target.
    rain_range: tuple[float, float, float, float]  # luar min, ideal min/max, luar max (mm/bulan)
    temp_range: tuple[float, float, float, float]  # derajat Celsius
    base_growth: float  # bagian dari siklus tumbuh per hari
    care_bonus: float  # pengali tambahan per tindakan per hari
    dry_base_days: float
    dry_rain_factor: float
    grade_factors: dict[str, float]
    roast_factors: dict[str, float]
    water_cost: float
    fertilizer_cost: float
    starting_balance: float
    star_target: float
    trees_per_ha: float
    ripen_days: float
    grade_yellow_at: float
    grade_red_at: float
    season_days: int = 30  # aturan permainan pada PRD v2, bukan angka agronomi

    def __post_init__(self) -> None:
        for bounds in (self.rain_range, self.temp_range):
            if (len(bounds) != 4 or not all(isfinite(v) for v in bounds)
                    or list(bounds) != sorted(bounds) or bounds[0] == bounds[1]
                    or bounds[2] == bounds[3]):
                raise ValueError("rentang iklim harus: luar_min < ideal_min <= ideal_max < luar_max")
        values = (self.base_growth, self.care_bonus, self.dry_base_days,
                  self.dry_rain_factor, self.water_cost, self.fertilizer_cost,
                  self.starting_balance, self.star_target, self.trees_per_ha,
                  self.ripen_days)
        if (not all(isfinite(v) and v >= 0 for v in values)
                or self.base_growth == 0 or self.dry_base_days == 0
                or self.season_days < 1):
            raise ValueError("parameter permainan harus bernilai hingga dan tidak negatif")
        if (self.trees_per_ha == 0 or self.ripen_days == 0
                or not 0 < self.grade_yellow_at < self.grade_red_at <= 1):
            raise ValueError("kepadatan pohon, hari matang, dan batas grade tidak valid")
        if (set(self.grade_factors) != {"A", "B", "C"}
                or set(self.roast_factors) != {"light", "medium", "dark"}):
            raise ValueError("faktor grade A/B/C dan roast light/medium/dark wajib lengkap")
        if not all(isfinite(v) and v > 0 for v in (
                *self.grade_factors.values(), *self.roast_factors.values())):
            raise ValueError("faktor harga harus positif")


def climate_factor(value: float, bounds: tuple[float, float, float, float]) -> float:
    """Faktor 0..1; nilai ideal mendapat 1, di luar batas mendapat 0."""
    if not isfinite(value):
        raise ValueError("nilai iklim harus hingga")
    outer_low, ideal_low, ideal_high, outer_high = bounds
    if value <= outer_low or value >= outer_high:
        return 0.0
    if value < ideal_low:
        return (value - outer_low) / (ideal_low - outer_low)
    if value > ideal_high:
        return (outer_high - value) / (outer_high - ideal_high)
    return 1.0


def growth_per_day(rain_mm: float, temp_c: float, watered: bool,
                   fertilized: bool, config: Config) -> float:
    care = 1 + config.care_bonus * (int(watered) + int(fertilized))
    return (config.base_growth * climate_factor(rain_mm, config.rain_range)
            * climate_factor(temp_c, config.temp_range) * care)


def drying_days(rain_mm: float, config: Config) -> int:
    if not isfinite(rain_mm) or rain_mm < 0:
        raise ValueError("curah hujan harus hingga dan tidak negatif")
    rain_normalized = min(rain_mm / config.rain_range[3], 1.0)
    return ceil(config.dry_base_days * (1 + config.dry_rain_factor * rain_normalized))


def sale_value(kg: float, base_price_per_kg: float, grades: dict[str, int],
               roast: str, config: Config) -> float:
    if not isfinite(kg) or not isfinite(base_price_per_kg) or kg < 0 or base_price_per_kg < 0:
        raise ValueError("berat dan harga harus hingga dan tidak negatif")
    if (roast not in config.roast_factors
            or set(grades) - config.grade_factors.keys()
            or any(v < 0 for v in grades.values())):
        raise ValueError("grade atau roasting tidak dikenal")
    total = sum(grades.values())
    if total == 0 or kg == 0:
        return 0.0
    grade_factor = sum(config.grade_factors[k] * n for k, n in grades.items()) / total
    return kg * base_price_per_kg * grade_factor * config.roast_factors[roast]
