"""Palet warna & fungsi color blending.

Aturan proyek: SEMUA warna hanya didefinisikan di file ini.
Warna = tuple RGB (0..1).
"""
from __future__ import annotations

from typing import Sequence

import cairo

Color = tuple[float, float, float]


def hex_to_rgb(code: str) -> Color:
    """'#RRGGBB' -> (r, g, b) 0..1."""
    code = code.lstrip("#")
    return tuple(int(code[i:i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


# ---------------------------------------------------------------- palet dasar
SKY_TOP = hex_to_rgb("#8EC9E8")
SKY_BOTTOM = hex_to_rgb("#E6F4EA")
GRASS = hex_to_rgb("#7DB05A")
GRASS_DARK = hex_to_rgb("#5C8F42")

SOIL_DRY = hex_to_rgb("#A47551")
SOIL_WET = hex_to_rgb("#4E3424")
SOIL_PEBBLE_LIGHT = hex_to_rgb("#C9A27A")
SOIL_PEBBLE_DARK = hex_to_rgb("#3B271B")
SOIL_CRACK = hex_to_rgb("#2E1D13")

TRUNK_LIGHT = hex_to_rgb("#9A7B55")
TRUNK_DARK = hex_to_rgb("#5E4630")

LEAF_HEALTHY = hex_to_rgb("#2F7D32")
LEAF_LIGHT = hex_to_rgb("#4FA64A")
LEAF_WEAK = hex_to_rgb("#A9B84A")      # daun pucat saat vigor rendah
LEAF_VEIN = hex_to_rgb("#1E5A22")

CHERRY_GREEN = hex_to_rgb("#6BA43A")
CHERRY_YELLOW = hex_to_rgb("#EDC531")
CHERRY_RED = hex_to_rgb("#C8161F")
CHERRY_CROWN = hex_to_rgb("#3A1410")
FLOWER_PETAL = hex_to_rgb("#FFFFFF")
FLOWER_CENTER = hex_to_rgb("#F2D544")

BEAN_GREEN = hex_to_rgb("#8C9E66")
BEAN_LIGHT = hex_to_rgb("#B38050")
BEAN_MEDIUM = hex_to_rgb("#734527")
BEAN_DARK = hex_to_rgb("#33190F")

SACK_BASE = hex_to_rgb("#D9BE8C")
SACK_SHADE = hex_to_rgb("#B79A66")
SACK_ROPE = hex_to_rgb("#7A5A2E")
SACK_WINDOW = hex_to_rgb("#F4EFE3")

OUTLINE = hex_to_rgb("#2B2118")
SHADOW = hex_to_rgb("#000000")

UI_PANEL = hex_to_rgb("#FFF8EC")
UI_PANEL_HEADER = hex_to_rgb("#5A3A22")
UI_TEXT = hex_to_rgb("#3A2A1C")
UI_TEXT_LIGHT = hex_to_rgb("#FFF8EC")
UI_MUTED = hex_to_rgb("#8A7560")
UI_ACCENT = hex_to_rgb("#C8161F")
UI_GOLD = hex_to_rgb("#E0A526")


# ---- latar / bangunan (scenery.py)
SUN = hex_to_rgb("#FFE9A0")
SUN_GLOW = hex_to_rgb("#FFF6D6")
CLOUD = hex_to_rgb("#FFFFFF")
CLOUD_SHADE = hex_to_rgb("#D5E4EE")
HILL_FAR = hex_to_rgb("#9CC3B4")
HILL_MID = hex_to_rgb("#7FB08A")
HILL_NEAR = hex_to_rgb("#639C58")
FENCE_WOOD = hex_to_rgb("#B98C5A")
FENCE_DARK = hex_to_rgb("#7A5832")
WALL_HOUSE = hex_to_rgb("#F2E3C6")
WALL_HOUSE_SHADE = hex_to_rgb("#D9C6A2")
ROOF_HOUSE = hex_to_rgb("#B5482F")
ROOF_HOUSE_DARK = hex_to_rgb("#8A3322")
DOOR_WOOD = hex_to_rgb("#6B4428")
GLASS = hex_to_rgb("#A9D6EA")
GLASS_SHINE = hex_to_rgb("#E9F7FC")
WINDOW_FRAME = hex_to_rgb("#F8F4EA")
STONE = hex_to_rgb("#A59C90")
BRICK = hex_to_rgb("#B8664A")
BRICK_DARK = hex_to_rgb("#8F4A35")
FACTORY_WALL = hex_to_rgb("#D8CDBA")
FACTORY_WALL_SHADE = hex_to_rgb("#B9AD97")
FACTORY_ROOF = hex_to_rgb("#6E7F8C")
FACTORY_ROOF_LIGHT = hex_to_rgb("#93A5B3")
FACTORY_INTERIOR = hex_to_rgb("#3B3027")
FACTORY_SIGN = hex_to_rgb("#4A2F1B")
SMOKE = hex_to_rgb("#E8E8E8")


# ----------------------------------------------------------- color blending
def lerp(a: float, b: float, t: float) -> float:
    return a * (1.0 - t) + b * t   # tepat a saat t=0 dan tepat b saat t=1


def lerp_color(c1: Color, c2: Color, t: float) -> Color:
    """[GRAFKOM] Color blending: interpolasi linear dua warna RGB."""
    t = clamp01(t)
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def gradient_color(stops: Sequence[tuple[float, Color]], t: float) -> Color:
    """[GRAFKOM] Color blending multi-stop. `stops` terurut menaik, posisi 0..1."""
    t = clamp01(t)
    if t <= stops[0][0]:
        return stops[0][1]
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if t <= p1:
            span = p1 - p0
            return lerp_color(c0, c1, 0.0 if span == 0 else (t - p0) / span)
    return stops[-1][1]


def lighten(c: Color, amount: float) -> Color:
    return lerp_color(c, (1.0, 1.0, 1.0), amount)


def darken(c: Color, amount: float) -> Color:
    return lerp_color(c, (0.0, 0.0, 0.0), amount)


CHERRY_STOPS = [(0.0, CHERRY_GREEN), (0.5, CHERRY_YELLOW), (1.0, CHERRY_RED)]
BEAN_STOPS = [(0.0, BEAN_GREEN), (0.33, BEAN_LIGHT), (0.66, BEAN_MEDIUM), (1.0, BEAN_DARK)]


def cherry_color(ripeness: float) -> Color:
    """Kematangan ceri 0..1: hijau -> kuning -> merah."""
    return gradient_color(CHERRY_STOPS, ripeness)


def bean_color(roast: float) -> Color:
    """Tingkat sangrai 0..1: biji hijau -> light -> medium -> dark."""
    return gradient_color(BEAN_STOPS, roast)


def leaf_color(vigor: float, shade: float = 0.0) -> Color:
    """Warna daun: pucat (vigor rendah) -> hijau sehat. `shade` 0..1 = variasi terang."""
    base = lerp_color(LEAF_WEAK, LEAF_HEALTHY, clamp01(vigor))
    return lerp_color(base, LEAF_LIGHT, clamp01(shade) * 0.6)


def set_source(ctx: cairo.Context, color: Color, alpha: float = 1.0) -> None:
    ctx.set_source_rgba(color[0], color[1], color[2], alpha)
