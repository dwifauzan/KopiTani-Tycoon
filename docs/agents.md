# AGENTS.md — KopiTani Tycoon

Panduan kerja untuk AI coding agent (Claude Code, Codex, Cursor, dll.) yang membangun proyek ini.
Baca seluruh file ini sebelum menulis kode. Jika ada instruksi user yang bertentangan dengan file ini, tanyakan dulu ke user.

---

## 1. Ringkasan Proyek

**KopiTani Tycoon** adalah game edukasi 2D berbasis web tentang budidaya dan pengolahan pascapanen kopi.
Pemain menanam kopi, merawat, memanen ceri, lalu mengolahnya lewat mesin (sortasi → pulper + jemur → roasting) dan menjualnya.
Parameter game (laju tumbuh, lama jemur, harga) berasal dari **data nyata** (BMKG, BPS, Kementan).

Ini adalah **Final Project mata kuliah Grafika Komputer**. Penilaian utama ada di penerapan konsep grafika, bukan di kompleksitas gameplay.

### Syarat wajib dari dosen (TIDAK BOLEH dilanggar)

1. **Pycairo wajib** dipakai untuk membentuk dan merender objek grafis.
2. **Hierarchical Modeling / Scene Graph** wajib diterapkan.
3. **Procedural Modeling** wajib diterapkan.
4. Minimal **2 materi grafika lain**: transformasi 2D, color blending, path & complex shapes, clipping & masking, compositing.
5. Memakai **data nyata** yang sumbernya jelas.
6. Platform: **website**.
7. Tema: **pertanian industrial / agroindustri**.

---

## 2. Tech Stack

| Bagian | Teknologi |
| --- | --- |
| Bahasa backend | Python 3.11+ |
| Rendering | **Pycairo** (`cairo.ImageSurface`, `cairo.Context`) |
| Web server | Flask + `flask-sock` (WebSocket) |
| Frontend | HTML + CSS + JavaScript murni (tanpa framework) |
| Data | CSV / JSON lokal di folder `data/` |
| Testing | `pytest` |

Jangan menambah library besar (React, Pygame, Three.js, Phaser, PIL untuk menggambar, dll.) tanpa izin user.

---

## 3. Arsitektur

```
Browser (HTML + JS)                Server Python (Flask)                     Data lokal
┌──────────────────┐   klik/WS    ┌──────────────────────────┐   load    ┌───────────────┐
│ <img>/<canvas>   │ ───────────► │ Game logic + data loader │ ◄──────── │ CSV / JSON    │
│ tampilkan frame  │              │ Generator prosedural     │           │ BMKG/BPS/...  │
│ kirim input      │ ◄─────────── │ Scene graph (Node)       │           └───────────────┘
└──────────────────┘  frame PNG   │ Renderer Pycairo         │
                                  └──────────────────────────┘
```

- **Semua gambar dibuat oleh Pycairo di server.** Frontend hanya menampilkan PNG dan mengirim input.
- Frontend **tidak boleh** menggambar objek game sendiri (tidak ada `ctx.arc`, `ctx.fillRect` untuk objek game di JS). JS hanya boleh `drawImage` frame dari server.
- Resolusi kanvas: **960×540**. Target **≥ 15 fps** saat animasi, turun ke render-saat-berubah saja ketika idle.

### Protokol WebSocket

Client → Server (JSON):
```json
{ "type": "click", "x": 412, "y": 233 }
{ "type": "select_region", "region_id": "jember", "month": 7 }
{ "type": "toggle_debug" }
```

Server → Client:
- Frame: pesan **binary** berisi PNG.
- State ringkas (JSON, opsional untuk UI HTML): `{ "type": "state", "saldo": 12000, "hari": 14 }`

---

## 4. Struktur Folder

