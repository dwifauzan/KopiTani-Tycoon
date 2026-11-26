"""Overlay UI Bagian A pada kanvas 320×180; dipanggil renderer scene graph Bagian B."""
from __future__ import annotations

import math
import cairo

from docs import colors
from game.logic import Game


def _rect(ctx: cairo.Context, x: int, y: int, w: int, h: int,
          color: colors.Color) -> None:
    colors.set_source(ctx, color)
    ctx.rectangle(x, y, w, h)
    ctx.fill()


def _text(ctx: cairo.Context, value: str, x: int, y: int, size: int = 7,
          color: colors.Color = colors.UI_TEXT) -> None:
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    colors.set_source(ctx, color)
    ctx.move_to(x, y)
    ctx.show_text(value)


def _icon(ctx: cairo.Context, name: str, x: int, y: int) -> None:
    """Ikon 8×8 dari path Pycairo, mengikuti palet Bagian C."""
    ctx.save()
    ctx.translate(x, y)
    colors.set_source(ctx, colors.UI_GOLD)
    if name in ("coin", "temperature"):
        ctx.arc(4, 4 if name == "coin" else 6, 3 if name == "coin" else 2, 0, 2 * math.pi)
        ctx.fill()
        if name == "temperature":
            ctx.rectangle(3, 0, 2, 6)
            ctx.fill()
    elif name in ("calendar", "fertilizer"):
        ctx.rectangle(1, 1, 6, 6)
        ctx.fill()
        if name == "calendar":
            colors.set_source(ctx, colors.UI_PANEL_HEADER)
            ctx.rectangle(2, 3, 4, 1)
            ctx.fill()
    elif name in ("water", "rain"):
        ctx.move_to(4, 0)
        ctx.curve_to(2, 3, 1, 4, 1, 5)
        ctx.curve_to(1, 9, 7, 9, 7, 5)
        ctx.curve_to(7, 4, 6, 3, 4, 0)
        ctx.fill()
    elif name == "star":
        for i in range(10):
            radius = 4 if i % 2 == 0 else 2
            point = (4 + radius * math.sin(i * math.pi / 5),
                     4 - radius * math.cos(i * math.pi / 5))
            (ctx.move_to if i == 0 else ctx.line_to)(*point)
        ctx.close_path()
        ctx.fill()
    ctx.restore()


