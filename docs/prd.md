# PRD — KopiTani Tycoon (v2.0)

**KopiTani Tycoon: Game Edukasi Agroindustri Kopi**

| Info | Keterangan |
| --- | --- |
| Versi | 2.0 — menggantikan PRD v1.0 |
| Tanggal | 25 November 2026 |
| Mata kuliah | Grafika Komputer — Informatika 2026 |
| Jenis aplikasi | Game edukasi |
| Platform | Website |
| Sudut pandang | **Side view (tampak samping)**, 2D |
| Gaya visual | **Pixel art** |
| Tim | A: _(nama)_ · B: _(nama)_ · C: _(nama)_ |

### Perubahan dari v1.0

| Aspek | v1.0 | v2.0 |
| --- | --- | --- |
| Sudut pandang | Top-down (isometrik semu) | **Side view** |
| Kebun | Grid 3×3 | **1 baris, 5 petak** |
| Gaya visual | Belum ditentukan | **Pixel art** (render 320×180, diperbesar 3×) |
| Aset | 100% Pycairo | **Campuran:** objek inti Pycairo, hiasan boleh PNG |
| Pabrik | Tampak atas | **Tampak potongan (cutaway)**: dinding depan dibuka, mesin terlihat |
| Tujuan menang | Belum ada | **Sistem bintang** di akhir musim (F14) |

---

## 1. Latar Belakang dan Masalah

Nilai jual kopi di tingkat petani sering rendah karena **penanganan pascapanen yang kurang tepat**: ceri dipetik sebelum matang, sortasi kurang baik, dan pengeringan tidak menyesuaikan cuaca. Hubungan **iklim → pertumbuhan → mutu panen → pengolahan → harga** juga sulit dipahami jika hanya disajikan dalam tabel statistik.

**Solusi:** game edukasi 2D tampak samping yang memvisualisasikan rantai budidaya hingga pengolahan kopi. Parameter permainan berasal dari data nyata (BMKG, BPS, Kementan), sehingga pemain langsung melihat akibat dari keputusannya.

---

## 2. Tujuan dan Indikator Keberhasilan

| # | Tujuan | Indikator keberhasilan |
| --- | --- | --- |
| T1 | Pemain memahami tahapan budidaya hingga pascapanen kopi | Responden dapat menyelesaikan 1 musim tanpa bantuan |
| T2 | Pemain memahami pengaruh iklim dan mutu panen | Hasil berubah saat wilayah/bulan dan grade berbeda |
| T3 | Memenuhi seluruh syarat RTM Grafika Komputer | Scene graph, procedural modeling, dan ≥ 2 materi lain dapat ditunjukkan saat demo |
| T4 | Berjalan lancar di browser | ≥ 15 fps dengan 5 pohon dan 3 mesin aktif |

---

## 3. Pengguna

| Pengguna | Kebutuhan |
| --- | --- |
| Pelajar SMK pertanian / mahasiswa | Memahami alur agroindustri kopi secara visual |
| Penyuluh pertanian | Media bantu menjelaskan petik merah dan pascapanen |
| Masyarakat umum | Mengenal proses kopi dari kebun sampai siap jual |
| Dosen / penguji | Melihat penerapan teknik grafika (mode debug) |

---

## 4. Ruang Lingkup

**Termasuk:**
- Komoditas kopi, varietas Robusta dan Arabika.
- Satu layar tampak samping: kebun 5 petak, conveyor, pabrik potongan dengan 3 stasiun proses.
- Satu musim permainan (30 hari game, sekitar 15 menit) dengan penilaian bintang.
- Parameter dari data nyata yang tersimpan lokal.

**Tidak termasuk:**
- Grafis 3D, OpenGL/WebGL, game engine.
- Karakter yang berjalan, NPC, multiplayer, login, database server.
- Layar yang bergulir (scrolling). Kamera diam, satu layar.
- Komoditas selain kopi.

---

## 5. Alur Permainan

