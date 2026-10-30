#!/usr/bin/env python3
"""
Aplikasi: Online Book Catalog Organizer & Scraper
Mata Kuliah: Automation Systems
Program Studi Teknik Informatika - Universitas Pelita Bangsa
"""

import argparse
import csv
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


def setup_directories():
    """Membuat folder output, data, dan backup menggunakan pathlib."""
    Path("data").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)
    Path("backup").mkdir(exist_ok=True)


def scrape_books(base_url, limit):
    """Mengambil data buku dari situs web target dengan penanganan error yang andal."""
    print(f"[*] Memulai web scraping dari: {base_url} (Target: {limit} data)...")
    books = []
    page = 1
    
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[!] Kesalahan Koneksi: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all('article', class_='product_pod')

    while len(books) < limit and items:
        for item in items:
            if len(books) >= limit:
                break
            try:
                # Judul Buku
                title = item.h3.a['title']
                
                # Harga Buku
                price_str = item.find('p', class_='price_color').text
                
                # Kategori & Tautan (Akan diambil dari halaman detail jika memungkinkan, atau simulasi link)
                relative_url = item.h3.a['href']
                detail_url = urljoin(base_url, relative_url)
                
                books.append({
                    'title': title,
                    'price': price_str,
                    'url': detail_url
                })
            except AttributeError:
                continue
        
        # Cek halaman berikutnya jika kurang dari limit
        if len(books) < limit:
            next_btn = soup.find('li', class_='next')
            if next_btn and next_btn.a:
                next_page_url = urljoin(base_url, next_btn.a['href'])
                try:
                    res = requests.get(next_page_url, timeout=10)
                    res.raise_for_status()
                    soup = BeautifulSoup(res.text, 'html.parser')
                    items = soup.find_all('article', class_='product_pod')
                    base_url = next_page_url
                except requests.exceptions.RequestException:
                    break
            else:
                break

    if not books:
        print("[!] Peringatan: Tidak ada data yang berhasil dikumpulkan atau data kosong.")
    else:
        print(f"[+] Berhasil mengumpulkan {len(books)} record buku.")
    
    return books


def process_and_filter_data(books, keyword):
    """Memproses data, menerapkan Regular Expressions, dan menyaring berdasarkan keyword."""
    raw_data_path = Path("data/raw_data.txt")
    csv_output_path = Path("output/hasil_scraping.csv")
    report_output_path = Path("output/laporan.txt")

    # 1. Simpan data mentah menggunakan open() & pathlib (Reading and Writing Files)
    with open(raw_data_path, "w", encoding="utf-8") as f:
        for b in books:
            f.write(f"Title: {b['title']} | Price: {b['price']} | URL: {b['url']}\n")
    print(f"[+] Data mentah disimpan ke: {raw_data_path}")

    processed_data = []
    
    # 2. Implementasi Regular Expressions (Minimal 2 pola berbeda)
    # Pola 1: Ekstraksi angka harga dari string mata uang (misal: '£51.77' -> '51.77')
    price_pattern = re.compile(r'([0-9]+\.[0-9]+)')
    
    # Pola 2: Validasi atau pencarian kata kunci khusus pada judul dengan re.IGNORECASE
    keyword_regex = re.compile(re.escape(keyword), re.IGNORECASE) if keyword else None

    for b in books:
        # Validasi/Pembersihan harga dengan RegEx
        price_match = price_pattern.search(b['price'])
        clean_price = float(price_match.group(1)) if price_match else 0.0
        
        # Tentukan kategori harga otomatis
        category = "Premium" if clean_price > 30.0 else "Standard"

        # Filter keyword jika ada
        if keyword_regex and not keyword_regex.search(b['title']):
            continue

        processed_data.append({
            'title': b['title'],
            'price_raw': b['price'],
            'price_clean': clean_price,
            'category': category,
            'url': b['url']
        })

    # 3. Simpan ke CSV
    with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ['title', 'price_raw', 'price_clean', 'category', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in processed_data:
            writer.writerow(row)
    print(f"[+] Data terstruktur disimpan ke: {csv_output_path}")

    # 4. Buat Laporan Ringkasan (.txt)
    total_items = len(processed_data)
    avg_price = sum(r['price_clean'] for r in processed_data) / total_items if total_items > 0 else 0.0

    report_content = f"""=== LAPORAN RINGKASAN AUTOMATION SYSTEMS ===
Tema: Online Book Catalog Organizer
Keyword Filter: {keyword if keyword else 'Tidak ada'}
Total Record Diproses: {total_items}
Rata-rata Harga Buku: £{avg_price:.2f}

Rincian Buku:
"""
    for idx, r in enumerate(processed_data, 1):
        report_content += f"{idx}. {r['title']} - {r['price_raw']} ({r['category']})\n"

    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"[+] Laporan ringkasan disimpan ke: {report_output_path}")

    return processed_data


def create_backup_zip():
    """Membuat backup hasil pemrosesan dalam format .zip (Chapter 11)."""
    backup_path = Path("backup/backup_data.zip")
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in Path("output").rglob("*"):
            if file_path.is_file():
                zipf.write(file_path, file_path.relative_to("output"))
        if Path("data/raw_data.txt").exists():
            zipf.write(Path("data/raw_data.txt"), Path("data/raw_data.txt").name)
    print(f"[+] Backup berhasil dibuat di: {backup_path}")


def main():
    parser = argparse.ArgumentParser(description="Automation Systems - Book Catalog Scraper & Organizer")
    parser.add_argument("--url", default="https://books.toscrape.com/", help="URL target web scraping")
    parser.add_argument("--keyword", default="", help="Kata kunci untuk menyaring judul buku")
    parser.add_argument("--limit", type=int, default=30, help="Jumlah minimum record yang diambil (default: 30)")
    parser.add_argument("--backup", action="store_true", help="Otomatis buat file ZIP backup hasil pemrosesan")

    args = parser.parse_args()

    setup_directories()
    
    # Eksekusi Web Scraping
    books = scrape_books(args.url, args.limit)
    if not books:
        print("[!] Proses dihentikan karena tidak ada data.")
        sys.exit(1)

    # Pemrosesan Data & RegEx
    processed = process_and_filter_data(books, args.keyword)

    # Backup ZIP jika argumen --backup diberikan
    if args.backup:
        create_backup_zip()

    print("\n=== PROSES AUTOMATION SELESAI ===")


if __name__ == "__main__":
    main()
