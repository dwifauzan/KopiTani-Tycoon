"""Generator pohon kopi prosedural (ber-seed).

Struktur scene graph hasil generator:

    PohonKopi              <- scale per tahap tumbuh
    └── Batang
        ├── Cabang x (2 * n_ruas)   <- rotate: ayunan angin
        │   ├── Daun ...
        │   └── ClusterBunga (tahap 3) / ClusterCeri (tahap 4)
        └── Daun mahkota

Semua acak memakai `random.Random(seed)` (BUKAN random global), sehingga
seed sama -> pohon identik di setiap frame.
"""
from __future__ import annotations

import math
import random
from typing import Iterator

import cairo

from graphics import colors
from graphics.node import Node
from graphics.procedural.cherry import make_cherry_cluster, make_flower_cluster
from graphics.procedural.leaf import LeafNode

# --------------------------------------------------- parameter VISUAL (bukan data)
# Hanya mengatur bentuk gambar. Angka agronomi (laju tumbuh, dll.) ada di formulas.py.
TRUNK_HEIGHT = 110.0
STAGE_SCALE = {1: 0.5, 2: 0.7, 3: 0.9, 4: 1.0}       # [GRAFKOM] skala per tahap
STAGE_TRUNK = {1: 0.6, 2: 0.8, 3: 0.95, 4: 1.0}
STAGE_BRANCH = {1: 0.6, 2: 0.8, 3: 1.0, 4: 1.0}
BRANCH_BASE_LENGTH = 72.0
BRANCH_ANGLE_DEG = (55.0, 75.0)      # sudut cabang terhadap batang
BRANCH_ANGLE_JITTER_DEG = 4.0
WIND_AMPLITUDE = 0.05                # radian, maksimum di ujung atas


def n_ruas_for_stage(stage: int) -> int:
    """Jumlah ruas batang = 2 + stage * 2."""
    return 2 + stage * 2


def walk(node: Node) -> Iterator[Node]:
    """Telusuri semua node (pre-order)."""
    yield node
    for c in node.children:
        yield from walk(c)


class TrunkNode(Node):
    """Batang tegak meruncing. Origin = pangkal batang, tumbuh ke -y."""

    def __init__(self, height: float, base_width: float = 8.0, top_width: float = 3.5) -> None:
        super().__init__("Batang")
        self.height = height
        self.base_width = base_width
        self.top_width = top_width

    @property
    def params(self) -> tuple:
        return (round(self.height, 3), self.base_width, self.top_width)

    def draw_self(self, ctx: cairo.Context) -> None:
        bw, tw, h = self.base_width / 2, self.top_width / 2, self.height
        ctx.move_to(-bw, 0)
        ctx.line_to(-tw, -h)
        ctx.line_to(tw, -h)
        ctx.line_to(bw, 0)
        ctx.close_path()
        grad = cairo.LinearGradient(-bw, 0, bw, 0)
        grad.add_color_stop_rgb(0.0, *colors.TRUNK_DARK)
        grad.add_color_stop_rgb(0.5, *colors.TRUNK_LIGHT)
        grad.add_color_stop_rgb(1.0, *colors.TRUNK_DARK)
        ctx.set_source(grad)
        ctx.fill_preserve()
        colors.set_source(ctx, colors.OUTLINE, 0.6)
        ctx.set_line_width(0.6)
        ctx.stroke()


class BranchNode(Node):
    """Cabang lateral. Origin = titik tempel di batang, tumbuh ke -y lokal.

    `rotation` = base_rotation + ayunan angin (diatur oleh CoffeeTreeNode.update).
    """

    def __init__(self, length: float, side: int, base_rotation: float, amp: float,
                 freq: float, phase: float) -> None:
        super().__init__("Cabang")
        self.length = length
        self.side = side                  # -1 kiri, +1 kanan
        self.base_rotation = base_rotation
        self.amp = amp
        self.freq = freq
        self.phase = phase
        self.rotation = base_rotation

    @property
    def params(self) -> tuple:
        return (round(self.length, 3), self.side, round(self.base_rotation, 4),
                round(self.amp, 4), round(self.freq, 4), round(self.phase, 4))

    def sway(self, t: float) -> None:
        """[GRAFKOM] Transformasi 2D: ayunan angin, rotation = amp * sin(t*freq + phase)."""
        self.rotation = self.base_rotation + self.amp * math.sin(t * self.freq + self.phase)

    def draw_self(self, ctx: cairo.Context) -> None:
        w0, w1 = 1.8, 0.6
        ctx.move_to(-w0, 0)
        ctx.line_to(-w1, -self.length)
        ctx.line_to(w1, -self.length)
        ctx.line_to(w0, 0)
        ctx.close_path()
        colors.set_source(ctx, colors.TRUNK_LIGHT)
        ctx.fill_preserve()
        colors.set_source(ctx, colors.OUTLINE, 0.5)
        ctx.set_line_width(0.4)
        ctx.stroke()


class CoffeeTreeNode(Node):
    """Akar pohon kopi. Origin = pangkal batang di tanah (tumbuh ke -y)."""

    def __init__(self, seed: int, stage: int, vigor: float) -> None:
        super().__init__("PohonKopi")
        self.seed = seed
        self.stage = stage
        self.vigor = vigor
        self.branches: list[BranchNode] = []
        self.sx = self.sy = STAGE_SCALE[stage]

    @property
    def params(self) -> tuple:
        return (self.seed, self.stage, round(self.vigor, 3))

    def local_bounds(self) -> tuple[float, float, float, float]:
        """Kotak perkiraan (koordinat lokal, sebelum skala) untuk hit-test / debug."""
        return (-80.0, -TRUNK_HEIGHT - 30.0, 80.0, 0.0)

    def update(self, t: float) -> None:
        """Perbarui ayunan angin semua cabang pada waktu `t` (detik)."""
        for b in self.branches:
            b.sway(t)

    def cherries(self) -> list[Node]:
        return [n for n in walk(self) if n.__class__.__name__ == "CherryNode"]


