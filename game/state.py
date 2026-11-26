"""State permainan murni; tidak menyimpan objek grafika."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Plot:
    variety: str | None = None
    growth: float = 0.0
    mature_day: int | None = None
    watered: bool = False
    fertilized: bool = False

    @property
    def stage(self) -> int:
        return min(4, int(self.growth * 4) + 1) if self.variety else 0


@dataclass
class Batch:
    kg: float
    grades: dict[str, int]
    stage: str = "harvested"
    ready_day: int = 0
    roast: str | None = None


@dataclass
class GameState:
    balance: float
    region_id: str
    month: int
    day: int = 1
    plots: list[Plot] = field(default_factory=lambda: [Plot() for _ in range(5)])
    batches: list[Batch] = field(default_factory=list)
    sold_kg: float = 0.0
    sold_grade_a_kg: float = 0.0
    finished: bool = False
