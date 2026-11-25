"""Render pratinjau Bagian C ke PNG (tanpa server) + ukur waktu render.

Jalankan dari root repo:
    python tools/preview_bagian_c.py            # -> preview_bagian_c.png
    python tools/preview_bagian_c.py --frames   # + 3 frame ayunan angin
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
from graphics.procedural.cherry import CherryNode  # noqa: E402
from graphics.procedural.coffee_tree import build_coffee_tree  # noqa: E402
from graphics.procedural.leaf import LeafNode  # noqa: E402
from graphics.procedural.sacks import SackNode, SacksPile  # noqa: E402
from graphics.procedural.soil import SoilNode  # noqa: E402

W, H = 960, 540


def draw_background(ctx: cairo.Context) -> None:
    """[GRAFKOM] Compositing: layer paling bawah = langit gradasi + rumput."""
    sky = cairo.LinearGradient(0, 0, 0, H * 0.62)
    sky.add_color_stop_rgb(0, *colors.SKY_TOP)
    sky.add_color_stop_rgb(1, *colors.SKY_BOTTOM)
    ctx.set_source(sky)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    grass = cairo.LinearGradient(0, H * 0.45, 0, H)
    grass.add_color_stop_rgb(0, *colors.GRASS)
    grass.add_color_stop_rgb(1, *colors.GRASS_DARK)
    ctx.set_source(grass)
    ctx.rectangle(0, H * 0.45, W, H)
    ctx.fill()


def label(ctx: cairo.Context, text: str, x: float, y: float, size: float = 12) -> None:
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    colors.set_source(ctx, colors.UI_TEXT)
    ctx.move_to(x, y)
    ctx.show_text(text)


def build_scene(t: float = 0.0) -> Node:
    root = Node("Scene")
    garden = root.add(Node("Kebun"))
    # 4 tahap pohon, tiap tahap di petak tanah sendiri
    for i, stage in enumerate((1, 2, 3, 4)):
        plot = garden.add(Node(f"Petak{stage}"))
        plot.tx, plot.ty = 130 + i * 195, 300
        plot.add(SoilNode(width=120, height=44, seed=10 + i, moisture=0.25 + 0.15 * i))
        tree = build_coffee_tree(seed=100 + i, stage=stage, vigor=0.55 + 0.15 * i)
        tree.update(t)
        plot.add(tree)
    return root


def main() -> None:
    frames = "--frames" in sys.argv
    out = Path(__file__).resolve().parent.parent
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw_background(ctx)

    scene = build_scene(0.0)
    t0 = time.perf_counter()
    scene.render(ctx)
    print(f"render 4 pohon: {(time.perf_counter() - t0) * 1000:.1f} ms")

    for i in range(4):
        label(ctx, f"Tahap {i + 1}", 100 + i * 195, 335)

    # ramp warna ceri (hijau -> kuning -> merah)
    label(ctx, "Color blending: kematangan ceri", 40, 380)
    for i in range(9):
        c = CherryNode(radius=7, ripeness=i / 8)
        c.tx, c.ty = 50 + i * 36, 388
        c.render(ctx)
    # ramp warna biji (hijau -> light -> medium -> dark)
    label(ctx, "Color blending: tingkat sangrai", 40, 440)
    for i, roast in enumerate((0.0, 0.33, 0.66, 1.0)):
        ctx.save()
        ctx.translate(70 + i * 62, 505)
        sack = SackNode(fill=0.75, roast=roast, width=44, height=36)
        sack.render(ctx)
        ctx.restore()
    # daun
    for i in range(3):
        leaf = LeafNode(34, 15, colors.leaf_color(1.0 - i * 0.4))
        leaf.tx, leaf.ty = 330 + i * 40, 475
        leaf.render(ctx)
    label(ctx, "Daun (Bezier)", 320, 490, 11)

    pile = SacksPile(volume_kg=520, kg_per_sack=60, roast=0.66, seed=3)
    pile.tx, pile.ty = 560, 510
    pile.render(ctx)
    label(ctx, "Tumpukan karung (clipping level isi)", 470, 525, 11)

    panel = PanelNode(220, "Data: Jember - Juli",
                      [("Curah hujan", "contoh"), ("Suhu rata-rata", "contoh"), ("Harga dasar", "contoh")],
                      is_dummy=True)
    panel.tx, panel.ty = 710, 20
    panel.render(ctx)
    badge = BadgeNode("Rp 0 (contoh)", "Saldo")
    badge.tx, badge.ty = 20, 20
    badge.render(ctx)

    surf.write_to_png(str(out / "preview_bagian_c.png"))
    print("tersimpan: preview_bagian_c.png")

    if frames:   # bukti ayunan angin: 3 waktu berbeda
        for k, t in enumerate((0.0, 0.8, 1.6)):
            s2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
            c2 = cairo.Context(s2)
            draw_background(c2)
            build_scene(t).render(c2)
            s2.write_to_png(str(out / f"preview_angin_{k}.png"))
        print("tersimpan: preview_angin_0..2.png")

    # benchmark: 9 pohon tahap 4 + animasi
    trees = [build_coffee_tree(i, 4, 1.0) for i in range(9)]
    bench = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    bctx = cairo.Context(bench)
    n = 20
    t0 = time.perf_counter()
    for f in range(n):
        for j, tr in enumerate(trees):
            tr.update(f * 0.05)
            tr.tx, tr.ty = 100 + (j % 3) * 300, 180 + (j // 3) * 160
            tr.render(bctx)
    per = (time.perf_counter() - t0) / n * 1000
    print(f"9 pohon tahap 4: {per:.1f} ms/frame (~{1000 / per:.0f} fps hanya bagian pohon)")


if __name__ == "__main__":
    main()
