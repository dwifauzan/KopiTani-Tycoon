# Sumber data Bagian A

Belum ada data asli di `data/raw/`. Jangan isi `data/processed/regions.json` atau
`config.json` dengan angka tanpa sumber. Data sintetis hanya ada di tes dan
`data/dummy/`, ditandai `DUMMY`, dan hanya dimuat saat `python app.py --dummy`.

Saat data tersedia, catat setiap dataset di tabel berikut sebelum dipakai:

| Kelompok | Instansi | Judul dataset/dokumen | URL | Periode | Tanggal akses | Satuan | Cakupan | File mentah |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Iklim | | | | | | mm/bulan, °C | | |
| Produksi | | | | | | kg, ha | | |
| Harga | | | | | | Rp/kg | | |
| Agronomi | | | | | | rentang iklim, pohon/ha | | |
| Pascapanen | | | | | | hari, faktor grade | | |
| Ekonomi game | | | | | | biaya, target, faktor roasting | | |

`regions.json` adalah array objek dengan kolom: `region_id`, `month` (1–12),
`rain_mm`, `temp_c`, `production_kg`, `area_ha`, `price_idr_per_kg`, dan
`sources` berisi `climate`, `production`, `price`.

`config.json` memakai nama field dari `game.formulas.Config` dan `sources`
berisi `agronomy`, `postharvest`, `economy`. Sumber harus menjelaskan angka
yang dipakai; `TODO: sumber` pada kode menandai angka yang masih dibutuhkan.