```
Mulai (menu + tutorial singkat)
  → Pilih wilayah & bulan  (data BMKG/BPS dimuat)
  → ┌───────────── diulang selama 1 musim (30 hari game) ─────────────┐
    │ Tanam → Rawat → Tumbuh 4 tahap → Panen (grade)                  │
    │   → Conveyor → Sortasi → Pulper → Jemur → Roasting → Karung      │
    │   → Jual → Upgrade (opsional) → kembali ke Tanam                 │
    └─────────────────────────────────────────────────────────────────┘
  → Akhir musim: bintang 1–3 + ringkasan edukasi
```

### Tujuan pemain

Mendapat **keuntungan sebesar mungkin dengan mutu kopi setinggi mungkin** dalam satu musim.

| Bintang | Syarat (angka target ditetapkan saat implementasi) |
| --- | --- |
| ★ | Saldo akhir > modal awal |
| ★★ | Mencapai target saldo |
| ★★★ | Mencapai target saldo **dan** ≥ 70% kopi terjual bergrade A |

### Keputusan yang dihadapi pemain

- **Kapan panen.** Ceri hijau/kuning menurunkan grade; menunggu merah butuh waktu.
- **Wilayah dan bulan.** Bulan hujan membuat penjemuran lama dan antrean menumpuk.
- **Perawatan.** Siram dan pupuk mempercepat tumbuh tapi memakan biaya.
- **Tingkat sangrai.** Light, medium, dan dark punya harga dan durasi berbeda.
- **Upgrade.** Menambah petak atau mempercepat mesin.

---

## 6. Tata Letak Layar (Side View)

Resolusi internal **320×180 piksel**, diperbesar 3× menjadi **960×540** di browser.

```
y=0   ┌──────────────────────────────────────────────────────────────┐
      │ [Saldo] [Hari 12/30] [Jember · Jul]        [Data] [F9]       │ ← bar atas (16 px)
y=16  │   ☀            ☁                   ☁                         │ ← langit, matahari, awan
      │ ▲▲ bukit & hutan latar (PNG) ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲        │ ← latar belakang
      │                                     ┌──── PABRIK (cutaway) ──┐│
      │  🌳   🌳   🌱   🌳   ·               │ Sortasi Pulper  Roaster ││
      │  🌳   🌳   🌱   🌳   ·               │   ▼      ⚙      [◉]    ││
y=150 │══╧════╧════╧════╧════╧═══ conveyor ═══╧═══ Rak jemur ═ Karung ═╡│ ← garis tanah
      │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ lapisan tanah ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
y=180 └──────────────────────────────────────────────────────────────┘
       x=0 ───── kebun (x 8–160) ─────    x 170–312: pabrik
```

| Area | Posisi (px, resolusi internal) |
| --- | --- |
| Bar atas (UI) | y 0–16 |
| Langit + awan | y 16–90 |
| Latar bukit/hutan | y 70–150 |
| Kebun 5 petak | x 8–160, garis tanah y = 150, tinggi pohon maks ±60 px |
| Conveyor | Sepanjang garis tanah dari kebun ke pabrik |
| Pabrik | x 170–312, y 60–150 |
| Lapisan tanah | y 150–180 |

**Urutan lapisan (compositing):** langit → awan → bukit/hutan latar → tanah → kebun & pabrik → conveyor & ceri → efek (hujan, malam) → UI.

---

## 7. Kebutuhan Fungsional

**MVP** = wajib selesai · **Opsional** = setelah semua MVP selesai.

