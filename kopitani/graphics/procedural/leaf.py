"""Daun kopi: elips runcing dari 2 kurva Bezier."""
from __future__ import annotations

import cairo

from graphics import colors
from graphics.node import Node


def leaf_path(ctx: cairo.Context, length: float, width: float) -> None:
    """[GRAFKOM] Path & complex shapes: bentuk daun runcing dari 2 kurva Bezier.

    Pangkal di (0, 0), ujung di (0, -length) (daun menghadap ke atas).
    """
    ctx.new_path()
    ctx.move_to(0, 0)
    # sisi kanan
    ctx.curve_to(width, -length * 0.25, width * 0.8, -length * 0.75, 0, -length)
    # sisi kiri (kembali ke pangkal)
    ctx.curve_to(-width * 0.8, -length * 0.75, -width, -length * 0.25, 0, 0)
    ctx.close_path()


class LeafNode(Node):
    """Satu helai daun. Origin = pangkal daun, arah daun = sumbu -y lokal."""

    def __init__(self, length: float = 16.0, width: float = 7.0,
                 color: colors.Color = colors.LEAF_HEALTHY, name: str = "Daun") -> None:
        super().__init__(name)
        self.length = length
        self.width = width
        self.color = color
        self._edge = colors.darken(color, 0.35)

    @property
    def params(self) -> tuple:
        return (round(self.length, 3), round(self.width, 3),
                tuple(round(c, 3) for c in self.color))

    def local_bounds(self) -> tuple[float, float, float, float]:
        w = self.width * 0.8
        return (-w, -self.length, w, 0.0)

    def draw_self(self, ctx: cairo.Context) -> None:
        leaf_path(ctx, self.length, self.width)
        colors.set_source(ctx, self.color)
        ctx.fill_preserve()
        colors.set_source(ctx, self._edge, 0.9)
        ctx.set_line_width(0.6)
        ctx.stroke()
        # tulang daun
        colors.set_source(ctx, colors.LEAF_VEIN, 0.8)
        ctx.set_line_width(0.5)
        ctx.move_to(0, 0)
        ctx.line_to(0, -self.length * 0.92)
        ctx.stroke()
