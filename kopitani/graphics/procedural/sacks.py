"""Karung hasil olahan + tumpukan karung (jumlah dari volume)."""
from __future__ import annotations

import math
import random

import cairo

from graphics import colors
from graphics.node import Node

# Tata letak tumpukan piramida, dari baris paling bawah. Total = 10 karung.
PILE_ROWS = (4, 3, 2, 1)
MAX_SACKS = sum(PILE_ROWS)


def sacks_from_volume(volume_kg: float, kg_per_sack: float) -> tuple[int, float]:
    """Ubah volume (kg) jadi (jumlah karung tampil, isi karung terakhir 0..1).

    `kg_per_sack` diberikan pemanggil (dari data/CONFIG), bukan ditentukan di sini.
    Jumlah dibatasi MAX_SACKS agar tumpukan tetap muat di layar.
    """
    if volume_kg <= 0 or kg_per_sack <= 0:
        return 0, 0.0
    full = int(volume_kg // kg_per_sack)
    rest = (volume_kg - full * kg_per_sack) / kg_per_sack
    if full >= MAX_SACKS:
        return MAX_SACKS, 1.0
    if rest > 1e-9:
        return full + 1, rest
    return full, 1.0


class SackNode(Node):
    """Satu karung dengan jendela level isi. Origin = tengah dasar karung."""

    def __init__(self, fill: float = 1.0, roast: float = 0.66, width: float = 34.0,
                 height: float = 30.0, name: str = "Karung") -> None:
        super().__init__(name)
        self.fill = colors.clamp01(fill)
        self.roast = colors.clamp01(roast)
        self.width = width
        self.height = height

    @property
    def params(self) -> tuple:
        return (round(self.fill, 3), round(self.roast, 3), self.width, self.height)

    def local_bounds(self) -> tuple[float, float, float, float]:
        return (-self.width / 2, -self.height - 6, self.width / 2, 0.0)

    # -------------------------------------------------------------- path
    def _body_path(self, ctx: cairo.Context) -> None:
        """[GRAFKOM] Path & complex shapes: siluet karung (badan menggembung + leher)."""
        w, h = self.width / 2, self.height
        ctx.new_path()
        ctx.move_to(-w * 0.55, -h)                        # leher kiri
        ctx.curve_to(-w * 1.25, -h * 0.85, -w * 1.15, -h * 0.1, -w * 0.9, 0)
        ctx.line_to(w * 0.9, 0)
        ctx.curve_to(w * 1.15, -h * 0.1, w * 1.25, -h * 0.85, w * 0.55, -h)
        ctx.close_path()

    def _window_path(self, ctx: cairo.Context) -> None:
        ctx.save()
        ctx.translate(0, -self.height * 0.45)
        ctx.scale(self.width * 0.26, self.height * 0.3)
        ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
        ctx.restore()

    # -------------------------------------------------------------- gambar
    def draw_self(self, ctx: cairo.Context) -> None:
        w, h = self.width / 2, self.height

        # badan karung (gradasi samping)
        self._body_path(ctx)
        grad = cairo.LinearGradient(-w, 0, w, 0)
        grad.add_color_stop_rgb(0.0, *colors.SACK_SHADE)
        grad.add_color_stop_rgb(0.45, *colors.SACK_BASE)
        grad.add_color_stop_rgb(1.0, *colors.SACK_SHADE)
        ctx.set_source(grad)
        ctx.fill_preserve()
        colors.set_source(ctx, colors.OUTLINE, 0.8)
        ctx.set_line_width(0.8)
        ctx.stroke()

        # ikatan leher
        colors.set_source(ctx, colors.SACK_ROPE)
        ctx.set_line_width(1.6)
        ctx.move_to(-w * 0.6, -h + 1.5)
        ctx.line_to(w * 0.6, -h + 1.5)
        ctx.stroke()
        colors.set_source(ctx, colors.SACK_SHADE)
        ctx.move_to(-w * 0.55, -h)
        ctx.line_to(-w * 0.8, -h - 5)
        ctx.line_to(-w * 0.1, -h - 2)
        ctx.line_to(w * 0.1, -h - 2)
        ctx.line_to(w * 0.8, -h - 5)
        ctx.line_to(w * 0.55, -h)
        ctx.close_path()
        ctx.fill()

        # jendela level isi
        self._window_path(ctx)
        colors.set_source(ctx, colors.SACK_WINDOW)
        ctx.fill_preserve()

        # [GRAFKOM] Clipping & masking: isi biji hanya terlihat di dalam jendela,
        # tingginya mengikuti level isi (fill 0..1).
        ctx.save()
        ctx.clip()
        win_top = -self.height * 0.45 - self.height * 0.3
        win_h = self.height * 0.6
        level_y = win_top + win_h * (1.0 - self.fill)
        colors.set_source(ctx, colors.bean_color(self.roast))
        ctx.rectangle(-w, level_y, self.width, win_h + 2)
        ctx.fill()
        ctx.restore()

        self._window_path(ctx)
        colors.set_source(ctx, colors.OUTLINE, 0.8)
        ctx.set_line_width(0.8)
        ctx.stroke()


class SacksPile(Node):
    """Tumpukan karung berbentuk piramida. Origin = tengah dasar tumpukan.

    Jumlah dari `sacks_from_volume`. Posisi/kemiringan kecil diacak dengan seed.
    """

    def __init__(self, volume_kg: float = 0.0, kg_per_sack: float = 60.0, roast: float = 0.66,
                 seed: int = 0, name: str = "TumpukanKarung") -> None:
        super().__init__(name)
        self.volume_kg = volume_kg
        self.kg_per_sack = kg_per_sack
        self.roast = roast
        self.seed = seed
        self.n_sacks, last_fill = sacks_from_volume(volume_kg, kg_per_sack)
        self._build(last_fill)

    @property
    def params(self) -> tuple:
        return (self.n_sacks, round(self.roast, 3), self.seed)

    def _build(self, last_fill: float) -> None:
        rng = random.Random(self.seed)
        sw, sh = 34.0, 30.0
        placed = 0
        for row, count in enumerate(PILE_ROWS):
            row_w = count * sw * 0.95
            for i in range(count):
                if placed >= self.n_sacks:
                    return
                sack = SackNode(fill=1.0, roast=self.roast, width=sw, height=sh)
                sack.tx = -row_w / 2 + sw * 0.475 + i * sw * 0.95 + rng.uniform(-1.5, 1.5)
                sack.ty = -row * sh * 0.78
                sack.rotation = rng.uniform(-0.05, 0.05)
                placed += 1
                if placed == self.n_sacks:
                    sack.fill = last_fill
                self.add(sack)