| ID | Fitur | Prioritas | Kriteria terima |
| --- | --- | --- | --- |
| F1 | Pilih wilayah & bulan | MVP | Mengganti pilihan mengubah nilai di panel data dan laju tumbuh |
| F2 | Kebun 5 petak: tanam, siram, pupuk | MVP | 5 petak dapat ditanam dan dirawat terpisah |
| F3 | Pohon kopi prosedural 4 tahap | MVP | Tiap petak berbentuk unik, konsisten antar-frame, membesar per tahap, cabang berayun |
| F4 | Panen ceri dengan grade A/B/C | MVP | Grade sesuai warna saat dipetik, tercatat per batch |
| F5 | Conveyor kebun → pabrik | MVP | Ceri bergerak mulus di sepanjang jalur |
| F6 | Stasiun proses: sortasi, pulper, rak jemur, roasting | MVP | Batch melewati semua stasiun; lama jemur sesuai data hujan; warna biji sesuai tingkat sangrai |
| F7 | Jual & saldo | MVP | Saldo bertambah sesuai rumus harga |
| F8 | Panel info data | MVP | Nilai dan sumber data tampil; nilainya sama dengan dataset |
| F9 | Mode debug scene graph | MVP | Bounding box dan pohon node tampil saat tombol F9 ditekan |
| F14 | Waktu musim & sistem bintang | MVP | Musim berakhir di hari ke-30; layar akhir menampilkan bintang dan ringkasan edukasi |
| F10 | Upgrade petak/mesin | Opsional | Menambah petak ke-6 dst. atau mempercepat mesin |
| F11 | Siang-malam | Opsional | Overlay warna langit berubah sesuai jam game |
| F12 | Efek hujan | Opsional | Partikel hujan muncul saat curah hujan bulan itu tinggi |
| F13 | Simpan progres | Opsional | Progres tersimpan di browser |

### Grade panen

| Warna ceri saat dipetik | Grade | Faktor grade |
| --- | --- | --- |
| Merah | A | 1,0 |
| Kuning | B | _(dari literatur)_ |
| Hijau | C | _(dari literatur)_ |

### Kontrol

| Aksi | Kontrol |
| --- | --- |
| Tanam | Klik petak kosong → pilih Robusta/Arabika |
| Siram / pupuk | Klik pohon → tombol |
| Panen | Klik pohon yang berbuah (ceri dipetik semua; grade dihitung per ceri) |
| Pilih tingkat sangrai | Klik mesin roasting |
| Jual | Klik tumpukan karung → Jual |
| Debug | F9 |

---

## 8. Kebutuhan Grafika Komputer

| Syarat | Penerapan | Ditunjukkan di |
| --- | --- | --- |
| **Scene graph** | Kelas `Node` dengan transformasi lokal; save → transform → draw → children → restore | Pohon kopi, mesin, seluruh scene; mode debug F9 |
| **Procedural modeling** | Pohon kopi rekursif ber-seed; siluet bukit; awan; lapisan tanah; tumpukan karung | Kebun, latar, pabrik |
| Transformasi 2D | Ayunan cabang (rotate), pohon membesar (scale), ceri di conveyor (translate), roda gigi & drum (rotate), awan bergerak | F3, F5, F6 |
| Color blending | Ceri hijau → kuning → merah; biji hijau → coklat saat roasting & jemur; warna langit siang-malam | F4, F6, F11 |
| Path & complex shapes | Daun & ceri (Bézier), siluet bukit, jalur conveyor, bentuk mesin | F3, F5, F6 |
| Clipping & masking | Jendela kaca roaster, level isi karung, potongan dinding pabrik | F6, F7 |
| Compositing | Lapisan latar → objek → efek → UI; overlay malam & hujan | Seluruh frame |
| Teknik pixel art | Render 320×180 tanpa antialias, diperbesar 3× nearest-neighbor | Seluruh frame |
| **Pycairo** | Semua objek inti digambar dan **semua** aset (termasuk PNG) dirender oleh Pycairo | Seluruh aplikasi |

### Struktur scene graph