def draw_ui(ctx: cairo.Context, game: Game, selected_plot: int | None = None,
            show_data: bool = False, tooltip: str = "") -> None:
    """Gambar HUD, panel data, tombol petak, tooltip, dan hasil akhir musim."""
    state, data = game.state, game.data
    ctx.save()
    ctx.set_antialias(cairo.ANTIALIAS_NONE)
    _rect(ctx, 0, 0, 320, 16, colors.UI_PANEL_HEADER)
    _icon(ctx, "coin", 4, 4)
    _text(ctx, f"Rp {state.balance:,.0f}", 14, 11, color=colors.UI_TEXT_LIGHT)
    _icon(ctx, "calendar", 88, 4)
    _text(ctx, f"Hari {state.day}/{game.config.season_days}", 98, 11,
          color=colors.UI_TEXT_LIGHT)
    _text(ctx, f"{state.region_id[:12]} {state.month:02d}", 155, 11,
          color=colors.UI_TEXT_LIGHT)
    if any("DUMMY" in source.upper() for source in data.sources.values()):
        _text(ctx, "DUMMY", 240, 11, 6, colors.UI_ACCENT)
    _text(ctx, "DATA", 277, 11, color=colors.UI_GOLD)

    # [GRAFKOM] Compositing: penanda petak pilihan berada di atas scene kebun.
    for i, plot in enumerate(state.plots):
        x = 8 + i * 30
        if i == selected_plot:
            _rect(ctx, x - 2, 128, 28, 24, colors.UI_GOLD)
        _rect(ctx, x, 130, 24, 20, colors.UI_PANEL)
        _text(ctx, f"{i + 1}:{plot.stage or '-'}", x + 3, 143, 7)

    if selected_plot is not None and not 0 <= selected_plot < len(state.plots):
        raise ValueError("petak harus 0..4")
    if selected_plot is not None and not state.finished:
        plot = state.plots[selected_plot]
        actions = ("ROBUSTA", "ARABIKA") if not plot.variety else ("SIRAM", "PUPUK", "PANEN")
        for i, action in enumerate(actions):
            x = 5 + i * 37
            _rect(ctx, x, 162, 34, 13, colors.UI_PANEL_HEADER)
            if action in ("SIRAM", "PUPUK"):
                _icon(ctx, "water" if action == "SIRAM" else "fertilizer", x + 1, 164)
            label = {"ROBUSTA": "ROB", "ARABIKA": "ARA"}.get(action, action)
            _text(ctx, label, x + (9 if action in ("SIRAM", "PUPUK") else 2),
                  171, 6, colors.UI_TEXT_LIGHT)
        _text(ctx, f"Petak {selected_plot + 1}: {plot.variety or 'kosong'}", 5, 156)

    if not state.finished:
        if state.batches:
            batch = state.batches[0]
            _text(ctx, f"{batch.stage} {batch.kg:.1f}kg", 124, 156, 6)
            if batch.stage == "dried":
                actions = ("LIGHT", "MED", "DARK")
            elif batch.stage == "roasted":
                actions = ("JUAL",)
            else:
                actions = ("PROSES",)
            for i, action in enumerate(actions):
                x = 124 + i * 38
                _rect(ctx, x, 162, 35, 13, colors.UI_PANEL_HEADER)
                _text(ctx, action, x + 2, 171, 6, colors.UI_TEXT_LIGHT)
        _rect(ctx, 278, 162, 37, 13, colors.UI_GOLD)
        _text(ctx, "HARI +", 280, 171, 6)

    if show_data:
        _rect(ctx, 198, 18, 118, 73, colors.UI_PANEL)
        _rect(ctx, 198, 18, 118, 12, colors.UI_PANEL_HEADER)
        _text(ctx, "DATA WILAYAH", 202, 27, color=colors.UI_TEXT_LIGHT)
        _icon(ctx, "rain", 201, 32)
        _text(ctx, f"Hujan  {data.rain_mm:g} mm", 211, 40)
        _icon(ctx, "temperature", 201, 42)
        _text(ctx, f"Suhu   {data.temp_c:g} C", 211, 50)
        _text(ctx, f"Harga  Rp {data.price_idr_per_kg:,.0f}/kg", 202, 60)
        dummy = any("DUMMY" in source.upper() for source in data.sources.values())
        source = "DUMMY - bukan data nyata" if dummy else "Sumber: " + data.sources["climate"]
        _text(ctx, source[:28], 202, 77, 6, colors.UI_ACCENT if dummy else colors.UI_MUTED)

    if tooltip:
        width = min(310, max(36, len(tooltip) * 4 + 8))
        _rect(ctx, 5, 138, width, 12, colors.UI_PANEL)
        _text(ctx, tooltip[:70], 9, 147, 6)

    if state.finished:
        _rect(ctx, 60, 38, 200, 103, colors.UI_PANEL)
        _rect(ctx, 60, 38, 200, 18, colors.UI_PANEL_HEADER)
        _text(ctx, "AKHIR MUSIM", 68, 50, 10, colors.UI_TEXT_LIGHT)
        if game.stars():
            for i in range(game.stars()):
                _icon(ctx, "star", 68 + i * 12, 65)
        else:
            _text(ctx, "Belum ada bintang", 68, 75, 8, colors.UI_GOLD)
        _text(ctx, f"Saldo: Rp {state.balance:,.0f}", 68, 94)
        pct = 100 * state.sold_grade_a_kg / state.sold_kg if state.sold_kg else 0
        _text(ctx, f"Kopi grade A: {pct:.0f}%", 68, 108)
        _text(ctx, "Mutu panen memengaruhi harga jual.", 68, 126, 6)
    ctx.restore()