def build_coffee_tree(seed: int, stage: int, vigor: float = 1.0,
                      ripeness: float | None = None) -> CoffeeTreeNode:
    """Bangun pohon kopi prosedural.

    seed     : menentukan bentuk (sama -> identik).
    stage    : 1 bibit, 2 muda, 3 berbunga, 4 berbuah.
    vigor    : 0..1 (dari rumus pertumbuhan) -> warna/ukuran daun & jumlah bunga/ceri.
    ripeness : None = ceri campuran hijau-kuning-merah; angka 0..1 = semua ceri
               sekitar nilai itu (mis. dari state game).
    """
    if stage not in STAGE_SCALE:
        raise ValueError(f"stage harus 1..4, bukan {stage!r}")
    vigor = colors.clamp01(vigor)
    rng = random.Random(seed)   # [GRAFKOM] Procedural modeling: semua acak ber-seed

    tree = CoffeeTreeNode(seed, stage, vigor)
    trunk_h = TRUNK_HEIGHT * STAGE_TRUNK[stage]
    trunk = tree.add(TrunkNode(trunk_h))
    n_ruas = n_ruas_for_stage(stage)
    leaf_size = 0.8 + 0.2 * vigor

    for i in range(n_ruas):
        frac = 0.12 + 0.8 * i / (n_ruas - 1)           # posisi ruas di batang (0..1)
        for side in (-1, +1):
            angle = math.radians(rng.uniform(*BRANCH_ANGLE_DEG)
                                 + rng.uniform(-BRANCH_ANGLE_JITTER_DEG, BRANCH_ANGLE_JITTER_DEG))
            length = (BRANCH_BASE_LENGTH * STAGE_BRANCH[stage] * (1.0 - 0.65 * frac)
                      * rng.uniform(0.9, 1.1))           # mengecil ke atas
            branch = BranchNode(
                length=length, side=side, base_rotation=side * angle,
                amp=WIND_AMPLITUDE * (0.4 + 0.6 * frac) * rng.uniform(0.8, 1.2),
                freq=rng.uniform(1.2, 2.0), phase=rng.uniform(0, 2 * math.pi))
            branch.tx, branch.ty = 0.0, -trunk_h * frac
            trunk.add(branch)
            tree.branches.append(branch)
            _decorate_branch(branch, rng, stage, vigor, ripeness, leaf_size)

    _add_crown(trunk, rng, trunk_h, vigor, leaf_size)
    tree.update(0.0)
    return tree


def _decorate_branch(branch: BranchNode, rng: random.Random, stage: int, vigor: float,
                     ripeness: float | None, leaf_size: float) -> None:
    """Pasang daun berpasangan, lalu bunga (tahap 3) atau ceri (tahap 4)."""
    length = branch.length
    n_pairs = max(2, min(4, int(length / 17)))
    for k in range(n_pairs):
        s = 0.3 + 0.6 * k / max(1, n_pairs - 1)          # posisi sepanjang cabang
        for leaf_side in (-1, +1):
            ln = 19.0 * leaf_size * (1.0 - 0.3 * s) * rng.uniform(0.9, 1.1)
            leaf = LeafNode(ln, ln * 0.42, colors.leaf_color(vigor, rng.random()))
            leaf.tx, leaf.ty = 0.0, -length * s
            leaf.rotation = leaf_side * math.radians(rng.uniform(55, 80))
            branch.add(leaf)
    tip_len = 17.0 * leaf_size * rng.uniform(0.9, 1.1)      # daun di ujung cabang
    tip = LeafNode(tip_len, tip_len * 0.42, colors.leaf_color(vigor, rng.random()))
    tip.ty = -length
    branch.add(tip)

    if stage < 3:
        return
    count = max(0, round(rng.randint(3, 6) * vigor))      # jumlah dikali vigor
    if count == 0:
        return
    if stage == 3:
        cluster = make_flower_cluster(rng, count)
    else:
        cluster = make_cherry_cluster(rng, count, ripeness)
    cluster.tx, cluster.ty = 0.0, -length * rng.uniform(0.4, 0.75)   # di ketiak daun
    cluster.rotation = -branch.base_rotation                # menggantung ke bawah
    branch.add(cluster)


def _add_crown(trunk: TrunkNode, rng: random.Random, trunk_h: float, vigor: float,
               leaf_size: float) -> None:
    """3 daun di pucuk batang."""
    for ang in (-30.0, 0.0, 30.0):
        ln = 18.0 * leaf_size * rng.uniform(0.9, 1.1)
        leaf = LeafNode(ln, ln * 0.42, colors.leaf_color(vigor, rng.random()), name="DaunPucuk")
        leaf.ty = -trunk_h
        leaf.rotation = math.radians(ang + rng.uniform(-6, 6))
        trunk.add(leaf)


def describe_tree(node: Node) -> tuple:
    """Ringkasan struktur node (untuk perbandingan/test): seed sama -> hasil sama."""
    return (
        node.__class__.__name__, node.name,
        round(node.tx, 4), round(node.ty, 4), round(node.rotation, 4),
        round(node.sx, 4), round(node.sy, 4),
        getattr(node, "params", ()),
        tuple(describe_tree(c) for c in node.children),
    )