```
Scene (root)
├── Langit ─┬─ Matahari/Bulan
│           └─ Awan xn                        (translate: bergerak pelan)
├── Latar ─┬─ Bukit (prosedural)
│          └─ Hutan latar (PNG)
├── Tanah ─ Lapisan tanah (prosedural)
├── Kebun ─ Petak x5 ─ PohonKopi ─ Batang ─ Cabang xn ─┬─ Daun
│                                                       ├─ Bunga
│                                                       └─ Ceri
├── Conveyor ─ Sabuk ─ Ceri di jalur xn
├── Pabrik ─┬─ Bangunan (dinding belakang, atap, potongan depan)
│           ├─ Sortasi ─┬─ Corong
│           │           └─ Ayakan               (translate: bergetar)
│           ├─ Pulper ──┬─ Corong
│           │           └─ Silinder + RodaGigi  (rotate)
│           ├─ RakJemur ─ Biji xn               (color blending)
│           ├─ Roaster ─┬─ Drum                 (rotate)
│           │           ├─ Jendela kaca         (clip)
│           │           └─ Cerobong ─ Asap xn
│           └─ Gudang ─ Karung xn               (clip: level isi)
├── Efek ─┬─ Hujan
│         └─ Overlay malam
└── UI ─┬─ Bar atas
        ├─ Panel data
        └─ Layar akhir musim
```

### Aturan procedural pohon kopi (tampak samping)

| Parameter | Pengaruh |
| --- | --- |
| `seed` | Variasi sudut, panjang cabang, posisi daun (tetap per petak) |
| `stage` (1–4) | Jumlah ruas = 2 + stage × 2; bunga di tahap 3; ceri di tahap 4 |
| `vigor` (0–1) | Kerimbunan daun dan jumlah ceri (dari laju tumbuh) |
| Cabang | Berpasangan kiri-kanan di tiap ruas, sudut 15°–30° dari horizontal, makin ke atas makin pendek |
| Ukuran | Tinggi maks ±60 px, lebar maks ±28 px (resolusi internal) |
| Ayunan | `rotation = amp × sin(t × freq + phase_seed)` per cabang |

---

## 9. Kebutuhan Data

| Data | Sumber | Dipakai untuk |
| --- | --- | --- |
| Produksi & luas areal kopi | BPS — Statistik Kopi Indonesia / Statistik Tanaman Perkebunan Tahunan; Kementan — Statistik Perkebunan | Daftar wilayah, jumlah ceri per pohon (dari produktivitas) |
| Curah hujan & suhu bulanan | BMKG Data Online (dataonline.bmkg.go.id) | `f_hujan`, `f_suhu`, lama jemur, efek hujan |
| Harga produsen kopi | BPS — Statistik Harga Produsen Pertanian | Harga dasar penjualan, target bintang |
| Syarat tumbuh & pascapanen | Panduan budidaya Kementan, jurnal | Rentang ideal iklim, aturan grade, urutan proses |

```
laju_tumbuh = laju_dasar × f_hujan × f_suhu × f_rawat
lama_jemur  = lama_dasar × (1 + k × normalisasi_curah_hujan)
harga_jual  = harga_dasar_data × faktor_grade × faktor_roasting
```

Identitas setiap dataset dicatat di `data/SOURCES.md`. Data dummy hanya untuk uji tampilan dan diberi label "DUMMY".

---

## 10. Daftar Aset

### Aturan aset

| Aturan | Ketentuan |
| --- | --- |
| Objek inti yang dinilai (pohon kopi, mesin, conveyor, efek, UI) | **Wajib Pycairo** |
| Hiasan latar yang detail (hutan, semak, batu, pagar) | **Boleh PNG** |
| Format gambar luar | **PNG** dengan latar transparan (bukan JPG) |
| Cara menampilkan PNG | Dimuat dan dirender **lewat Pycairo** (`ImageSurface.create_from_png`), bukan lewat JavaScript |
| Lisensi PNG | Hanya aset berlisensi bebas (mis. CC0); sumber dicatat di `assets/CREDITS.md` |
| Gaya | Pixel art, tampak samping, palet terbatas 16–32 warna (`colors.py`) |
| Ukuran tile acuan | 16×16 px |

### A. Lingkungan

