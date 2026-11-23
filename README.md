# ☕ KopiTani Tycoon

**Game Edukasi Budidaya dan Pengolahan Kopi Berbasis Web Menggunakan Pycairo**

Final Project Mata Kuliah Grafika Komputer — Informatika 2026

---

## Tentang Proyek

KopiTani Tycoon adalah game edukasi 2D berbasis web tentang agroindustri kopi. Pemain mengelola kebun kopi sekaligus unit pengolahan pascapanen: menanam, merawat, memanen ceri, mengolahnya lewat mesin, lalu menjual hasilnya.

Pertumbuhan tanaman, lama penjemuran, dan harga jual dipengaruhi **data nyata** dari BMKG, BPS, dan Kementerian Pertanian. Dengan begitu pemain bisa melihat langsung bagaimana iklim dan mutu panen memengaruhi hasil akhir.

### Permasalahan yang diangkat

- Mutu dan harga kopi petani sering rendah karena penanganan pascapanen kurang tepat, misalnya petik ceri belum matang, sortasi buruk, atau pengeringan tidak sesuai cuaca.
- Hubungan antara iklim, pertumbuhan, pengolahan, dan nilai jual sulit dipahami jika hanya dibaca dari tabel statistik.

### Target pengguna

Pelajar SMK pertanian, mahasiswa, penyuluh pertanian, dan masyarakat umum.

---

## Fitur

| ID | Fitur | Status |
| --- | --- | --- |
| F1 | Pilih wilayah dan bulan (memuat data iklim & harga) | MVP |
| F2 | Kebun grid 3×3: tanam, siram, pupuk | MVP |
| F3 | Pohon kopi prosedural dengan 4 tahap tumbuh | MVP |
| F4 | Panen ceri dengan grade mutu | MVP |
| F5 | Conveyor dari kebun ke pabrik | MVP |
| F6 | Tiga mesin: sortasi, pulper + jemur, roasting | MVP |
| F7 | Jual hasil & saldo | MVP |
| F8 | Panel info data (nilai + sumber) | MVP |
| F9 | Mode debug scene graph | MVP |
| F10 | Upgrade slot & mesin | Opsional |
| F11 | Siklus siang-malam | Opsional |
| F12 | Efek hujan | Opsional |
| F13 | Simpan progres | Opsional |

---

## Penerapan Grafika Komputer

Semua objek game digambar dengan **Pycairo** di sisi server. Browser hanya menampilkan frame PNG dan mengirim input klik.

| Teknik | Penerapan | Lokasi kode |
| --- | --- | --- |
| **Hierarchical Modeling / Scene Graph** | Kelas `Node` dengan transformasi lokal; pohon kopi (batang → cabang → daun/ceri) dan mesin (rangka → roda gigi/drum/corong) | `graphics/node.py`, `graphics/scene.py` |
| **Procedural Modeling** | Pohon kopi rekursif ber-seed, daun dari kurva Bézier, cluster ceri, tekstur tanah, tumpukan karung | `graphics/procedural/` |
| Transformasi 2D | Rotasi roda gigi & drum, translasi ceri di conveyor, scaling pohon per tahap, ayunan cabang | `graphics/objects/`, `graphics/procedural/coffee_tree.py` |
| Color blending | Ceri hijau → kuning → merah, biji hijau → coklat sesuai tingkat roasting | `graphics/colors.py` |
| Path & complex shapes | Daun, ceri, jalur conveyor, siluet mesin | `graphics/procedural/leaf.py`, `graphics/objects/conveyor.py` |
| Clipping & masking | Level isi karung/silo, jendela kaca mesin roasting | `graphics/objects/machine_roaster.py`, `graphics/procedural/sacks.py` |
| Compositing | Layer latar → objek → efek → UI; overlay malam (opsional) | `graphics/renderer.py` |

> Cari semua bagian kode yang menerapkan materi kuliah dengan:
> ```bash
> grep -rn "\[GRAFKOM\]" graphics/
> ```

### Scene graph

```
Scene (root)
├── Latar (langit, tanah)
├── Kebun
│   └── Petak x9
│       └── PohonKopi            ← scale: tahap tumbuh
│           └── Batang
│               └── Cabang xn    ← rotate: ayunan
│                   ├── Daun
│                   └── Ceri     ← color blending
├── Conveyor
│   └── Ceri di jalur            ← translate di path
├── Pabrik
│   └── Mesin x3
│       └── Rangka
│           ├── RodaGigi         ← rotate
│           ├── Drum             ← rotate + clip
│           └── Corong           ← translate
└── UI
    └── Panel data, saldo
```

---

## Arsitektur

```
Browser (HTML + JS)                Server Python (Flask)                     Data lokal
┌──────────────────┐   klik/WS    ┌──────────────────────────┐   load    ┌───────────────┐
│ tampilkan frame  │ ───────────► │ Game logic + data loader │ ◄──────── │ CSV / JSON    │
│ kirim input      │              │ Generator prosedural     │           │ BMKG/BPS/...  │
│                  │ ◄─────────── │ Scene graph (Node)       │           └───────────────┘
└──────────────────┘  frame PNG   │ Renderer Pycairo         │
                                  └──────────────────────────┘
```