```
kopitani/
├── AGENTS.md
├── README.md
├── requirements.txt
├── app.py                    # entry Flask + WebSocket
├── game/
│   ├── __init__.py
│   ├── state.py              # GameState: saldo, hari, slot, inventori
│   ├── logic.py              # aturan tanam, tumbuh, panen, olah, jual
│   ├── formulas.py           # semua rumus (laju tumbuh, grade, harga)
│   └── data_loader.py        # baca & validasi CSV/JSON
├── graphics/
│   ├── __init__.py
│   ├── node.py               # kelas Node (scene graph)
│   ├── scene.py              # bangun pohon scene dari GameState
│   ├── renderer.py           # traversal + render ke PNG
│   ├── colors.py             # palet & fungsi color blending
│   ├── procedural/
│   │   ├── coffee_tree.py    # generator pohon kopi
│   │   ├── leaf.py           # bentuk daun (Bézier)
│   │   ├── cherry.py         # ceri + warna
│   │   ├── soil.py           # tekstur tanah
│   │   └── sacks.py          # tumpukan karung/biji
│   └── objects/
│       ├── machine_sorter.py
│       ├── machine_pulper.py
│       ├── machine_roaster.py
│       ├── conveyor.py
│       └── ui_panel.py
├── data/
│   ├── raw/                  # file asli dari portal (jangan diedit)
│   ├── processed/            # hasil pembersihan yang dipakai game
│   └── SOURCES.md            # identitas tiap dataset
├── static/
│   ├── index.html
│   ├── main.js
│   └── style.css
└── tests/
    ├── test_node.py
    ├── test_procedural.py
    ├── test_formulas.py
    └── test_data_loader.py
```

---

## 5. Spesifikasi Inti

### 5.1 Scene Graph (`graphics/node.py`)

```python
class Node:
    name: str
    tx: float = 0; ty: float = 0      # translasi lokal
    rotation: float = 0               # radian, lokal
    sx: float = 1; sy: float = 1      # skala lokal
    children: list["Node"]
    visible: bool = True
    clip: Callable[[cairo.Context], None] | None = None   # path clipping opsional

    def add(self, child: "Node") -> "Node": ...
    def draw_self(self, ctx: cairo.Context) -> None: ...  # override di subclass
    def render(self, ctx: cairo.Context) -> None:
        ctx.save()
        ctx.translate(self.tx, self.ty)
        ctx.rotate(self.rotation)
        ctx.scale(self.sx, self.sy)
        if self.clip: self.clip(ctx); ctx.clip()
        self.draw_self(ctx)
        for c in self.children: c.render(ctx)
        ctx.restore()
```

Struktur pohon scene minimum:
```
Scene (root)
├── Latar (langit, tanah)
├── Kebun
│   └── Petak x9
│       └── PohonKopi
│           └── Batang
│               └── Cabang xn
│                   ├── Daun
│                   └── Ceri
├── Conveyor
│   └── Ceri di jalur
├── Pabrik
│   └── Mesin x3
│       └── Rangka
│           ├── RodaGigi   (rotate)
│           ├── Drum       (rotate + clip)
│           └── Corong     (translate)
└── UI
    └── Panel data, saldo
```

Aturan:
- Transformasi **selalu** disimpan sebagai nilai lokal di node, tidak dihitung manual ke koordinat dunia.
- Hit-test klik: transformasi koordinat klik dengan invers matriks node (`cairo.Matrix.invert`).
- **Mode debug (F9)**: gambar bounding box tiap node + daftar pohon node di pojok layar.

### 5.2 Procedural Modeling

**Pohon kopi (`coffee_tree.py`)**
- Input: `seed: int`, `stage: 1..4`, `vigor: float 0..1` (dari rumus pertumbuhan).
- Pakai `random.Random(seed)`. **Jangan** pakai `random` global → pohon harus identik setiap frame.
- Batang tegak dibagi `n_ruas = 2 + stage*2` ruas.
- Tiap ruas memunculkan **sepasang cabang lateral** (kiri-kanan), sudut 55°–75° ± jitter, panjang mengecil ke atas.
- Daun: berpasangan di sepanjang cabang, bentuk elips runcing dari 2 kurva Bézier.
- Bunga (stage 3) dan ceri (stage 4): cluster 3–6 buah di ketiak daun; jumlah dikali `vigor`.
- Ayunan angin: `rotation` cabang = `amp * sin(t * freq + phase_seed)`.

**Lainnya**: tekstur tanah (titik/retakan dari noise ber-seed), tumpukan karung (jumlah dari volume hasil olahan).

### 5.3 Materi Grafika Lain (minimal yang harus ada)

| Materi | Wajib diterapkan di |
| --- | --- |
| Transformasi 2D | roda gigi & drum berputar, ceri bergerak di conveyor, pohon membesar per tahap |
| Color blending | warna ceri hijau→kuning→merah, biji hijau→coklat sesuai roasting (`lerp_color` di `colors.py`) |
| Path & complex shapes | daun, ceri, jalur conveyor, siluet mesin |
| Clipping & masking | level isi karung/silo, jendela kaca roaster |
| Compositing | layer latar → objek → efek → UI; overlay malam (opsional) memakai `OPERATOR_MULTIPLY`/alpha |