| ID | Aset | Metode | Ukuran (px) | Animasi / variasi | Teknik grafika | PIC |
| --- | --- | --- | --- | --- | --- | --- |
| L1 | Langit (gradasi pita warna) | Pycairo | 320×134 | Warna berubah siang-malam | Color blending | C |
| L2 | Matahari & bulan | Pycairo | 12×12 | Bergerak melengkung sepanjang hari | Primitives, translate | C |
| L3 | Awan | Pycairo | 24–40 × 10–14 | Bentuk prosedural, bergerak pelan | Procedural, translate | C |
| L4 | Siluet bukit (2 lapis) | Pycairo | 320×60 | Bentuk dari fungsi sinus/noise | Procedural, path | C |
| L5 | Hutan / pohon besar latar | **PNG** | 32×48 per pohon | 2–3 variasi | Compositing | C |
| L6 | Semak, batu, bunga liar | **PNG** | 8–16 | 3–4 variasi | Compositing | C |
| L7 | Pagar kayu | **PNG** | 16×16 tile | Diulang horizontal | Compositing | C |
| L8 | Garis rumput (permukaan tanah) | Pycairo | 320×4 | Helai prosedural | Procedural | C |
| L9 | Lapisan tanah (potongan) | Pycairo | 320×30 | Titik batu & akar prosedural | Procedural | C |

### B. Kebun

| ID | Aset | Metode | Ukuran (px) | Animasi / variasi | Teknik grafika | PIC |
| --- | --- | --- | --- | --- | --- | --- |
| K1 | Petak tanah (gundukan) | Pycairo | 26×8 | Kering / basah (warna lebih gelap) | Color blending | C |
| K2 | Pohon kopi tahap 1 (bibit) | Pycairo | ±8×12 | Ber-seed | Procedural, scene graph | C |
| K3 | Pohon kopi tahap 2 (muda) | Pycairo | ±16×28 | Ber-seed, ayunan | Procedural, scene graph, rotate | C |
| K4 | Pohon kopi tahap 3 (berbunga) | Pycairo | ±22×44 | + bunga putih | Procedural, scene graph | C |
| K5 | Pohon kopi tahap 4 (berbuah) | Pycairo | ±28×60 | + ceri | Procedural, scene graph | C |
| K6 | Daun | Pycairo | 3–5 × 2 | 2 warna hijau | Path Bézier | C |
| K7 | Bunga kopi | Pycairo | 2×2 | — | Primitives | C |
| K8 | Ceri kopi | Pycairo | 2×2 | Hijau → kuning → merah | Color blending | C |
| K9 | Efek siram (tetesan) | Pycairo | 6×8 | Jatuh 0,5 detik | Translate | C |
| K10 | Efek pupuk (butiran) | Pycairo | 6×6 | Jatuh & memudar | Translate, alpha | C |
| K11 | Penanda petak terpilih | Pycairo | 28×64 | Berkedip | Compositing | A |

### C. Conveyor dan Pabrik

| ID | Aset | Metode | Ukuran (px) | Animasi / variasi | Teknik grafika | PIC |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Sabuk conveyor | Pycairo | panjang ±160 × 6 | Garis sabuk bergeser | Path, translate | B |
| P2 | Ceri di conveyor | Pycairo | 2×2 | Bergerak di jalur | Translate | B |
| P3 | Bangunan pabrik (potongan) | Pycairo | 142×90 | Dinding belakang, atap, tepi potongan | Primitives, clipping | B |
| P4 | Mesin sortasi (corong + ayakan) | Pycairo | 28×36 | Ayakan bergetar | Scene graph, translate | B |
| P5 | Mesin pulper (corong + silinder + roda gigi) | Pycairo | 28×36 | Silinder & roda gigi berputar | Scene graph, rotate | B |
| P6 | Rak jemur | Pycairo | 36×14 | Biji berubah warna saat kering | Color blending | B |
| P7 | Mesin roasting (drum + jendela + cerobong) | Pycairo | 32×44 | Drum berputar, biji terlihat lewat jendela | Scene graph, rotate, clip | B |
| P8 | Asap cerobong | Pycairo | 4–8 | Naik & memudar | Translate, alpha | B |
| P9 | Biji kopi | Pycairo | 2×2 | Hijau → coklat muda → coklat tua | Color blending | B |
| P10 | Karung kopi | Pycairo | 12×14 | Level isi naik | Clipping | B |
| P11 | Tumpukan karung (gudang) | Pycairo | 40×30 | Jumlah dari volume hasil | Procedural | B |
| P12 | Indikator mesin (lampu status) | Pycairo | 3×3 | Hijau (jalan) / kuning (antri) / merah (penuh) | Color | B |

