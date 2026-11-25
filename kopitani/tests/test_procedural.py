"""Test Bagian C: generator prosedural, color blending, objek UI."""
import math
import random

import cairo

from graphics import colors
from graphics.node import Node
from graphics.objects.ui_panel import BadgeNode, PanelNode
from graphics.procedural.cherry import CherryNode, FlowerNode
from graphics.procedural.coffee_tree import (
    STAGE_SCALE, build_coffee_tree, describe_tree, n_ruas_for_stage, walk)
from graphics.procedural.leaf import LeafNode
from graphics.procedural.sacks import MAX_SACKS, SacksPile, sacks_from_volume
from graphics.procedural.soil import SoilNode


def count(root, cls_name):
    return sum(1 for n in walk(root) if n.__class__.__name__ == cls_name)


def render_ok(node):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 300)
    ctx = cairo.Context(surf)
    node.tx, node.ty = 150, 250
    node.render(ctx)


# ------------------------------------------------------------ pohon
def test_seed_sama_identik():
    for stage in (1, 2, 3, 4):
        a = describe_tree(build_coffee_tree(42, stage, 0.8))
        b = describe_tree(build_coffee_tree(42, stage, 0.8))
        assert a == b


def test_seed_beda_bentuk_beda():
    a = describe_tree(build_coffee_tree(1, 4, 1.0))
    b = describe_tree(build_coffee_tree(2, 4, 1.0))
    assert a != b


def test_tidak_memakai_random_global():
    state = random.getstate()
    build_coffee_tree(7, 4, 1.0)
    assert random.getstate() == state


def test_jumlah_cabang_sesuai_stage():
    for stage in (1, 2, 3, 4):
        tree = build_coffee_tree(5, stage, 1.0)
        assert n_ruas_for_stage(stage) == 2 + stage * 2
        assert len(tree.branches) == 2 * n_ruas_for_stage(stage)
        assert count(tree, "BranchNode") == len(tree.branches)


def test_cabang_sepasang_kiri_kanan():
    tree = build_coffee_tree(5, 3, 1.0)
    assert sum(1 for b in tree.branches if b.side == -1) == sum(1 for b in tree.branches if b.side == 1)


def test_sudut_dan_panjang_cabang():
    tree = build_coffee_tree(11, 4, 1.0)
    for b in tree.branches:
        deg = abs(math.degrees(b.base_rotation))
        assert 50.0 <= deg <= 80.0
        assert (b.base_rotation > 0) == (b.side > 0)
    right = [b for b in tree.branches if b.side == 1]
    ys = [-b.ty for b in right]            # makin tinggi ...
    assert ys == sorted(ys)
    assert right[-1].length < right[0].length   # ... makin pendek


def test_ceri_hanya_di_stage_4():
    for stage in (1, 2, 3):
        assert count(build_coffee_tree(3, stage, 1.0), "CherryNode") == 0
    assert count(build_coffee_tree(3, 4, 1.0), "CherryNode") > 0


def test_bunga_hanya_di_stage_3():
    for stage in (1, 2, 4):
        assert count(build_coffee_tree(3, stage, 1.0), "FlowerNode") == 0
    assert count(build_coffee_tree(3, 3, 1.0), "FlowerNode") > 0


def test_vigor_mempengaruhi_jumlah_ceri():
    assert count(build_coffee_tree(3, 4, 0.0), "CherryNode") == 0
    low = count(build_coffee_tree(3, 4, 0.3), "CherryNode")
    high = count(build_coffee_tree(3, 4, 1.0), "CherryNode")
    assert 0 < low < high


def test_skala_membesar_per_tahap():
    scales = [build_coffee_tree(1, s).sx for s in (1, 2, 3, 4)]
    assert scales == sorted(scales) and len(set(scales)) == 4
    assert scales == [STAGE_SCALE[s] for s in (1, 2, 3, 4)]


def test_cabang_berayun_dan_deterministik():
    tree = build_coffee_tree(9, 4, 1.0)
    tree.update(0.0)
    r0 = [b.rotation for b in tree.branches]
    tree.update(0.7)
    r1 = [b.rotation for b in tree.branches]
    assert r0 != r1
    tree.update(0.7)
    assert r1 == [b.rotation for b in tree.branches]
    for b in tree.branches:       # ayunan tidak melebihi amplitudo
        assert abs(b.rotation - b.base_rotation) <= b.amp + 1e-9


def test_ripeness_dipaksa():
    tree = build_coffee_tree(3, 4, 1.0, ripeness=1.0)
    assert all(c.ripeness >= 0.9 for c in tree.cherries())
    tree = build_coffee_tree(3, 4, 1.0, ripeness=0.0)
    assert all(c.ripeness <= 0.1 for c in tree.cherries())


