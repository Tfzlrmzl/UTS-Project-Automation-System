#!/usr/bin/env python3
"""Online Book Catalog Organizer & Scraper."""

import argparse
import csv
import re
import sys
import zipfile
from decimal import Decimal
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"
BACKUP_DIR = PROJECT_DIR / "backup"
PRICE_PATTERN = re.compile(r"(\d+(?:\.\d{1,2})?)")
CSV_FIELDS = ["title", "price_raw", "price_clean", "category", "url"]


def positive_integer(value):
    """Parse a positive integer for the --limit argument."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("limit harus berupa bilangan bulat") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("limit harus lebih besar dari 0")
    return parsed


def valid_url(value):
    """Accept only absolute HTTP(S) URLs."""
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        parsed.port
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"URL tidak valid: {exc}") from exc
    if parsed.scheme not in {"http", "https"} or not hostname:
        raise argparse.ArgumentTypeError("URL harus berupa alamat HTTP atau HTTPS yang valid")
    return value


def setup_directories():
    """Create project data, output, and backup directories."""
    for directory in (DATA_DIR, OUTPUT_DIR, BACKUP_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def fetch_page(url):
    """Fetch and decode a page, honoring the encoding detected from its content."""
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return BeautifulSoup(response.text, "html.parser")


def scrape_books(base_url, limit):
    """Collect up to limit books, following pagination links when available."""
    print(f"[*] Memulai web scraping dari: {base_url} (Target: {limit} data)...")
    books = []
    current_url = base_url
    visited_urls = set()

    while len(books) < limit and current_url and current_url not in visited_urls:
        visited_urls.add(current_url)
        soup = fetch_page(current_url)

        for item in soup.select("article.product_pod"):
            if len(books) >= limit:
                break

            title_link = item.select_one("h3 a[title][href]")
            price_element = item.select_one("p.price_color")
            if title_link is None or price_element is None:
                print("[!] Melewati entri buku dengan data judul/harga yang tidak lengkap.", file=sys.stderr)
                continue

            title = title_link.get("title", "").strip()
            raw_price = price_element.get_text(strip=True)
            if not title or PRICE_PATTERN.search(raw_price) is None:
                print("[!] Melewati entri buku dengan judul atau harga yang tidak valid.", file=sys.stderr)
                continue

            books.append(
                {
                    "title": title,
                    "price": raw_price,
                    "url": urljoin(current_url, title_link["href"]),
                }
            )

        next_link = soup.select_one("li.next a[href]")
        current_url = urljoin(current_url, next_link["href"]) if next_link else None

    if not books:
        raise ValueError("Tidak ada data buku valid yang berhasil dikumpulkan.")
    if len(books) < limit:
        print(f"[!] Hanya {len(books)} dari {limit} data yang tersedia.")
    else:
        print(f"[+] Berhasil mengumpulkan {len(books)} record buku.")
    return books


def process_and_filter_data(books, keyword):
    """Normalize book data, apply an optional title filter, and write output files."""
    raw_data_path = DATA_DIR / "raw_data.txt"
    csv_output_path = OUTPUT_DIR / "hasil_scraping.csv"
    report_output_path = OUTPUT_DIR / "laporan.txt"
    keyword_regex = re.compile(re.escape(keyword), re.IGNORECASE) if keyword else None
    processed_data = []

    for book in books:
        match = PRICE_PATTERN.search(book["price"])
        if match is None:
            print(f"[!] Harga tidak valid; entri '{book['title']}' dilewati.", file=sys.stderr)
            continue

        price = Decimal(match.group(1))
        if keyword_regex and not keyword_regex.search(book["title"]):
            continue

        processed_data.append(
            {
                "title": book["title"],
                "price_raw": book["price"],
                "price_clean": price,
                "category": "Premium" if price > Decimal("30.00") else "Standard",
                "url": book["url"],
            }
        )

    with raw_data_path.open("w", encoding="utf-8", newline="\n") as raw_file:
        for book in books:
            raw_file.write(
                f"Title: {book['title']} | Price: {book['price']} | URL: {book['url']}\n"
            )

    with csv_output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in processed_data:
            csv_row = row.copy()
            csv_row["price_clean"] = f"{row['price_clean']:.2f}"
            writer.writerow(csv_row)

    total_items = len(processed_data)
    average_price = (
        sum((row["price_clean"] for row in processed_data), Decimal("0")) / total_items
        if total_items
        else Decimal("0")
    )
    report_lines = [
        "=== LAPORAN RINGKASAN AUTOMATION SYSTEMS ===",
        "Tema: Online Book Catalog Organizer",
        f"Keyword Filter: {keyword or 'Tidak ada'}",
        f"Total Record Diproses: {total_items}",
        f"Rata-rata Harga Buku: £{average_price:.2f}",
        "",
        "Rincian Buku:",
    ]
    report_lines.extend(
        f"{index}. {row['title']} - {row['price_raw']} ({row['category']})"
        for index, row in enumerate(processed_data, 1)
    )
    report_output_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"[+] Data mentah disimpan ke: {raw_data_path}")
    print(f"[+] Data terstruktur disimpan ke: {csv_output_path}")
    print(f"[+] Laporan ringkasan disimpan ke: {report_output_path}")
    if keyword and not processed_data:
        print(f"[!] Tidak ada judul yang cocok dengan keyword '{keyword}'.")
    return processed_data


def create_backup_zip():
    """Create a ZIP archive containing processed output and raw input data."""
    backup_path = BACKUP_DIR / "backup_data.zip"
    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(OUTPUT_DIR.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(OUTPUT_DIR))
        raw_data_path = DATA_DIR / "raw_data.txt"
        if raw_data_path.is_file():
            archive.write(raw_data_path, raw_data_path.name)
    print(f"[+] Backup berhasil dibuat di: {backup_path}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Automation Systems - Book Catalog Scraper & Organizer"
    )
    parser.add_argument(
        "--url",
        type=valid_url,
        default="https://books.toscrape.com/",
        help="URL target web scraping (HTTP atau HTTPS)",
    )
    parser.add_argument("--keyword", default="", help="Kata kunci untuk menyaring judul buku")
    parser.add_argument(
        "--limit",
        type=positive_integer,
        default=30,
        help="Jumlah maksimum data yang diambil (default: 30)",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Buat file ZIP backup hasil pemrosesan",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        setup_directories()
        books = scrape_books(args.url, args.limit)
        process_and_filter_data(books, args.keyword.strip())
        if args.backup:
            create_backup_zip()
    except (requests.RequestException, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"[!] Proses gagal: {exc}", file=sys.stderr)
        return 1

    print("\n=== PROSES AUTOMATION SELESAI ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
