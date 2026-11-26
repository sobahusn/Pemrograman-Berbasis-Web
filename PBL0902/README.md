# PBL0902 - Car Microservices (FastAPI)

## Struktur

```text
PBL0902/
├── APPX/                 # FastAPI UI/gateway
├── SiteA/
│   ├── MS1/              # FastAPI service, berbagi DB-A
│   ├── MS2/              # FastAPI service, berbagi DB-A
│   └── DB-A.db
├── SiteB/
│   └── MS3/              # FastAPI service dan DB-B.db
├── server/               # Factory endpoint service
└── main.py               # Menjalankan semua proses
```

Struktur dan alur mengikuti PBL0901: APPX menampilkan data dari tiga
microservice; MS1 dan MS2 menggunakan database bersama DB-A, sedangkan MS3
menggunakan DB-B. Perbedaannya, seluruh aplikasi dan REST API di PBL0902
menggunakan FastAPI, bukan Flask. Database PBL0902 yang sudah ada dipertahankan
sebagai DB-A. UI APPX mengikuti tampilan PBL0602, dengan pemilih MS1/MS2/MS3
untuk menentukan service tujuan operasi tambah, ubah, hapus, dan pencarian.

## Menjalankan

Gunakan Python 3.12 dan `uv`. Jalankan dari folder PBL0902:

```bash
uv sync
uv run main.py
```

Runner menyalakan APPX dan ketiga service dalam proses terpisah. Tekan
`Ctrl+C` untuk menghentikan semua service.

- APPX: http://127.0.0.1:5000
- MS1: http://127.0.0.1:5051/cars/
- MS2: http://127.0.0.1:5052/cars/
- MS3: http://127.0.0.1:5053/cars/
- Dokumentasi API: `http://127.0.0.1:<port>/docs`

Log service disimpan di `.run-logs/`.
