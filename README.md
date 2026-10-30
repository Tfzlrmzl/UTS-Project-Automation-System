# Online Book Catalog Organizer & Scraper

Aplikasi otomatisasi berbasis Python untuk mengumpulkan, menyaring, mengorganisasi, dan membackup data katalog buku dari web secara otomatis melalui Command Line Interface (CLI). Tugas Ujian Tengah Semester (UTS) Mata Kuliah **Automation Systems**, Program Studi Teknik Informatika, Universitas Pelita Bangsa.

## Anggota Kelompok
1. Haji Tafsil Mujair (Ketua / Anggota)
2. Anggota 2
3. Anggota 3

---

## Fitur Utama & Integrasi Materi
- **Web Scraping (Chapter 13)**: Mengambil minimal 30 data buku dari `https://books.toscrape.com/` menggunakan `requests` dan `BeautifulSoup`.
- **Regular Expressions (Chapter 9)**: Menggunakan `re` untuk ekstraksi nilai harga numerik dan penyaringan judul berdasarkan kata kunci (`--keyword`).
- **File I/O (Chapter 10)**: Membaca dan menyimpan data mentah serta hasil terstruktur ke dalam format `.txt` dan `.csv`.
- **Organisasi File & Backup (Chapter 11)**: Pembuatan direktori otomatis via `pathlib` dan kompresi hasil ke dalam arsip `.zip`.
- **CLI & Error Handling (Chapter 12)**: Penggunaan `argparse` untuk argumen fleksibel serta penanganan kegagalan koneksi & data kosong.

---

## Cara Instalasi & Penggunaan

### 1. Instalasi Dependensi
Pastikan Python telah terinstal, lalu jalankan perintah berikut di terminal:
```bash
pip install -r requirements.txt
```

### 2. Cara Menjalankan Program
Gunakan argumen CLI sesuai kebutuhan:
```bash
python main.py --url https://books.toscrape.com/ --keyword python --limit 30 --backup
```

### Penjelasan Argumen CLI:
- `--url`: Menentukan URL target web scraping.
- `--keyword`: Kata kunci penyaringan judul buku (opsional).
- `--limit`: Jumlah minimum data yang diambil (default: 30).
- `--backup`: Bendera (flag) untuk mengaktifkan pembuatan backup `.zip` otomatis.

---

## Struktur Direktori Proyek
```text
UTS_Project_Kelompok_01/
│
├── main.py
├── requirements.txt
├── README.md
├── data/
│   └── raw_data.txt
├── output/
│   - hasil_scraping.csv
│   - laporan.txt
├── backup/
│   └── backup_data.zip
└── dokumentasi/
    └── laporan_uts.pdf
```
