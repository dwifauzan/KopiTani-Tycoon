# Bagian A — data, logika, UI, server

Bagian A dapat dicoba dengan data contoh **DUMMY**. Angkanya bukan data nyata
dan tidak boleh dipakai sebagai hasil akhir proyek.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py --dummy
```

Buka `http://localhost:5000`. Pilih wilayah/bulan, klik **Mulai**, lalu klik
petak 1–5. Tombol ROB/ARA di bawah frame memilih varietas; tombol lain untuk siram, pupuk, panen,
proses, pilih roasting, jual, dan tambah hari. Klik **DATA** untuk nilai dan
label sumber. Frame ini baru UI Bagian A; grafika kebun/pabrik menunggu
integrasi Bagian B dan C.

Jalankan tes dengan `.venv/bin/python -m pytest -q tests`.

Untuk data asli, masukkan `regions.json` dan `config.json` ke `data/processed/`
sesuai skema pada `data/SOURCES.md`, lalu jalankan `python app.py` tanpa
`--dummy`. Isi `data/SOURCES.md` dengan identitas dataset dan literatur dahulu.
File mentah disimpan di `data/raw/` tanpa diedit. Belum ada pembersih CSV
karena format file sumber belum diberikan.
