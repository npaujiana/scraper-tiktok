# 🎵 Scraper TikTok

Alat pengunduh dan pengekstrak data konten TikTok/Douyin yang dilengkapi dengan fitur penyimpanan data terpusat menggunakan PostgreSQL.

> Fork dari [TikTokDownloader](https://github.com/JoeanAmier/TikTokDownloader) oleh JoeanAmier, dengan modifikasi dan penambahan fitur Data Bank.

---

## ✨ Fitur Utama

- 📥 **Unduh Konten** — Video, gambar, musik dari TikTok & Douyin
- 💬 **Ekstrak Data** — Detail video, komentar, profil pengguna, tren
- 🗄️ **Data Bank (PostgreSQL)** — Penyimpanan data terpusat secara otomatis
- 📊 **Statistik Data** — Lihat jumlah data tersimpan per kategori
- 📑 **Ekspor ke Excel** — Ekspor data ke `.xlsx` dengan header bergaya dan filter
- 🌐 **Mode API** — REST API via FastAPI untuk integrasi dengan sistem lain
- 🖥️ **Mode Terminal** — Antarmuka interaktif berbasis terminal
- 📋 **Mode Monitor** — Pantau clipboard secara otomatis

---

## 🚀 Instalasi

### Prasyarat

- Python 3.12+
- PostgreSQL (opsional, untuk fitur Data Bank)

### Langkah Instalasi

```bash
# Clone repositori
git clone https://github.com/npaujiana/scraper-tiktok.git
cd scraper-tiktok

# Buat virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependensi
pip install -r requirements.txt
# atau
pip install .
```

---

## ⚙️ Konfigurasi

Konfigurasi disimpan di `Volume/settings.json`. File akan otomatis dibuat saat pertama kali menjalankan aplikasi.

### Konfigurasi Data Bank

Untuk mengaktifkan fitur penyimpanan data ke PostgreSQL, ubah pengaturan berikut:

```json
{
    "databank_enabled": true,
    "databank_dsn": "postgresql://postgres:postgres@localhost:5444/tiktok_databank"
}
```

### Membuat Database

```bash
# Buat database PostgreSQL
psql -U postgres -p 5444 -c "CREATE DATABASE tiktok_databank;"
```

Tabel akan dibuat secara otomatis saat aplikasi pertama kali terhubung ke database.

---

## 📖 Cara Penggunaan

### Menjalankan Aplikasi

```bash
python main.py
```

### Menu Utama

Setelah menjalankan aplikasi, pilih mode yang diinginkan:

| No | Mode | Keterangan |
|----|------|------------|
| 1-4 | Cookie | Atur Cookie untuk Douyin/TikTok |
| 5 | Terminal Interaktif | Mode pengunduhan utama |
| 6 | Monitor Clipboard | Pantau clipboard otomatis |
| 7 | Web API | REST API di `http://localhost:5555` |

### Mode Terminal Interaktif

Di dalam mode terminal, tersedia berbagai pilihan:

- Unduh video/gambar secara batch atau satuan
- Ekstrak data komentar, pengguna, tren
- **📊 Statistik Data Bank** — Lihat ringkasan data tersimpan
- **📑 Ekspor Data ke Excel** — Pilih kategori dan ekspor ke `.xlsx`

### Mode API

Akses dokumentasi API di:
- Swagger UI: `http://localhost:5555/docs`
- ReDoc: `http://localhost:5555/redoc`

Endpoint utama:

| Metode | Endpoint | Fungsi |
|--------|----------|--------|
| POST | `/extract` | Ekstrak data dari tautan |
| POST | `/douyin/detail` | Detail video Douyin |
| POST | `/douyin/comment` | Komentar video Douyin |
| POST | `/douyin/account` | Data akun Douyin |
| POST | `/tiktok/detail` | Detail video TikTok |

---

## 🗄️ Data Bank

Fitur Data Bank menyimpan semua data yang diekstrak ke PostgreSQL secara otomatis dan paralel dengan penyimpanan file biasa.

### Tabel Database

| Tabel | Isi |
|-------|-----|
| `contents` | Video, gambar, dan konten lainnya |
| `comments` | Komentar pada video |
| `users` | Profil pengguna |
| `search_users` | Hasil pencarian pengguna |
| `search_lives` | Hasil pencarian siaran langsung |
| `hot_trends` | Data tren populer |

### Fitur Utama Data Bank

- **Upsert Otomatis** — Data duplikat diperbarui, bukan ditambahkan ulang
- **Connection Pooling** — Koneksi async via `asyncpg` untuk performa tinggi
- **Ekspor Excel** — Multi-sheet, header bergaya, kolom otomatis
- **Statistik** — Ringkasan jumlah data per tabel

---

## 📁 Struktur Proyek

```
scraper-tiktok/
├── main.py                          # Entry point
├── pyproject.toml                   # Konfigurasi proyek & dependensi
├── Volume/
│   └── settings.json                # File konfigurasi
├── src/
│   ├── application/
│   │   ├── main_terminal.py         # Mode terminal interaktif
│   │   ├── main_server.py           # Mode Web API
│   │   └── main_monitor.py          # Mode monitor clipboard
│   ├── config/
│   │   ├── settings.py              # Manajemen konfigurasi
│   │   └── parameter.py             # Parameter aplikasi
│   ├── databank/                    # Modul Data Bank (baru)
│   │   ├── __init__.py
│   │   ├── models.py                # Skema tabel PostgreSQL
│   │   ├── database.py              # Operasi database async
│   │   └── exporter.py              # Ekspor data ke Excel
│   ├── extract/
│   │   └── extractor.py             # Pengekstrak data konten
│   ├── downloader/                  # Pengunduh file
│   ├── interface/                   # Antarmuka API TikTok/Douyin
│   └── ...
```

---

## 🛠️ Dependensi Utama

| Paket | Fungsi |
|-------|--------|
| `httpx` | HTTP client async |
| `fastapi` | Framework Web API |
| `asyncpg` | Driver PostgreSQL async |
| `openpyxl` | Baca/tulis file Excel |
| `rich` | Antarmuka terminal yang indah |
| `uvicorn` | Server ASGI |

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [GNU General Public License v3.0](LICENSE).

Berdasarkan proyek asli [TikTokDownloader](https://github.com/JoeanAmier/TikTokDownloader) oleh [JoeanAmier](https://github.com/JoeanAmier).

---

## 🙏 Kredit

- Proyek asli: [JoeanAmier/TikTokDownloader](https://github.com/JoeanAmier/TikTokDownloader)
- Modifikasi Data Bank: [npaujiana](https://github.com/npaujiana)
