"""Dekorasi latar & bangunan: langit, awan, bukit, pagar, semak, rumah kebun, pabrik.

Semua dibuat dengan kode (Pycairo), bentuk acak memakai random.Random(seed)
sehingga identik di setiap frame. Tidak ada aset gambar luar.

Catatan integrasi:
- `FactoryNode` hanya CANGKANG bangunan (dinding, atap gerigi, cerobong berasap,
  bukaan aula). Mesin & conveyor (Bagian B) cukup di-`add` sebagai anak FactoryNode,
  posisikan di dalam `factory.hall_rect`.
- Objek bergerak (awan, asap) punya `update(t)` -> panggil tiap frame.
"""
from __future__ import annotations

import math
import random

import cairo

from graphics import colors
from graphics.node import Node
from graphics.objects.ui_panel import rounded_rect


# ====================================================================== langit
class SkyNode(Node):
    """Langit gradasi + matahari bercahaya. Origin = pojok kiri-atas."""

    def __init__(self, width: float = 960.0, height: float = 300.0,
                 sun_x: float = 800.0, sun_y: float = 70.0, name: str = "Langit") -> None:
        super().__init__(name)
        self.width, self.height = width, height
        self.sun_x, self.sun_y = sun_x, sun_y

    @property
    def params(self) -> tuple:
        return (self.width, self.height, self.sun_x, self.sun_y)

    def local_bounds(self) -> tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw_self(self, ctx: cairo.Context) -> None:
        sky = cairo.LinearGradient(0, 0, 0, self.height)   # [GRAFKOM] Color blending (gradasi)
        sky.add_color_stop_rgb(0.0, *colors.SKY_TOP)
        sky.add_color_stop_rgb(1.0, *colors.SKY_BOTTOM)
        ctx.set_source(sky)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

        # [GRAFKOM] Compositing: cahaya matahari = radial gradient dengan alpha menurun
        glow = cairo.RadialGradient(self.sun_x, self.sun_y, 6, self.sun_x, self.sun_y, 120)
        glow.add_color_stop_rgba(0.0, *colors.SUN_GLOW, 0.95)
        glow.add_color_stop_rgba(0.25, *colors.SUN, 0.45)
        glow.add_color_stop_rgba(1.0, *colors.SUN, 0.0)
        ctx.set_source(glow)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()
        colors.set_source(ctx, colors.SUN_GLOW)
        ctx.arc(self.sun_x, self.sun_y, 22, 0, 2 * math.pi)
        ctx.fill()


# ====================================================================== awan
class CloudNode(Node):
    """Awan dari gabungan lingkaran ber-seed. Origin = tengah dasar awan.

    update(t): awan melayang ke kanan dan muncul lagi dari kiri (wrap).
    """

    def __init__(self, seed: int = 0, width: float = 120.0, speed: float = 6.0,
                 wrap_width: float = 960.0, name: str = "Awan") -> None:
        super().__init__(name)
        self.seed, self.width, self.speed, self.wrap_width = seed, width, speed, wrap_width
        self.base_x = 0.0
        rng = random.Random(seed)
        self.puffs: list[tuple[float, float, float]] = []   # x, y, r
        n = rng.randint(5, 6)
        for i in range(n):
            f = i / (n - 1)
            r = width * rng.uniform(0.2, 0.27) * (1.0 - 0.4 * abs(f - 0.5) * 2)
            self.puffs.append((-width * 0.38 + f * width * 0.76, -r * rng.uniform(0.35, 0.85), r))

    @property
    def params(self) -> tuple:
        return (self.seed, self.width, tuple((round(a, 3), round(b, 3), round(c, 3)) for a, b, c in self.puffs))

    def local_bounds(self) -> tuple[float, float, float, float]:
        return (-self.width * 0.6, -self.width * 0.3, self.width * 0.6, 4.0)

    def update(self, t: float) -> None:
        """[GRAFKOM] Transformasi 2D: translasi awan terhadap waktu."""
        span = self.wrap_width + self.width * 2
        self.tx = (self.base_x + t * self.speed + self.width) % span - self.width

    def draw_self(self, ctx: cairo.Context) -> None:
        base_r = self.width * 0.13
        for dy, col, a in ((4.0, colors.CLOUD_SHADE, 0.85), (0.0, colors.CLOUD, 0.95)):
            colors.set_source(ctx, col, a)
            rounded_rect(ctx, -self.width * 0.46, -base_r * 1.5 + dy, self.width * 0.92,
                         base_r * 1.5, base_r * 0.75)       # dasar awan (new_path di dalamnya)
            for x, y, r in self.puffs:
                ctx.new_sub_path()
                ctx.arc(x, y + dy, r, 0, 2 * math.pi)
            ctx.fill()