def test_stage_tidak_valid():
    try:
        build_coffee_tree(1, 5)
    except ValueError:
        return
    raise AssertionError("harus ValueError")


def test_render_semua_stage():
    for stage in (1, 2, 3, 4):
        render_ok(build_coffee_tree(1, stage, 0.7))


# ------------------------------------------------------------ warna
def test_lerp_color_ujung_dan_clamp():
    a, b = (0.0, 0.0, 0.0), (1.0, 0.5, 0.2)
    assert colors.lerp_color(a, b, 0) == a
    assert colors.lerp_color(a, b, 1) == b
    assert colors.lerp_color(a, b, -5) == a
    assert colors.lerp_color(a, b, 9) == b
    assert colors.lerp_color(a, b, 0.5) == (0.5, 0.25, 0.1)


def test_cherry_color_hijau_kuning_merah():
    assert colors.cherry_color(0.0) == colors.CHERRY_GREEN
    assert colors.cherry_color(0.5) == colors.CHERRY_YELLOW
    assert colors.cherry_color(1.0) == colors.CHERRY_RED
    r, g, _ = colors.cherry_color(1.0)
    assert r > g
    _, g0, _ = colors.cherry_color(0.0)
    assert g0 > colors.cherry_color(1.0)[1]


def test_bean_color_makin_gelap():
    lum = [sum(colors.bean_color(t / 10)) for t in range(11)]
    assert lum == sorted(lum, reverse=True)
    assert colors.bean_color(0.0) == colors.BEAN_GREEN
    assert colors.bean_color(1.0) == colors.BEAN_DARK


def test_semua_warna_valid():
    for name in dir(colors):
        v = getattr(colors, name)
        if name.isupper() and isinstance(v, tuple) and len(v) == 3 and isinstance(v[0], float):
            assert all(0.0 <= c <= 1.0 for c in v), name


# ------------------------------------------------------------ tanah, karung
def test_tanah_deterministik():
    a, b = SoilNode(seed=4), SoilNode(seed=4)
    assert a.pebbles == b.pebbles and a.cracks == b.cracks
    assert SoilNode(seed=5).pebbles != a.pebbles
    for x, y, *_ in a.pebbles:    # kerikil di dalam elips
        assert (x / (a.width / 2)) ** 2 + (y / (a.height / 2)) ** 2 <= 1.0


def test_tanah_render_basah_dan_kering():
    render_ok(SoilNode(seed=1, moisture=0.0))
    render_ok(SoilNode(seed=1, moisture=1.0))


def test_sacks_from_volume():
    assert sacks_from_volume(0, 60) == (0, 0.0)
    assert sacks_from_volume(120, 60) == (2, 1.0)
    n, fill = sacks_from_volume(150, 60)
    assert n == 3 and abs(fill - 0.5) < 1e-9
    assert sacks_from_volume(99999, 60) == (MAX_SACKS, 1.0)


def test_tumpukan_karung():
    pile = SacksPile(volume_kg=150, kg_per_sack=60, seed=1)
    assert len(pile.children) == 3 == pile.n_sacks
    assert abs(pile.children[-1].fill - 0.5) < 1e-9
    assert describe_tree(pile) == describe_tree(SacksPile(volume_kg=150, kg_per_sack=60, seed=1))
    assert len(SacksPile(volume_kg=0).children) == 0
    render_ok(pile)
    render_ok(SacksPile(volume_kg=9999, roast=0.2))


# ------------------------------------------------------------ daun, ceri, UI
def test_node_dasar_dirender():
    for n in (LeafNode(), CherryNode(ripeness=0.5), FlowerNode()):
        render_ok(n)


def test_ceri_warna_ikut_kematangan():
    assert CherryNode(ripeness=0.0).color == colors.CHERRY_GREEN
    assert CherryNode(ripeness=1.0).color == colors.CHERRY_RED
    assert CherryNode(ripeness=5.0).ripeness == 1.0


def test_panel_dan_lencana():
    p = PanelNode(title="Data", rows=[("Curah hujan", "210 mm"), ("Suhu", "26 C")], source="BMKG")
    assert p.height > PanelNode(title="x").height
    render_ok(p)
    render_ok(PanelNode(title="x", rows=[("a", "b")], is_dummy=True))
    render_ok(BadgeNode("Rp 120.000"))


def test_hirarki_transformasi_anak_ikut_induk():
    tree = build_coffee_tree(1, 2)
    before = tree.children[0].tx
    tree.tx = 100
    assert tree.children[0].tx == before      # transformasi anak tetap lokal