1. Pemain klik di browser → dikirim lewat WebSocket.
2. Game logic memperbarui state memakai rumus dan data.
3. Generator prosedural memperbarui node di scene graph.
4. Pycairo merender scene ke PNG 960×540 dan mengirimkannya ke browser.

---

## Data

Sumber data lengkap (instansi, judul dataset, URL, periode, tanggal akses, satuan, cakupan) dicatat di [`data/SOURCES.md`](data/SOURCES.md).

| Data | Sumber | Dipakai untuk |
| --- | --- | --- |
| Curah hujan & suhu bulanan | BMKG Data Online | Laju tumbuh & lama penjemuran |
| Produksi & luas areal kopi | BPS / Satu Data Pertanian Kementan | Pilihan wilayah & hasil panen dasar |
| Harga kopi tingkat produsen | BPS / Dinas Perdagangan | Harga dasar penjualan |
| Tahapan & standar pascapanen | Publikasi teknis & studi literatur | Urutan mesin, aturan grade, durasi proses |

### Rumus utama

```
laju_tumbuh = laju_dasar × f_hujan × f_suhu × f_rawat
harga_jual  = harga_dasar_data × faktor_grade × faktor_roasting
lama_jemur  = lama_dasar × (1 + k × normalisasi_curah_hujan)
```

Semua konstanta beserta sumber literaturnya ada di `game/formulas.py` (`CONFIG`).

> **Catatan:** model pertumbuhan adalah penyederhanaan untuk tujuan edukasi, bukan model agronomi yang presisi. Data dummy (jika ada) disimpan di `data/dummy/` dan diberi label "DUMMY" di dalam game.

---

## Instalasi

### Prasyarat

- Python 3.11 atau lebih baru
- Library sistem Cairo (dibutuhkan oleh Pycairo)

| OS | Perintah install Cairo |
| --- | --- |
| Ubuntu/Debian | `sudo apt install libcairo2-dev pkg-config python3-dev` |
| macOS (Homebrew) | `brew install cairo pkg-config` |
| Windows | Biasanya cukup `pip install pycairo` (wheel sudah menyertakan Cairo). Jika gagal, gunakan MSYS2 atau Conda: `conda install -c conda-forge pycairo` |

### Langkah

```bash
# 1. Clone repositori
git clone <url-repo>
cd kopitani

# 2. Buat virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependensi
pip install -r requirements.txt

# 4. Siapkan data
#    Letakkan file asli dari portal di data/raw/, lalu jalankan:
python -m game.data_loader --prepare

# 5. Jalankan server
python app.py
```

Buka **http://localhost:5000** di browser (Chrome / Firefox).

---

## Cara Bermain

| Aksi | Kontrol |
| --- | --- |
| Pilih wilayah & bulan | Dropdown di panel kanan atas |
| Tanam bibit | Klik petak kosong → pilih Robusta / Arabika |
| Siram / pupuk | Klik pohon → tombol Siram / Pupuk |
| Panen | Klik ceri yang sudah merah (ceri hijau menurunkan grade) |
| Proses di pabrik | Ceri otomatis berjalan di conveyor; klik mesin untuk memulai proses |
| Pilih tingkat roasting | Klik mesin roasting → Light / Medium / Dark |
| Jual | Klik karung hasil olahan → Jual |
| Mode debug scene graph | Tekan **F9** |

---

## Struktur Folder

```
kopitani/
├── app.py                 # entry Flask + WebSocket
├── game/                  # state, logika, rumus, data loader
├── graphics/
│   ├── node.py            # scene graph
│   ├── scene.py           # penyusunan scene
│   ├── renderer.py        # render Pycairo → PNG
│   ├── colors.py          # palet & color blending
│   ├── procedural/        # pohon, daun, ceri, tanah, karung
│   └── objects/           # mesin, conveyor, UI
├── data/
│   ├── raw/               # data asli (tidak diedit)
│   ├── processed/         # data siap pakai
│   └── SOURCES.md         # identitas sumber data
├── static/                # index.html, main.js, style.css
└── tests/                 # pytest
```

---

## Testing

```bash
pytest
```

Test mencakup: transformasi scene graph & hit-test, konsistensi generator prosedural (seed sama → hasil sama), batas nilai rumus, dan validasi data loader.

---

## Tim Pengembang

| Nama | NIM | Peran |
| --- | --- | --- |
| _(isi)_ | _(isi)_ | _(isi)_ |
| _(isi)_ | _(isi)_ | _(isi)_ |
| _(isi)_ | _(isi)_ | _(isi)_ |

Dosen pengampu: _(isi)_

---

## Lisensi

Proyek ini dibuat untuk keperluan akademik Mata Kuliah Grafika Komputer. Data yang digunakan tetap milik masing-masing instansi sumber.