# ====================================================================== bukit
class HillsNode(Node):
    """Bukit berlapis (jauh -> dekat) dari jumlah sinus ber-seed. Origin = kiri, garis dasar."""

    def __init__(self, width: float = 960.0, depth: float = 120.0, seed: int = 0,
                 layers: int = 3, amplitude: float = 38.0, name: str = "Bukit") -> None:
        super().__init__(name)
        self.width, self.depth, self.seed, self.layers = width, depth, seed, layers
        rng = random.Random(seed)
        self.layer_pts: list[list[tuple[float, float]]] = []
        for li in range(layers):
            amp = amplitude * (1.0 - 0.28 * li)
            waves = [(rng.uniform(0.004, 0.011) * (1 + li * 0.6), rng.uniform(0, 2 * math.pi),
                      rng.uniform(0.4, 1.0)) for _ in range(3)]
            pts = []
            step = 16
            for x in range(0, int(width) + step, step):
                y = -sum(a * math.sin(x * f + ph) for f, ph, a in waves) / 3 * amp * 1.6
                pts.append((float(x), y + li * 14.0 - (layers - li) * 6))
            self.layer_pts.append(pts)

    @property
    def params(self) -> tuple:
        return (self.width, self.depth, self.seed, self.layers)

    def local_bounds(self) -> tuple[float, float, float, float]:
        return (0.0, -self.depth, self.width, self.depth * 0.5)

    def draw_self(self, ctx: cairo.Context) -> None:
        for li, pts in enumerate(self.layer_pts):
            t = li / max(1, self.layers - 1)
            # [GRAFKOM] Color blending: lapisan jauh lebih pucat (kabut atmosfer)
            col = colors.gradient_color(
                [(0.0, colors.HILL_FAR), (0.5, colors.HILL_MID), (1.0, colors.HILL_NEAR)], t)
            ctx.move_to(0, self.depth)
            for x, y in pts:
                ctx.line_to(x, y)
            ctx.line_to(self.width, self.depth)
            ctx.close_path()
            grad = cairo.LinearGradient(0, -self.depth * 0.6, 0, self.depth)
            grad.add_color_stop_rgb(0.0, *colors.lighten(col, 0.12))
            grad.add_color_stop_rgb(1.0, *colors.darken(col, 0.08))
            ctx.set_source(grad)
            ctx.fill()


