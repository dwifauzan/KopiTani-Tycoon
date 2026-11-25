# Bagian C — Gambar Tanaman & Tampilan

Isi folder ini hanya file Bagian C. Cara pakai: ekstrak ZIP di root repo (gabung dengan folder `graphics/` dan `tests/` yang sudah ada).

## File yang dibuat

| File | Isi |
| --- | --- |
| `graphics/colors.py` | Semua palet warna + color blending (`lerp_color`, `gradient_color`, `cherry_color`, `bean_color`, `leaf_color`) |
| `graphics/procedural/coffee_tree.py` | Generator pohon kopi 4 tahap (ber-seed) + ayunan angin |
| `graphics/procedural/leaf.py` | Daun dari 2 kurva Bezier |
| `graphics/procedural/cherry.py` | Ceri (hijau→kuning→merah), bunga, pembuat cluster |
| `graphics/procedural/soil.py` | Tanah: kerikil + retakan ber-seed, kering/basah |
| `graphics/procedural/sacks.py` | Karung dengan jendela level isi (clipping) + tumpukan dari volume |
| `graphics/procedural/scenery.py` | Langit + matahari, awan melayang, bukit berlapis, pagar, semak, **rumah kebun**, **cangkang pabrik** (atap gerigi, cerobong berasap, aula untuk mesin B) |
| `graphics/objects/ui_panel.py` | `PanelNode` (panel data: nilai + sumber, label DUMMY) dan `BadgeNode` (saldo) |
| `graphics/node.py` | **Versi minimal sesuai AGENTS.md** agar Bagian C bisa jalan sendiri. Kalau Bagian B sudah punya `node.py`, pakai punya B |
| `tests/test_procedural.py` | 30 test |
| `tools/preview_bagian_c.py` | Pratinjau close-up (4 tahap, warna, karung, UI) + benchmark fps. Hasil PNG-nya (`preview_bagian_c.png`) dibuat saat dijalankan |
| `tools/preview_scene_c.py` | Mockup scene penuh (latar, rumah, pabrik, kebun 3x3, UI) |
| `preview_scene_c.png` | Hasil mockup scene penuh (bahan laporan/proposal) |

## Cara pakai (untuk Bagian A & B)

```python
from graphics.procedural.coffee_tree import build_coffee_tree
from graphics.procedural.soil import SoilNode
from graphics.procedural.sacks import SacksPile
from graphics.objects.ui_panel import PanelNode, BadgeNode

# satu petak
petak = Node("Petak")
petak.add(SoilNode(width=120, height=44, seed=slot_id, moisture=0.4))
pohon = build_coffee_tree(seed=slot_id, stage=3, vigor=0.8)   # stage 1..4, vigor 0..1
petak.add(pohon)

# tiap frame (animasi angin):
pohon.update(waktu_detik)

# state berubah (stage/vigor baru) -> bangun ulang pohonnya dengan seed yang SAMA
# supaya bentuk tidak berubah mendadak.

pohon.cherries()            # daftar CherryNode (cek .ripeness untuk panen & grade)
build_coffee_tree(seed, 4, vigor, ripeness=0.9)   # paksa kematangan ceri dari state game

# latar & bangunan
pabrik = FactoryNode(); pabrik.update(t)      # asap bergerak
x0, y0, x1, y1 = pabrik.hall_rect             # taruh Mesin x3 (Bagian B) sebagai ANAK pabrik di area ini
pabrik.add(mesin_sortir)                      # Pabrik -> Mesin -> Rangka -> RodaGigi/Drum/Corong
SkyNode(); CloudNode(seed=1).update(t); HillsNode(seed=4); FenceNode(230, seed=2)
FarmHouseNode(); BushNode(seed=1)             # dekorasi saja (bukan fitur game)

SacksPile(volume_kg=150, kg_per_sack=60, roast=0.66, seed=1)  # kg_per_sack ambil dari data/CONFIG
PanelNode(220, "Data: Jember - Juli", [("Curah hujan", "210 mm")], source="BMKG")
```

Catatan:
- Jangan membuat pohon baru tiap frame; simpan objeknya dan panggil `update(t)`.
- Origin pohon = pangkal batang di tanah (tumbuh ke arah -y). Taruh node pohon di titik tengah petak.
- Node hasil Bagian C punya `local_bounds()` (x0, y0, x1, y1) untuk mode debug F9 / hit-test.
- Angka kg per karung dan semua angka data **tidak** ditulis di sini; kirim dari `formulas.py`/data.

## Peta teknik grafika → file

Cari dengan `grep -rn "\[GRAFKOM\]" graphics/`.

| Teknik | Lokasi |
| --- | --- |
| Scene graph (hierarki pohon) | `coffee_tree.py` (Pohon → Batang → Cabang → Daun/Ceri), `sacks.py` (Tumpukan → Karung) |
| Procedural modeling | `coffee_tree.py`, `soil.py`, `sacks.py`, `cherry.py` (semua `random.Random(seed)`) |
| Transformasi 2D | skala pohon per tahap & ayunan cabang (`coffee_tree.py`), rotasi kelopak (`cherry.py`) |
| Color blending | `colors.py`, warna ceri `cherry.py`, biji `sacks.py`, tanah `soil.py` |
| Path & complex shapes | `leaf.py`, `cherry.py`, `sacks.py`, `ui_panel.py` |
| Clipping & masking | level isi karung `sacks.py`, tekstur tanah `soil.py`, header panel `ui_panel.py` |
| Compositing | cahaya matahari, asap pabrik (alpha memudar) di `scenery.py`; keteduhan kanopi/bayangan di `coffee_tree.py`; bayangan panel di `ui_panel.py` |

## Menjalankan

```bash
pip install pycairo pytest
pytest                                 # 30 test
python tools/preview_bagian_c.py       # close-up + benchmark
python tools/preview_scene_c.py        # mockup scene penuh
```

## Yang belum / perlu dicek tim

- **fps**: belum diukur dengan pycairo asli (lingkungan pembuatan hanya punya pengganti yang lebih lambat). Jalankan `tools/preview_bagian_c.py` di laptop kalian; target ≥ 15 fps untuk 9 pohon + 3 mesin.
- Pohon sekarang lebih lebat (±45% lebih banyak node dari versi awal) sehingga lebih berat; kalau fps kurang, kurangi `n_pairs` di `_decorate_branch` (coffee_tree.py).
- `vigor` harus dikirim dari rumus pertumbuhan Bagian A (`formulas.py`).
- Bagian proposal (Bab II & mockup) tidak dibuat di sini; `preview_bagian_c.png` bisa jadi bahan mockup.
