"""Tanah petak: bedengan elips + kerikil & retakan dari noise ber-seed."""
from __future__ import annotations

import math
import random

import cairo

from graphics import colors
from graphics.node import Node


class SoilNode(Node):
    """Petak tanah. Origin = pusat bedengan.

    moisture 0..1 : 0 = kering (terang + retak), 1 = basah (gelap, tanpa retak).
    Semua tekstur dibuat SEKALI di __init__ dari `seed` -> tidak berkedip tiap frame.
    """

    def __init__(self, width: float = 90.0, height: float = 36.0, seed: int = 0,
                 moisture: float = 0.3, name: str = "Tanah") -> None:
        super().__init__(name)
        self.width = width
        self.height = height
        self.seed = seed
        self.moisture = colors.clamp01(moisture)
        self.pebbles: list[tuple[float, float, float, float]] = []   # x, y, r, shade
        self.cracks: list[list[tuple[float, float]]] = []
        self._generate()

    @property
    def params(self) -> tuple:
        return (self.width, self.height, self.seed, round(self.moisture, 3))

    def local_bounds(self) -> tuple[float, float, float, float]:
        return (-self.width / 2, -self.height / 2, self.width / 2, self.height / 2)

    # ---------------------------------------------------------- generator
    def _inside(self, x: float, y: float) -> bool:
        a, b = self.width / 2, self.height / 2
        return (x / a) ** 2 + (y / b) ** 2 <= 0.9

    def _generate(self) -> None:
        """[GRAFKOM] Procedural modeling: kerikil & retakan acak ber-seed."""
        rng = random.Random(self.seed)
        a, b = self.width / 2, self.height / 2
        n_pebbles = int(self.width * self.height / 55)
        while len(self.pebbles) < n_pebbles:
            x, y = rng.uniform(-a, a), rng.uniform(-b, b)
            if self._inside(x, y):
                self.pebbles.append((x, y, rng.uniform(0.5, 1.6), rng.random()))
        for _ in range(rng.randint(4, 7)):
            x, y = rng.uniform(-a * 0.7, a * 0.7), rng.uniform(-b * 0.7, b * 0.7)
            ang = rng.uniform(0, 2 * math.pi)
            pts = [(x, y)]
            for _ in range(rng.randint(3, 5)):
                ang += rng.uniform(-0.8, 0.8)
                step = rng.uniform(3.0, 7.0)
                x, y = x + math.cos(ang) * step, y + math.sin(ang) * step * 0.5
                if not self._inside(x, y):
                    break
                pts.append((x, y))
            if len(pts) >= 2:
                self.cracks.append(pts)

    # ---------------------------------------------------------- gambar
    def _ellipse_path(self, ctx: cairo.Context) -> None:
        ctx.save()
        ctx.scale(self.width / 2, self.height / 2)
        ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
        ctx.restore()

    def draw_self(self, ctx: cairo.Context) -> None:
        base = colors.lerp_color(colors.SOIL_DRY, colors.SOIL_WET, self.moisture)  # blending

        # bayangan di bawah bedengan
        ctx.save()
        ctx.translate(0, self.height * 0.08)
        self._ellipse_path(ctx)
        ctx.restore()
        colors.set_source(ctx, colors.SHADOW, 0.25)
        ctx.fill()

        # badan tanah (gradasi: tengah lebih terang)
        self._ellipse_path(ctx)
        grad = cairo.RadialGradient(0, -self.height * 0.15, 2, 0, 0, self.width * 0.55)
        grad.add_color_stop_rgb(0.0, *colors.lighten(base, 0.12))
        grad.add_color_stop_rgb(1.0, *colors.darken(base, 0.18))
        ctx.set_source(grad)
        ctx.fill_preserve()

        # [GRAFKOM] Clipping & masking: tekstur dipotong mengikuti tepi elips
        ctx.save()
        ctx.clip()
        for x, y, r, shade in self.pebbles:
            col = colors.lerp_color(colors.SOIL_PEBBLE_DARK, colors.SOIL_PEBBLE_LIGHT, shade)
            colors.set_source(ctx, col, 0.75)
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.fill()
        crack_alpha = 0.55 * (1.0 - self.moisture)
        if crack_alpha > 0.02:
            colors.set_source(ctx, colors.SOIL_CRACK, crack_alpha)
            ctx.set_line_width(0.7)
            for pts in self.cracks:
                ctx.move_to(*pts[0])
                for p in pts[1:]:
                    ctx.line_to(*p)
                ctx.stroke()
        ctx.restore()

        # garis tepi
        self._ellipse_path(ctx)
        colors.set_source(ctx, colors.darken(base, 0.5), 0.8)
        ctx.set_line_width(1.0)
        ctx.stroke()