# ====================================================================== pagar
class FenceNode(Node):
    """Pagar kayu. Origin = ujung kiri, kaki pagar. Tinggi tiang & kemiringan acak ber-seed."""

    def __init__(self, length: float = 240.0, seed: int = 0, gap: float = 30.0,
                 height: float = 26.0, name: str = "Pagar") -> None:
        super().__init__(name)
        self.length, self.seed, self.gap, self.height = length, seed, gap, height
        rng = random.Random(seed)
        n = int(length // gap) + 1
        self.posts = [(i * gap, height * rng.uniform(0.92, 1.08), rng.uniform(-0.04, 0.04))
                      for i in range(n)]

    @property
    def params(self) -> tuple:
        return (self.length, self.seed, self.gap, self.height)

    def local_bounds(self) -> tuple[float, float, float, float]:
        return (-3.0, -self.height * 1.1, self.length + 3.0, 2.0)

    def draw_self(self, ctx: cairo.Context) -> None:
        # bayangan tipis di tanah
        colors.set_source(ctx, colors.SHADOW, 0.15)
        ctx.rectangle(0, 0, self.length, 3)
        ctx.fill()
        # palang melintang (di belakang tiang)
        for ry in (0.35, 0.72):
            y = -self.height * ry
            colors.set_source(ctx, colors.FENCE_DARK)
            ctx.rectangle(0, y - 1.5, self.length, 4.5)
            ctx.fill()
            colors.set_source(ctx, colors.FENCE_WOOD)
            ctx.rectangle(0, y - 1.5, self.length, 3.0)
            ctx.fill()
        for x, h, tilt in self.posts:
            ctx.save()
            ctx.translate(x, 0)
            ctx.rotate(tilt)
            ctx.move_to(-2.6, 0)
            ctx.line_to(-2.6, -h + 3)
            ctx.line_to(0, -h)            # ujung tiang runcing
            ctx.line_to(2.6, -h + 3)
            ctx.line_to(2.6, 0)
            ctx.close_path()
            colors.set_source(ctx, colors.FENCE_WOOD)
            ctx.fill_preserve()
            colors.set_source(ctx, colors.FENCE_DARK)
            ctx.set_line_width(0.7)
            ctx.stroke()
            ctx.restore()


# ====================================================================== semak
class BushNode(Node):
    """Semak dari lingkaran bertumpuk ber-seed. Origin = tengah dasar."""

    def __init__(self, seed: int = 0, size: float = 30.0, name: str = "Semak") -> None:
        super().__init__(name)
        self.seed, self.size = seed, size
        rng = random.Random(seed)
        self.blobs = [(rng.uniform(-0.5, 0.5) * size, -rng.uniform(0.2, 0.5) * size,
                       rng.uniform(0.28, 0.42) * size, rng.random()) for _ in range(6)]

    @property
    def params(self) -> tuple:
        return (self.seed, self.size)

    def local_bounds(self) -> tuple[float, float, float, float]:
        return (-self.size * 0.9, -self.size, self.size * 0.9, 2.0)

    def draw_self(self, ctx: cairo.Context) -> None:
        colors.set_source(ctx, colors.SHADOW, 0.2)
        ctx.save()
        ctx.scale(1.0, 0.25)
        ctx.arc(0, 0, self.size * 0.7, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
        for x, y, r, sh in sorted(self.blobs, key=lambda b: b[1], reverse=True):
            colors.set_source(ctx, colors.leaf_color(1.0, sh * 0.8))
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.fill_preserve()
            colors.set_source(ctx, colors.darken(colors.LEAF_HEALTHY, 0.4), 0.6)
            ctx.set_line_width(0.6)
            ctx.stroke()
            colors.set_source(ctx, colors.lighten(colors.LEAF_LIGHT, 0.3), 0.35)
            ctx.arc(x - r * 0.3, y - r * 0.35, r * 0.4, 0, 2 * math.pi)
            ctx.fill()


# ====================================================================== rumah kebun
def _window(ctx: cairo.Context, cx: float, cy: float, w: float, h: float) -> None:
    """Jendela berkaca dengan kilau (kaca di-clip ke bingkai)."""
    rounded_rect(ctx, cx - w / 2 - 2, cy - h / 2 - 2, w + 4, h + 4, 2)
    colors.set_source(ctx, colors.WINDOW_FRAME)
    ctx.fill()
    ctx.save()
    ctx.rectangle(cx - w / 2, cy - h / 2, w, h)
    ctx.clip()                          # [GRAFKOM] Clipping: kilau kaca tidak keluar bingkai
    grad = cairo.LinearGradient(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    grad.add_color_stop_rgb(0.0, *colors.GLASS_SHINE)
    grad.add_color_stop_rgb(1.0, *colors.GLASS)
    ctx.set_source(grad)
    ctx.paint()
    colors.set_source(ctx, colors.GLASS_SHINE, 0.55)
    ctx.move_to(cx - w * 0.1, cy - h / 2)
    ctx.line_to(cx + w * 0.3, cy - h / 2)
    ctx.line_to(cx - w * 0.3, cy + h / 2)
    ctx.line_to(cx - w * 0.7, cy + h / 2)
    ctx.close_path()
    ctx.fill()
    ctx.restore()
    colors.set_source(ctx, colors.WINDOW_FRAME)          # kayu silang
    ctx.set_line_width(1.2)
    ctx.move_to(cx, cy - h / 2)
    ctx.line_to(cx, cy + h / 2)
    ctx.move_to(cx - w / 2, cy)
    ctx.line_to(cx + w / 2, cy)
    ctx.stroke()


class FarmHouseNode(Node):
    """Rumah kebun (dekorasi). Origin = tengah dasar rumah."""

    def __init__(self, width: float = 112.0, wall_h: float = 58.0, name: str = "RumahKebun") -> None:
        super().__init__(name)
        self.width, self.wall_h = width, wall_h

    @property
    def params(self) -> tuple:
        return (self.width, self.wall_h)

    def local_bounds(self) -> tuple[float, float, float, float]:
        w = self.width / 2 + 10
        return (-w, -self.wall_h - 62, w, 2.0)

    def draw_self(self, ctx: cairo.Context) -> None:
        w, h = self.width / 2, self.wall_h
        # bayangan tanah
        colors.set_source(ctx, colors.SHADOW, 0.2)
        ctx.save()
        ctx.translate(6, 1)
        ctx.scale(1.0, 0.12)
        ctx.arc(0, 0, w * 1.25, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()

        # cerobong (di belakang atap)
        colors.set_source(ctx, colors.BRICK)
        ctx.rectangle(w * 0.35, -h - 48, 13, 36)
        ctx.fill()
        colors.set_source(ctx, colors.BRICK_DARK)
        ctx.rectangle(w * 0.35 - 2, -h - 51, 17, 5)
        ctx.fill()

        # dinding
        grad = cairo.LinearGradient(-w, 0, w, 0)
        grad.add_color_stop_rgb(0.0, *colors.WALL_HOUSE)
        grad.add_color_stop_rgb(1.0, *colors.WALL_HOUSE_SHADE)
        ctx.set_source(grad)
        ctx.rectangle(-w, -h, w * 2, h)
        ctx.fill_preserve()
        colors.set_source(ctx, colors.OUTLINE, 0.6)
        ctx.set_line_width(0.9)
        ctx.stroke()
        # pondasi batu
        colors.set_source(ctx, colors.STONE)
        ctx.rectangle(-w, -7, w * 2, 7)
        ctx.fill()

        # atap pelana
        ctx.move_to(-w - 11, -h + 2)
        ctx.line_to(0, -h - 44)
        ctx.line_to(w + 11, -h + 2)
        ctx.close_path()
        rg = cairo.LinearGradient(-w, -h - 44, w, -h)
        rg.add_color_stop_rgb(0.0, *colors.lighten(colors.ROOF_HOUSE, 0.12))
        rg.add_color_stop_rgb(1.0, *colors.ROOF_HOUSE_DARK)
        ctx.set_source(rg)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()                      # [GRAFKOM] Clipping: garis genteng dipotong bentuk atap
        colors.set_source(ctx, colors.ROOF_HOUSE_DARK, 0.55)
        ctx.set_line_width(0.8)
        for k in range(1, 6):
            y = -h - 44 + k * 8
            ctx.move_to(-w - 12, y)
            ctx.line_to(w + 12, y)
        ctx.stroke()
        ctx.restore()
        colors.set_source(ctx, colors.OUTLINE, 0.7)
        ctx.set_line_width(1.0)
        ctx.move_to(-w - 11, -h + 2)
        ctx.line_to(0, -h - 44)
        ctx.line_to(w + 11, -h + 2)
        ctx.stroke()

        # jendela loteng, pintu, jendela samping
        _window(ctx, 0, -h - 18, 11, 11)
        rounded_rect(ctx, -10, -34, 20, 34, 2)
        colors.set_source(ctx, colors.DOOR_WOOD)
        ctx.fill_preserve()
        colors.set_source(ctx, colors.OUTLINE, 0.7)
        ctx.set_line_width(0.8)
        ctx.stroke()
        colors.set_source(ctx, colors.UI_GOLD)
        ctx.arc(6, -17, 1.5, 0, 2 * math.pi)
        ctx.fill()
        _window(ctx, -w * 0.58, -h * 0.58, 17, 17)
        _window(ctx, w * 0.58, -h * 0.58, 17, 17)
        # undakan
        colors.set_source(ctx, colors.STONE)
        ctx.rectangle(-14, -2, 28, 4)
        ctx.fill()


# ====================================================================== pabrik
class FactoryNode(Node):
    """Cangkang pabrik pengolahan kopi. Origin = tengah dasar bangunan.

    Mesin & conveyor (Bagian B) di-add sebagai ANAK node ini, di dalam `hall_rect`
    (koordinat lokal x0, y0, x1, y1) -> sesuai scene graph: Pabrik -> Mesin x3.
    update(t) menganimasikan asap cerobong.
    """

    def __init__(self, width: float = 330.0, wall_h: float = 96.0, name: str = "Pabrik") -> None:
        super().__init__(name)
        self.width, self.wall_h = width, wall_h
        self.t = 0.0

    @property
    def params(self) -> tuple:
        return (self.width, self.wall_h)

    @property
    def hall_rect(self) -> tuple[float, float, float, float]:
        w, h = self.width / 2, self.wall_h
        return (-w * 0.74, -h * 0.74, w * 0.74, 0.0)

    def local_bounds(self) -> tuple[float, float, float, float]:
        w = self.width / 2
        return (-w - 4, -self.wall_h - 150, w + 4, 2.0)

    def update(self, t: float) -> None:
        self.t = t

    # ---------------------------------------------------------- bagian-bagian
    def _chimney(self, ctx: cairo.Context) -> None:
        w, h = self.width / 2, self.wall_h
        cx, top = w * 0.8, -h - 108
        ctx.move_to(cx - 14, -h)
        ctx.line_to(cx - 10, top)
        ctx.line_to(cx + 10, top)
        ctx.line_to(cx + 14, -h)
        ctx.close_path()
        g = cairo.LinearGradient(cx - 14, 0, cx + 14, 0)
        g.add_color_stop_rgb(0.0, *colors.BRICK)
        g.add_color_stop_rgb(1.0, *colors.BRICK_DARK)
        ctx.set_source(g)
        ctx.fill()
        colors.set_source(ctx, colors.BRICK_DARK, 0.7)       # garis bata
        ctx.set_line_width(0.7)
        y = -h - 8
        while y > top + 6:
            ctx.move_to(cx - 14, y)
            ctx.line_to(cx + 14, y)
            y -= 9
        ctx.stroke()
        colors.set_source(ctx, colors.STONE)                  # bibir cerobong
        ctx.rectangle(cx - 13, top - 5, 26, 6)
        ctx.fill()

    def _smoke(self, ctx: cairo.Context) -> None:
        """[GRAFKOM] Transformasi 2D + Compositing: asap naik, membesar, memudar (alpha)."""
        w, h = self.width / 2, self.wall_h
        cx, top = w * 0.8, -h - 116
        for i in range(6):
            p = (self.t * 0.22 + i / 6) % 1.0
            x = cx + math.sin(p * 5 + i) * 7 + p * 34
            y = top - p * 85
            r = 6 + p * 15
            colors.set_source(ctx, colors.SMOKE, 0.75 * (1 - p) ** 1.4)
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.fill()

    def _roof(self, ctx: cairo.Context) -> None:
        """Atap gerigi (sawtooth): sisi miring gelap + strip kaca terang."""
        w, h = self.width / 2, self.wall_h
        n = 4
        tw = self.width / n
        for i in range(n):
            x0 = -w + i * tw
            ctx.move_to(x0, -h)
            ctx.line_to(x0, -h - 36)          # sisi tegak (kaca)
            ctx.line_to(x0 + tw, -h)
            ctx.close_path()
            g = cairo.LinearGradient(x0, -h - 36, x0 + tw, -h)
            g.add_color_stop_rgb(0.0, *colors.FACTORY_ROOF_LIGHT)
            g.add_color_stop_rgb(1.0, *colors.FACTORY_ROOF)
            ctx.set_source(g)
            ctx.fill_preserve()
            colors.set_source(ctx, colors.OUTLINE, 0.6)
            ctx.set_line_width(0.9)
            ctx.stroke()
            # kaca vertikal
            colors.set_source(ctx, colors.GLASS, 0.9)
            ctx.rectangle(x0 - 1.2, -h - 35, 2.4, 33)
            ctx.fill()
        colors.set_source(ctx, colors.FACTORY_ROOF)
        ctx.rectangle(-w - 3, -h - 3, self.width + 6, 5)
        ctx.fill()

    def draw_self(self, ctx: cairo.Context) -> None:
        w, h = self.width / 2, self.wall_h
        hx0, hy0, hx1, _ = self.hall_rect

        colors.set_source(ctx, colors.SHADOW, 0.22)       # bayangan tanah
        ctx.save()
        ctx.translate(10, 2)
        ctx.scale(1.0, 0.08)
        ctx.arc(0, 0, w * 1.1, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()

        self._chimney(ctx)
        self._smoke(ctx)

        # dinding depan
        g = cairo.LinearGradient(0, -h, 0, 0)
        g.add_color_stop_rgb(0.0, *colors.FACTORY_WALL)
        g.add_color_stop_rgb(1.0, *colors.FACTORY_WALL_SHADE)
        ctx.set_source(g)
        ctx.rectangle(-w, -h, w * 2, h)
        ctx.fill_preserve()
        colors.set_source(ctx, colors.OUTLINE, 0.65)
        ctx.set_line_width(1.0)
        ctx.stroke()
        colors.set_source(ctx, colors.BRICK_DARK)         # sabuk bata di kaki dinding
        ctx.rectangle(-w, -9, w * 2, 9)
        ctx.fill()

        self._roof(ctx)

        # papan nama di atas aula
        sw = 126.0
        rounded_rect(ctx, -sw / 2, hy0 - 30, sw, 22, 4)
        colors.set_source(ctx, colors.FACTORY_SIGN)
        ctx.fill_preserve()
        colors.set_source(ctx, colors.UI_GOLD)
        ctx.set_line_width(1.2)
        ctx.stroke()
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13)
        text = "PABRIK KOPI"
        ext = ctx.text_extents(text)
        colors.set_source(ctx, colors.UI_TEXT_LIGHT)
        ctx.move_to(-ext.x_advance / 2, hy0 - 14)
        ctx.show_text(text)

        # bukaan aula: interior gelap (mesin B digambar di atasnya sebagai anak)
        ctx.rectangle(hx0, hy0, hx1 - hx0, -hy0)
        ig = cairo.LinearGradient(0, hy0, 0, 0)
        ig.add_color_stop_rgb(0.0, *colors.darken(colors.FACTORY_INTERIOR, 0.25))
        ig.add_color_stop_rgb(1.0, *colors.lighten(colors.FACTORY_INTERIOR, 0.12))
        ctx.set_source(ig)
        ctx.fill_preserve()
        colors.set_source(ctx, colors.OUTLINE, 0.8)
        ctx.set_line_width(2.0)
        ctx.stroke()
        # lantai aula
        colors.set_source(ctx, colors.STONE, 0.8)
        ctx.rectangle(hx0, -6, hx1 - hx0, 6)
        ctx.fill()

        # jendela di sisi kiri-kanan aula
        for sx in (-1, 1):
            wx = sx * (hx1 + (w - hx1) / 2)
            _window(ctx, wx, -h * 0.5, 18, 22)
