"""Aturan tanam sampai jual, terpisah dari render dan input WebSocket."""
from __future__ import annotations

from math import isfinite

from game.data_loader import RegionMonth
from game.formulas import Config, drying_days, growth_per_day, sale_value
from game.state import Batch, GameState, Plot


class Game:
    def __init__(self, records: dict[tuple[str, int], RegionMonth], config: Config,
                 region_id: str, month: int) -> None:
        self.records = records
        self.config = config
        self.state = GameState(config.starting_balance, region_id, month)
        self.data  # fail early if the selected region/month has no data

    @property
    def data(self) -> RegionMonth:
        try:
            return self.records[(self.state.region_id, self.state.month)]
        except KeyError as exc:
            raise ValueError("data wilayah/bulan tidak tersedia") from exc

    def select_region(self, region_id: str, month: int) -> None:
        self._active()
        if (region_id, month) not in self.records:
            raise ValueError("data wilayah/bulan tidak tersedia")
        self.state.region_id, self.state.month = region_id, month

    def _active(self) -> None:
        if self.state.finished:
            raise ValueError("musim sudah berakhir")

    def _plot(self, index: int) -> Plot:
        if type(index) is not int or not 0 <= index < len(self.state.plots):
            raise ValueError("petak harus 0..4")
        return self.state.plots[index]

    def plant(self, index: int, variety: str) -> None:
        self._active()
        plot = self._plot(index)
        if variety not in ("Robusta", "Arabika") or plot.variety:
            raise ValueError("varietas tidak dikenal atau petak sudah ditanam")
        plot.variety = variety

    def care(self, index: int, action: str) -> None:
        self._active()
        plot = self._plot(index)
        if not plot.variety or plot.stage == 4 or action not in ("water", "fertilize"):
            raise ValueError("tindakan tidak berlaku untuk petak ini")
        flag = "watered" if action == "water" else "fertilized"
        cost = self.config.water_cost if action == "water" else self.config.fertilizer_cost
        if getattr(plot, flag) or self.state.balance < cost:
            raise ValueError("tindakan sudah dilakukan atau saldo tidak cukup")
        setattr(plot, flag, True)
        self.state.balance -= cost

    def advance_day(self) -> None:
        self._active()
        if self.state.day >= self.config.season_days:
            self.state.finished = True
            return
        for plot in self.state.plots:
            if plot.variety and plot.growth < 1:
                plot.growth = min(1.0, plot.growth + growth_per_day(
                    self.data.rain_mm, self.data.temp_c, plot.watered,
                    plot.fertilized, self.config))
                if plot.growth >= 0.75 and plot.mature_day is None:
                    plot.mature_day = self.state.day + 1
            plot.watered = plot.fertilized = False
        self.state.day += 1

    def ripeness(self, index: int) -> float:
        plot = self._plot(index)
        if plot.mature_day is None:
            return 0.0
        return min(1.0, max(0.0, (self.state.day - plot.mature_day) / self.config.ripen_days))

    def harvest(self, index: int, berry_ripeness: list[float] | None = None) -> Batch:
        self._active()
        plot = self._plot(index)
        if plot.mature_day is None:
            raise ValueError("pohon belum berbuah")
        berries = berry_ripeness if berry_ripeness is not None else [self.ripeness(index)]
        if not isinstance(berries, list) or not berries or any(
                isinstance(v, bool) or not isinstance(v, (int, float))
                or not isfinite(v) or not 0 <= v <= 1 for v in berries):
            raise ValueError("kematangan ceri harus 0..1 dan tidak kosong")
        grades = {grade: 0 for grade in ("A", "B", "C")}
        for value in berries:
            grade = ("A" if value >= self.config.grade_red_at else
                     "B" if value >= self.config.grade_yellow_at else "C")
            grades[grade] += 1
        kg = self.data.yield_kg_per_ha / self.config.trees_per_ha
        batch = Batch(kg=kg, grades=grades)
        self.state.batches.append(batch)
        self.state.plots[index] = Plot()
        return batch

    def process(self, batch: Batch, step: str, roast: str | None = None) -> None:
        self._active()
        if not any(item is batch for item in self.state.batches):
            raise ValueError("batch bukan milik permainan ini")
        next_step = {"harvested": "sorted", "sorted": "pulped",
                     "pulped": "drying", "drying": "dried", "dried": "roasted"}
        if next_step.get(batch.stage) != step:
            raise ValueError("urutan proses tidak valid")
        if step == "dried" and self.state.day < batch.ready_day:
            raise ValueError("penjemuran belum selesai")
        if step == "roasted":
            if roast not in self.config.roast_factors:
                raise ValueError("tingkat roasting tidak dikenal")
            batch.roast = roast
        if step == "drying":
            batch.ready_day = self.state.day + drying_days(self.data.rain_mm, self.config)
        batch.stage = step

    def sell(self, batch: Batch) -> float:
        self._active()
        if (not any(item is batch for item in self.state.batches)
                or batch.stage != "roasted" or batch.roast is None):
            raise ValueError("batch belum siap dijual")
        amount = sale_value(batch.kg, self.data.price_idr_per_kg, batch.grades,
                            batch.roast, self.config)
        total = sum(batch.grades.values())
        self.state.sold_kg += batch.kg
        self.state.sold_grade_a_kg += batch.kg * batch.grades["A"] / total
        self.state.balance += amount
        self.state.batches.remove(batch)
        return amount

    def stars(self) -> int:
        if not self.state.finished:
            raise ValueError("musim belum berakhir")
        if self.state.balance <= self.config.starting_balance:
            return 0
        if self.state.balance < self.config.star_target:
            return 1
        if self.state.sold_kg and self.state.sold_grade_a_kg / self.state.sold_kg >= 0.7:
            return 3
        return 2
