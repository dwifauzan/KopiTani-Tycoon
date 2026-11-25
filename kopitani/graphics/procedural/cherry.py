"""Ceri kopi (buah) dan bunga kopi, plus pembuat cluster ber-seed."""
from __future__ import annotations

import math
import random

import cairo

from graphics import colors
from graphics.node import Node


class CherryNode(Node):
    """Satu ceri kopi. Origin = titik tempel tangkai, ceri menggantung ke +y."""

    def __init__(self, radius: float = 3.6, ripeness: float = 1.0, name: str = "Ceri") -> None:
        super().__init__(name)
        self.radius = radius
        self._ripeness = 0.0
        self._base: colors.Color = colors.CHERRY_GREEN
        self._edge: colors.Color = colors.CHERRY_GREEN
        self._shine: colors.Color = colors.CHERRY_GREEN
        self.ripeness = ripeness

    @property
    def ripeness(self) -> float:
        return self._ripeness

    @ripeness.setter
    def ripeness(self, value: float) -> None:
        """Warna dihitung SEKALI saat kematangan berubah (bukan tiap frame)."""
        self._ripeness = colors.clamp01(value)
        self._base = colors.cherry_color(self._ripeness)   # [GRAFKOM] Color blending
        self._edge = colors.darken(self._base, 0.55)
        self._shine = colors.lighten(self._base, 0.55)

    @property
    def params(self) -> tuple:
        return (round(self.radius, 3), round(self.ripeness, 3))

    @property
    def color(self) -> colors.Color:
        return self._base

    def local_bounds(self) -> tuple[float, float, float, float]:
        r = self.radius
        return (-r, 0.0, r, r * 2.6)

    def draw_self(self, ctx: cairo.Context) -> None:
        r = self.radius
        cy = r * 1.4

        # tangkai
        colors.set_source(ctx, colors.LEAF_VEIN)
        ctx.set_line_width(0.7)
        ctx.move_to(0, 0)
        ctx.line_to(0, cy - r)
        ctx.stroke()

        # [GRAFKOM] Path: badan ceri = lingkaran yang diskalakan jadi elips
        ctx.save()
        ctx.translate(0, cy)
        ctx.scale(1.0, 1.15)
        ctx.arc(0, 0, r, 0, 2 * math.pi)
        ctx.restore()
        colors.set_source(ctx, self._base)
        ctx.fill_preserve()
        colors.set_source(ctx, self._edge, 0.85)
        ctx.set_line_width(0.5)
        ctx.stroke()

        # kilau (highlight) + "mahkota" kecil di ujung bawah
        colors.set_source(ctx, self._shine, 0.8)
        ctx.arc(-r * 0.35, cy - r * 0.4, r * 0.28, 0, 2 * math.pi)
        ctx.fill()
        colors.set_source(ctx, colors.CHERRY_CROWN, 0.9)
        ctx.arc(0, cy + r * 1.05, r * 0.2, 0, 2 * math.pi)
        ctx.fill()


class FlowerNode(Node):
    """Bunga kopi: 5 kelopak putih (tahap 3). Origin = pusat bunga."""

    def __init__(self, size: float = 3.2, name: str = "Bunga") -> None:
        super().__init__(name)
        self.size = size

    @property
    def params(self) -> tuple:
        return (round(self.size, 3),)

    def local_bounds(self) -> tuple[float, float, float, float]:
        s = self.size * 1.6
        return (-s, -s, s, s)

    def draw_self(self, ctx: cairo.Context) -> None:
        s = self.size
        for i in range(5):
            ctx.save()
            ctx.rotate(i * 2 * math.pi / 5)  # [GRAFKOM] Transformasi 2D: rotasi kelopak
            ctx.translate(0, -s * 0.8)
            ctx.scale(0.55, 1.0)
            ctx.arc(0, 0, s * 0.75, 0, 2 * math.pi)
            ctx.restore()
            colors.set_source(ctx, colors.FLOWER_PETAL, 0.95)
            ctx.fill_preserve()
            colors.set_source(ctx, colors.darken(colors.FLOWER_PETAL, 0.25), 0.7)
            ctx.set_line_width(0.3)
            ctx.stroke()
        colors.set_source(ctx, colors.FLOWER_CENTER)
        ctx.arc(0, 0, s * 0.35, 0, 2 * math.pi)
        ctx.fill()


def make_cherry_cluster(rng: random.Random, count: int, ripeness: float | None = None,
                        radius: float = 3.6, name: str = "ClusterCeri") -> Node:
    """Cluster ceri (menggantung ke +y). Semua acak memakai `rng` ber-seed.

    ripeness=None -> tiap ceri punya kematangan acak 0.3..1.0 (campuran hijau-kuning-merah).
    ripeness=nilai -> semua dekat nilai itu (+-0.08).
    """
    cluster = Node(name)
    for _ in range(count):
        x = rng.uniform(-6.0, 6.0)
        y = rng.uniform(1.0, 9.0)
        r = radius * rng.uniform(0.85, 1.15)
        if ripeness is None:
            rp = rng.uniform(0.3, 1.0)
        else:
            rp = colors.clamp01(ripeness + rng.uniform(-0.08, 0.08))
        cherry = CherryNode(r, rp)
        cherry.tx, cherry.ty = x, y
        cherry.rotation = rng.uniform(-0.25, 0.25)
        cluster.add(cherry)
    return cluster


def make_flower_cluster(rng: random.Random, count: int, name: str = "ClusterBunga") -> Node:
    """Cluster bunga kecil di ketiak daun."""
    cluster = Node(name)
    for _ in range(count):
        flower = FlowerNode(rng.uniform(2.6, 3.6))
        flower.tx = rng.uniform(-6.0, 6.0)
        flower.ty = rng.uniform(-2.0, 6.0)
        flower.rotation = rng.uniform(0, 2 * math.pi)
        cluster.add(flower)
    return cluster