### D. Efek

| ID | Aset | Metode | Ukuran (px) | Animasi / variasi | Teknik grafika | PIC |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | Hujan | Pycairo | 1×3 per tetes | Jatuh miring, kepadatan dari data | Translate, compositing | C |
| E2 | Overlay malam | Pycairo | 320×180 | Biru gelap transparan | Compositing | C |
| E3 | Kilau grade A | Pycairo | 5×5 | Bintang kecil berkedip saat panen merah | Alpha | C |
| E4 | Teks melayang "+Rp" | Pycairo | — | Naik & memudar saat jual | Translate, alpha | A |

### E. Antarmuka (UI)

| ID | Aset | Metode | Ukuran (px) | Keterangan | PIC |
| --- | --- | --- | --- | --- | --- |
| U1 | Bar atas | Pycairo | 320×16 | Saldo, hari, wilayah/bulan | A |
| U2 | Panel info data | Pycairo | ±120×80 | Nilai data + sumber | A |
| U3 | Tombol di kanvas (Siram, Pupuk, Jual, Light/Medium/Dark) | Pycairo | 32×12 | Normal / hover / ditekan | A |
| U4 | Ikon: koin, tetes air, pupuk, kalender, termometer, awan hujan, bintang | Pycairo | 8×8 | Satu set seragam | A |
| U5 | Tooltip | Pycairo | dinamis | Info saat kursor di atas objek | A |
| U6 | Layar akhir musim | Pycairo | 200×120 | Bintang + ringkasan edukasi | A |
| U7 | Layar menu & tutorial | **HTML** | — | Di luar kanvas (pilih wilayah, mulai) | A |
| U8 | Font pixel | **File font** (TTF, lisensi bebas) | 8 px | Dipasang di sistem server; dirender Pycairo | A |
| U9 | Overlay debug (F9) | Pycairo | 320×180 | Bounding box + daftar node | B |

### Ringkasan beban aset per anggota

| Anggota | Jumlah aset | Isi utama |
| --- | --- | --- |
| A | 10 | UI, ikon, tombol, layar akhir |
| B | 13 | Conveyor, pabrik, 4 stasiun proses, karung, debug |
| C | 22 (termasuk 3 kelompok PNG) | Langit, latar, tanah, pohon kopi 4 tahap, efek |

C memiliki item terbanyak, tetapi sebagian besar kecil dan dihasilkan dari satu generator (pohon, awan, bukit). Bila perlu, efek (E1–E3) dapat dipindah ke A.

---

## 11. Kebutuhan Non-Fungsional

| Aspek | Ketentuan |
| --- | --- |
| Performa | ≥ 15 fps saat animasi; lapisan statis (langit, bukit, tanah, bangunan) di-cache |
| Kompatibilitas | Chrome & Firefox terbaru |
| Offline | Data dan aset tersimpan lokal |
| Konsistensi visual | Objek prosedural ber-seed; koordinat bilangan bulat; tanpa antialias |
| Keterbacaan kode | Modular; bagian materi kuliah diberi penanda `[GRAFKOM]` |
| Kejujuran data & aset | Tidak ada angka atau sumber yang dikarang; setiap PNG tercatat lisensinya |

---

## 12. Arsitektur dan Teknologi

