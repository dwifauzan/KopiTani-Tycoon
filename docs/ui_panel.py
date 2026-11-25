"""Komponen UI: panel data (nilai + sumber) dan lencana saldo.

Semua digambar Pycairo (bukan HTML/Canvas JS). Warna dari colors.py.
"""
from __future__ import annotations

import math
from typing import Sequence

import cairo

from graphics import colors
from graphics.node import Node


def rounded_rect(ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float) -> None:
    """[GRAFKOM] Path & complex shapes: persegi bersudut membulat (4 busur)."""
    r = min(r, w / 2, h / 2)
    ctx.new_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def _font(ctx: cairo.Context, size: float, bold: bool = False, italic: bool = False) -> None:
    ctx.select_font_face(
        "Sans",
        cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


class PanelNode(Node):
    """Panel info data: judul, baris (label, nilai), dan baris sumber data.

    Origin = pojok kiri-atas panel.
    """

    HEADER_H = 26.0
    ROW_H = 18.0

    def __init__(self, width: float = 220.0, title: str = "Data",
                 rows: Sequence[tuple[str, str]] = (), source: str = "",
                 is_dummy: bool = False, name: str = "PanelData") -> None:
        super().__init__(name)
        self.width = width
        self.title = title
        self.rows = list(rows)
        self.source = source
        self.is_dummy = is_dummy      # data dummy WAJIB berlabel "DUMMY"

    @property
    def height(self) -> float:
        extra = 22.0 if (self.source or self.is_dummy) else 8.0
        return self.HEADER_H + self.ROW_H * len(self.rows) + extra

    def set_rows(self, rows: Sequence[tuple[str, str]], source: str = "") -> None:
        self.rows = list(rows)
        self.source = source

    def local_bounds(self) -> tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw_self(self, ctx: cairo.Context) -> None:
        w, h = self.width, self.height

        # [GRAFKOM] Compositing: bayangan semi-transparan di bawah panel
        rounded_rect(ctx, 3, 4, w, h, 10)
        colors.set_source(ctx, colors.SHADOW, 0.22)
        ctx.fill()

        rounded_rect(ctx, 0, 0, w, h, 10)
        colors.set_source(ctx, colors.UI_PANEL, 0.96)
        ctx.fill_preserve()

        # [GRAFKOM] Clipping: header berwarna mengikuti sudut membulat panel
        ctx.save()
        ctx.clip()
        colors.set_source(ctx, colors.UI_PANEL_HEADER)
        ctx.rectangle(0, 0, w, self.HEADER_H)
        ctx.fill()
        ctx.restore()

        rounded_rect(ctx, 0, 0, w, h, 10)
        colors.set_source(ctx, colors.UI_PANEL_HEADER)
        ctx.set_line_width(1.2)
        ctx.stroke()

        _font(ctx, 13, bold=True)
        colors.set_source(ctx, colors.UI_TEXT_LIGHT)
        ctx.move_to(10, 18)
        ctx.show_text(self.title)

        y = self.HEADER_H + 15
        for label, value in self.rows:
            _font(ctx, 11.5)
            colors.set_source(ctx, colors.UI_MUTED)
            ctx.move_to(10, y)
            ctx.show_text(label)
            _font(ctx, 11.5, bold=True)
            colors.set_source(ctx, colors.UI_TEXT)
            ext = ctx.text_extents(value)
            ctx.move_to(w - 10 - ext.x_advance, y)
            ctx.show_text(value)
            y += self.ROW_H

        if self.is_dummy:
            _font(ctx, 10, bold=True)
            colors.set_source(ctx, colors.UI_ACCENT)
            ctx.move_to(10, h - 8)
            ctx.show_text("DUMMY - bukan data nyata")
        elif self.source:
            _font(ctx, 9.5, italic=True)
            colors.set_source(ctx, colors.UI_MUTED)
            ctx.move_to(10, h - 8)
            ctx.show_text(f"Sumber: {self.source}")


class BadgeNode(Node):
    """Lencana kecil, mis. saldo uang. Origin = pojok kiri-atas."""

    def __init__(self, text: str = "", label: str = "Saldo", width: float = 160.0,
                 name: str = "Lencana") -> None:
        super().__init__(name)
        self.text = text
        self.label = label
        self.width = width

    def local_bounds(self) -> tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, 34.0)

    def draw_self(self, ctx: cairo.Context) -> None:
        w, h = self.width, 34.0
        rounded_rect(ctx, 2, 3, w, h, 17)
        colors.set_source(ctx, colors.SHADOW, 0.22)
        ctx.fill()

        rounded_rect(ctx, 0, 0, w, h, 17)
        grad = cairo.LinearGradient(0, 0, 0, h)
        grad.add_color_stop_rgb(0.0, *colors.lighten(colors.UI_GOLD, 0.25))
        grad.add_color_stop_rgb(1.0, *colors.UI_GOLD)
        ctx.set_source(grad)
        ctx.fill_preserve()
        colors.set_source(ctx, colors.darken(colors.UI_GOLD, 0.45))
        ctx.set_line_width(1.2)
        ctx.stroke()

        _font(ctx, 10)
        colors.set_source(ctx, colors.darken(colors.UI_GOLD, 0.6))
        ctx.move_to(14, 13)
        ctx.show_text(self.label)
        _font(ctx, 14, bold=True)
        colors.set_source(ctx, colors.UI_TEXT)
        ctx.move_to(14, 28)
        ctx.show_text(self.text)
