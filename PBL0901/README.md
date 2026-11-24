# c006-Microservice
Course 006 Microserive

## Menjalankan semua layanan

Instal dependency dan jalankan satu runner dari folder PBL0901:

```bash
cd PBL0901
python -m pip install -r requirements.txt
python main.py
```

Semua microservice akan dijalankan sebagai proses terpisah. Tekan `Ctrl+C`
untuk menghentikan semuanya.

- APPX: http://localhost:5000
- MS1: http://localhost:5051/cars/
- MS2: http://localhost:5052/cars/
- MS3: http://localhost:5053/cars/

Log tersedia di `PBL0901/.run-logs/`.