### 5.4 Rumus (`game/formulas.py`)

```
laju_tumbuh = laju_dasar × f_hujan × f_suhu × f_rawat
harga_jual  = harga_dasar_data × faktor_grade × faktor_roasting
lama_jemur  = lama_dasar × (1 + k × normalisasi_curah_hujan)
```

- `f_hujan`, `f_suhu` ∈ [0, 1], dihitung dari jarak nilai data ke **rentang ideal kopi**.
- Semua konstanta (rentang ideal, laju_dasar, faktor grade, k) ditaruh di **satu tempat** (`CONFIG` di `formulas.py`) beserta komentar sumber literaturnya.
- Jika sumber literatur belum ada, tulis `# TODO: sumber` dan laporkan ke user. **Jangan mengarang sumber.**

---

## 6. Langkah Kerja (Step by Step)

Kerjakan **berurutan**. Jangan lompat ke tahap berikutnya sebelum kriteria selesai terpenuhi dan test lulus. Setelah tiap tahap, laporkan ringkas ke user: apa yang dibuat, cara mencobanya, dan apa yang belum.

### Tahap 0 — Setup
- Buat struktur folder, `requirements.txt` (`flask`, `flask-sock`, `pycairo`, `pytest`), `README.md` berisi cara menjalankan.
- ✅ Selesai jika: `python app.py` jalan dan `http://localhost:5000` menampilkan halaman kosong.

### Tahap 1 — Data
- Minta user meletakkan file asli di `data/raw/` (agent **tidak** mengunduh dari internet kecuali diminta).
- Tulis skrip pembersihan → `data/processed/*.json`.
- Isi `data/SOURCES.md`: instansi, judul dataset, URL, periode, tanggal akses, satuan, cakupan wilayah.
- `data_loader.py` memvalidasi kolom & satuan; error jelas jika data hilang.
- ✅ Selesai jika: `test_data_loader.py` lulus dan semua dataset tercatat di `SOURCES.md`.

### Tahap 2 — Scene Graph + Renderer
- Implementasi `Node`, `renderer.py` (render ke `ImageSurface` 960×540 → bytes PNG).
- WebSocket kirim frame ke browser; browser menampilkannya.
- ✅ Selesai jika: tampil latar + satu kotak dummy yang berputar, dan `test_node.py` (transformasi anak mengikuti induk, hit-test) lulus.

### Tahap 3 — Pohon Kopi Prosedural
- Implementasi `coffee_tree.py`, `leaf.py`, `cherry.py`, `colors.py`.
- ✅ Selesai jika: 4 tahap pohon tampil, seed sama → output identik (test), seed beda → bentuk beda, cabang berayun.

### Tahap 4 — Kebun & Gameplay Dasar
- Grid 3×3, tanam, siram, pupuk, waktu berjalan, tumbuh sesuai rumus, panen dengan grade.
- Pilih wilayah & bulan memuat data yang sesuai.
- ✅ Selesai jika: satu pohon bisa ditanam sampai dipanen, dan mengganti wilayah/bulan mengubah laju tumbuh.

### Tahap 5 — Conveyor & Mesin
- Conveyor (path), 3 mesin dengan bagian bergerak, clipping untuk level isi dan jendela roaster.
- ✅ Selesai jika: ceri hasil panen berjalan ke pabrik, diproses 3 mesin, warna biji berubah saat roasting.

### Tahap 6 — Jual, UI, Panel Data, Debug
- Jual dengan rumus harga, saldo, panel data (nilai + sumber), mode debug F9.
- ✅ Selesai jika: satu siklus penuh tanam → jual dapat dimainkan tanpa error; panel data menampilkan sumber.

### Tahap 7 — Opsional (hanya jika user minta / MVP sudah beres)
- Upgrade slot & mesin, siklus siang-malam, efek hujan, simpan progres.

### Tahap 8 — Finalisasi
- Ukur fps, rapikan kode, lengkapi README (cara jalan, kontrol, daftar teknik grafika + lokasi file-nya), screenshot untuk laporan.
- ✅ Selesai jika: semua test lulus dan fps ≥ 15 dengan 9 pohon + 3 mesin aktif.

---