| Lapisan | Teknologi | Tugas |
| --- | --- | --- |
| Frontend | HTML + CSS + JavaScript | Menu (HTML), menampilkan frame PNG, mengirim klik |
| Komunikasi | WebSocket (`flask-sock`) | Input → server; frame → browser |
| Backend | Python 3.11 + Flask | Game logic, data loader, rumus |
| Grafika | **Pycairo** | Scene graph, procedural, render 320×180 → upscale 3× → PNG |
| Aset luar | PNG di `assets/` | Dimuat Pycairo |
| Data | CSV/JSON di `data/` | Parameter permainan |
| Testing | pytest | Node, prosedural, rumus, data loader |

```
Browser ──klik──► Flask: Game logic → Generator prosedural → Scene graph → Renderer Pycairo
   ▲                         ▲                                     ▲          (320×180, tanpa AA)
   │                   Data lokal (CSV/JSON)                 Aset PNG              │
   └──────────────────────────── frame PNG 960×540 ◄──────── upscale 3× nearest ◄──┘
```

---

## 13. Rencana Pengembangan (8 minggu)

| Minggu | A — Data & Logic + UI | B — Scene Graph & Pabrik | C — Procedural & Lingkungan |
| --- | --- | --- | --- |
| 1 | Unduh & bersihkan data; finalkan rumus | Setup repo, `Node`, renderer pixel art | Palet warna; cari & catat aset PNG |
| 2 | Flask + WebSocket, `GameState` | Integrasi frame ke browser, cache lapisan | Pohon kopi tahap 1–4 |
| 3 | Tanam, rawat, tumbuh | Bangunan pabrik, conveyor | Langit, awan, bukit, tanah |
| 4 | Panen + grade, pilih wilayah/bulan | Sortasi, pulper | Ayunan cabang, ceri & bunga |
| 5 | Jual, panel data, UI, ikon | Rak jemur, roaster, karung | Efek siram/pupuk, hujan, malam |
| 6 | **Integrasi: 1 musim penuh bisa dimainkan + layar bintang (MVP selesai)** | | |
| 7 | Simpan progres | Upgrade mesin, debug F9 dipoles | Polishing visual |
| 8 | **Bersama: testing, perbaikan, laporan, latihan demo** | | |

---

## 14. Rencana Pengujian

| Jenis | Cara | Lulus jika |
| --- | --- | --- |
| Unit test | pytest untuk node, prosedural, rumus, data loader | Semua lulus |
| Fungsional | Skenario per fitur F1–F9, F14 | Semua kriteria terima terpenuhi |
| Konsistensi data | Bandingkan panel data dengan dataset | Nilai sama |
| Visual | Cek tiap aset di resolusi 320×180 | Detail terbaca, gaya PNG & Pycairo serasi |
| Performa | 5 pohon + 3 mesin aktif + hujan | ≥ 15 fps |
| Usability | 5–10 responden memainkan 1 musim + kuesioner | Mayoritas menyelesaikan musim dan memahami alurnya |

---

## 15. Risiko dan Mitigasi

| Risiko | Mitigasi |
| --- | --- |
| Gaya PNG dan buatan Pycairo tidak serasi | Ambil palet dari paket PNG; satu paket aset saja |
| Detail hilang di resolusi kecil | Objek inti minimal ukuran pada daftar aset; uji tiap aset di 320×180 |
| Render server lambat | Cache lapisan statis; render ulang hanya yang berubah |
| Data iklim tidak lengkap | Pakai level provinsi/stasiun terdekat; tulis asumsinya |
| Scope membengkak | Kunci F1–F9 + F14 sebagai MVP |

---

## 16. Hal yang Masih Perlu Ditetapkan

- [ ] Wilayah yang dipakai (disarankan Jember + 2–3 sentra kopi lain).
- [ ] Faktor grade B/C dan faktor roasting beserta sumber literaturnya.
- [ ] Modal awal dan target saldo untuk sistem bintang.
- [ ] Paket aset PNG yang dipakai dan lisensinya.
- [ ] Font pixel yang dipakai dan lisensinya.
- [ ] Konfirmasi ke dosen bahwa aset hiasan PNG diperbolehkan.
- [ ] Nama anggota A, B, C.
