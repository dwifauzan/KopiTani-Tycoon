"""Mockup scene penuh (latar + rumah + pabrik + kebun 3x3 + UI) -> preview_scene_c.png.

    python tools/preview_scene_c.py
Catatan: mesin & conveyor adalah Bagian B; di sini hanya kotak penanda agar terlihat
posisinya di dalam aula pabrik. Angka di panel adalah CONTOH (berlabel DUMMY).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphics import colors  # noqa: E402
from graphics.node import Node  # noqa: E402
from graphics.objects.ui_panel import BadgeNode, PanelNode  # noqa: E402
from graphics.procedural.coffee_tree import build_coffee_tree  # noqa: E402
from graphics.procedural.sacks import SacksPile  # noqa: E402
from graphics.procedural.scenery import (BushNode, CloudNode, FarmHouseNode,  # noqa: E402
                                         FactoryNode, FenceNode, HillsNode, SkyNode)
from graphics.procedural.soil import SoilNode  # noqa: E402

W, H = 960, 540
HORIZON = 250


def build_scene(t: float = 0.0) -> Node:
    root = Node("Scene")
    latar = root.add(Node("Latar"))
    latar.add(SkyNode(W, HORIZON + 40, sun_x=820, sun_y=64))
    for i, (x, y, w, sp) in enumerate([(150, 62, 130, 5), (430, 40, 100, 3), (640, 96, 140, 7)]):
        c = CloudNode(seed=i + 1, width=w, speed=sp, wrap_width=W)
        c.base_x, c.ty = x, y
        c.update(t)
        latar.add(c)
    hills = HillsNode(W, depth=300, seed=4, layers=3)
    hills.ty = HORIZON
    latar.add(hills)
    ground = Node("Tanah")

    class Ground(Node):
        def draw_self(self, ctx: cairo.Context) -> None:
            g = cairo.LinearGradient(0, HORIZON + 10, 0, H)
            g.add_color_stop_rgb(0, *colors.GRASS)
            g.add_color_stop_rgb(1, *colors.GRASS_DARK)
            ctx.set_source(g)
            ctx.rectangle(0, HORIZON + 10, W, H)
            ctx.fill()
    latar.add(Ground("Rumput"))

    house = root.add(FarmHouseNode())
    house.tx, house.ty = 95, HORIZON + 62
    fence = root.add(FenceNode(length=230, seed=2))
    fence.tx, fence.ty = 0, HORIZON + 90
    for i, (x, y) in enumerate([(20, 305), (170, 312)]):
        b = root.add(BushNode(seed=i, size=30))
        b.tx, b.ty = x, y

    factory = root.add(FactoryNode())
    factory.tx, factory.ty = 770, HORIZON + 112
    factory.update(t)
    x0, y0, x1, _ = factory.hall_rect          # penanda posisi 3 mesin (Bagian B)
    slot = (x1 - x0) / 3
    for i in range(3):
        box = Node(f"MesinB{i}")

        class Box(Node):
            def draw_self(self, ctx: cairo.Context) -> None:
                colors.set_source(ctx, colors.FACTORY_ROOF, 0.9)
                ctx.rectangle(-26, -46, 52, 46)
                ctx.fill()
        m = factory.add(Box(f"Mesin{i}"))
        m.tx, m.ty = x0 + slot * (i + 0.5), -8
    pile = factory.add(SacksPile(volume_kg=420, kg_per_sack=60, roast=0.7, seed=5))
    pile.tx, pile.ty, pile.sx, pile.sy = 0, 28, 0.9, 0.9

    kebun = root.add(Node("Kebun"))
    stages = [4, 3, 4, 2, 4, 3, 1, 4, 2]
    for r in range(3):
        for c in range(3):
            i = r * 3 + c
            plot = kebun.add(Node(f"Petak{i}"))
            depth = 0.82 + 0.09 * r
            plot.tx, plot.ty = 262 + c * 128 + r * 8, 332 + r * 66
            plot.add(SoilNode(width=100 * depth + 14, height=34 * depth + 4, seed=i, moisture=0.2 + 0.08 * i))
            tree = build_coffee_tree(seed=30 + i, stage=stages[i], vigor=0.6 + 0.04 * i)
            tree.sx *= depth * 0.78
            tree.sy *= depth * 0.78
            tree.update(t)
            plot.add(tree)
    return root


def main() -> None:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t0 = time.perf_counter()
    root = build_scene(0.0)
    root.render(ctx)
    print(f"scene penuh: {(time.perf_counter() - t0) * 1000:.0f} ms")
    panel = PanelNode(230, "Data: Jember - Juli",
                      [("Curah hujan", "contoh"), ("Suhu rata-rata", "contoh"), ("Harga dasar", "contoh")],
                      is_dummy=True)
    panel.tx, panel.ty = 710, 14
    panel.render(ctx)
    badge = BadgeNode("Rp 0 (contoh)", "Saldo")
    badge.tx, badge.ty = 16, 14
    badge.render(ctx)
    out = Path(__file__).resolve().parent.parent / "preview_scene_c.png"
    surf.write_to_png(str(out))
    print("tersimpan:", out.name)


if __name__ == "__main__":
    main()