## 7. Hal yang DILARANG

**Grafika**
- ❌ Membuat grafis 3D atau memakai engine 3D/game engine (Three.js, Unity, Godot, Pygame, Phaser).
- ❌ Menggambar objek game di JavaScript/Canvas API frontend. Semua objek game digambar Pycairo.
- ❌ Memakai file gambar/sprite/aset dari luar (PNG, SVG, tileset). Semua bentuk dibuat dengan kode.
- ❌ Menghitung posisi dunia secara manual sehingga melewati scene graph.
- ❌ Memakai `random` tanpa seed untuk objek prosedural (menyebabkan objek "berkedip" tiap frame).

**Data**
- ❌ Mengarang angka data, sumber, URL, atau kutipan literatur.
- ❌ Menyebut data sintetis/dummy sebagai data nyata. Data dummy wajib ditandai jelas (`data/dummy/`, label "DUMMY" di UI).
- ❌ Mengedit file di `data/raw/`.
- ❌ Hardcode angka data di dalam kode game; ambil selalu dari `data/processed/`.

**Scope**
- ❌ Menambah fitur di luar daftar F1–F13: karakter berjalan, NPC, multiplayer, login, database server, inventory kompleks, komoditas selain kopi.
- ❌ Mengganti tech stack atau struktur folder tanpa persetujuan user.
- ❌ Refactor besar pada tahap yang sudah selesai tanpa alasan dan izin.

**Proses**
- ❌ Menandai tahap selesai padahal test gagal atau belum dicoba.
- ❌ Menghapus/mematikan test supaya lulus.
- ❌ Menyimpan secret/API key di repo.
- ❌ Commit/push tanpa diminta user.

---

## 8. Konvensi Kode

- Python: PEP 8, type hints, docstring singkat (Bahasa Indonesia boleh).
- Nama file & fungsi: `snake_case`; kelas: `PascalCase`.
- Satu file = satu tanggung jawab. Fungsi > 50 baris dipecah.
- Setiap fungsi grafika yang menerapkan materi kuliah diberi komentar penanda, contoh:
  `# [GRAFKOM] Clipping: level isi karung`
  → memudahkan menulis laporan & demo (bisa dicari dengan `grep -r "\[GRAFKOM\]"`).
- Warna hanya didefinisikan di `colors.py`.
- Konstanta game hanya di `formulas.py` (`CONFIG`).

---

## 9. Testing

Minimal ada test untuk:
- `Node`: transformasi anak mengikuti induk; `save/restore` tidak bocor; hit-test dengan matriks invers.
- Prosedural: seed sama → struktur identik; jumlah cabang sesuai `stage`; ceri hanya muncul di stage 4.
- Rumus: nilai `f_hujan`, `f_suhu` selalu di [0, 1]; harga naik jika grade naik.
- Data loader: error jelas jika file/kolom hilang.

Jalankan `pytest` sebelum melaporkan tahap selesai.

---

## 10. Cara Berkomunikasi dengan User

- Bahasa: **Bahasa Indonesia**.
- Di akhir setiap tahap: ringkas (maks. ±8 baris) — yang dibuat, cara mencoba, yang belum/kendala.
- **Wajib bertanya dulu** jika:
  - data yang dibutuhkan belum ada di `data/raw/`;
  - butuh library baru;
  - instruksi user bertentangan dengan file ini atau dengan syarat dosen;
  - sebuah keputusan sulit dibatalkan (hapus file, ubah struktur).
- Jangan bertanya untuk hal kecil yang sudah jelas dari file ini — langsung kerjakan.

---

## 11. Definition of Done (Proyek)

- [ ] Satu siklus tanam → rawat → panen → olah (3 mesin) → jual dapat dimainkan di browser.
- [ ] Scene graph dipakai untuk semua objek; mode debug menampilkannya.
- [ ] Pohon kopi, daun, ceri, tanah, tumpukan karung dibuat prosedural (ber-seed).
- [ ] Transformasi 2D, color blending, path, clipping, compositing terlihat di game dan ditandai `[GRAFKOM]` di kode.
- [ ] Semua grafis dirender oleh Pycairo.
- [ ] Parameter berasal dari data nyata; `data/SOURCES.md` lengkap; panel data menampilkan sumber.
- [ ] Semua test lulus; fps ≥ 15.
- [ ] README menjelaskan cara menjalankan dan peta "teknik grafika → file".
