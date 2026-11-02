# Online Book Catalog Organizer & Scraper

Aplikasi CLI berbasis Python untuk mengambil, memfilter, dan mengorganisasi data katalog buku dari [Books to Scrape](https://books.toscrape.com/). Proyek ini dibuat untuk tugas Ujian Tengah Semester mata kuliah **Automation Systems**, Program Studi Teknik Informatika, Universitas Pelita Bangsa.

## Fitur

- Mengambil data buku dan mengikuti halaman berikutnya menggunakan `requests` dan `BeautifulSoup`.
- Membersihkan harga dan memfilter judul berdasarkan kata kunci menggunakan regular expression.
- Menyimpan data mentah, hasil CSV, dan laporan ringkasan.
- Membuat arsip ZIP hasil pemrosesan dengan opsi `--backup`.
- Memvalidasi argumen CLI dan melaporkan kegagalan proses.

## Persyaratan

- Python 3
- Dependensi di `requirements.txt`

## Instalasi dan penggunaan

```bash
python -m pip install -r requirements.txt
python main.py --limit 30 --backup
```

Contoh dengan filter judul:

```bash
python main.py --keyword "python" --limit 30
```

Argumen yang tersedia:

| Argumen | Keterangan |
| --- | --- |
| `--url` | URL target HTTP/HTTPS; default `https://books.toscrape.com/`. |
| `--keyword` | Filter judul buku (opsional, tidak membedakan huruf besar/kecil). |
| `--limit` | Jumlah maksimum data yang diambil; default `30`. |
| `--backup` | Membuat arsip ZIP setelah data diproses. |

## Hasil

- `data/raw_data.txt` — data buku mentah.
- `output/hasil_scraping.csv` — data buku terstruktur.
- `output/laporan.txt` — ringkasan hasil pemrosesan.
- `backup/backup_data.zip` — arsip hasil jika opsi `--backup` digunakan.
- `dokumentasi/laporan_uts.pdf` — laporan tugas.

File data dan arsip hasil dibuat saat program berjalan dan tidak disimpan di repository.
