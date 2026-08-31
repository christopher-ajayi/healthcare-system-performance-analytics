from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# =========================================================
# Configuration
# =========================================================

SOURCE_PAGE = (
    "https://www.cihi.ca/en/"
    "national-health-expenditure-trends/nhex-trends-data"
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "spending"
)

RAW_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = (
    RAW_DIR
    / "cihi_nhex_2025_raw.zip"
)


# =========================================================
# Request official CIHI page
# =========================================================

headers = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/142.0 Safari/537.36"
    ),
    "Accept": "text/html",
}

response = requests.get(
    SOURCE_PAGE,
    headers=headers,
    timeout=60,
)

response.raise_for_status()


# =========================================================
# Parse page
# =========================================================

soup = BeautifulSoup(
    response.text,
    "html.parser",
)


# =========================================================
# Find NHEX ZIP link
# =========================================================

zip_links = []

for link in soup.find_all("a", href=True):

    href = link["href"]
    text = link.get_text(" ", strip=True)

    full_url = urljoin(
        SOURCE_PAGE,
        href,
    )

    if (
        ".zip" in full_url.lower()
        and (
            "download data tables" in text.lower()
            or "nhex" in full_url.lower()
        )
    ):
        zip_links.append(full_url)


if not zip_links:

    raise RuntimeError(
        "Could not find the official NHEX ZIP download "
        "link on the CIHI page."
    )


# Remove duplicates while preserving order

zip_links = list(dict.fromkeys(zip_links))


print("=" * 70)
print("CIHI NHEX — OFFICIAL DOWNLOAD DISCOVERY")
print("=" * 70)

print("\nCandidate ZIP links:")

for url in zip_links:
    print(url)


# =========================================================
# Select first official NHEX ZIP
# =========================================================

download_url = zip_links[0]

print("\nSelected download URL:")
print(download_url)


# =========================================================
# Download
# =========================================================

download_response = requests.get(
    download_url,
    headers={
        "User-Agent": headers["User-Agent"]
    },
    timeout=180,
    stream=True,
)

download_response.raise_for_status()


with open(OUTPUT_FILE, "wb") as file:

    for chunk in download_response.iter_content(
        chunk_size=1024 * 1024
    ):

        if chunk:
            file.write(chunk)


# =========================================================
# Validation
# =========================================================

if not OUTPUT_FILE.exists():
    raise RuntimeError(
        "NHEX file was not created."
    )

file_size_mb = (
    OUTPUT_FILE.stat().st_size
    / (1024 ** 2)
)

if file_size_mb == 0:
    raise RuntimeError(
        "Downloaded NHEX file is empty."
    )


print("\n" + "=" * 70)
print("NHEX ACQUISITION COMPLETE")
print("=" * 70)

print(f"\nSource: CIHI")
print("Dataset: National Health Expenditure Trends, 2025")
print(f"Downloaded: {datetime.now():%Y-%m-%d %H:%M:%S}")
print(f"Output: {OUTPUT_FILE}")
print(f"Size: {file_size_mb:.2f} MB")
print("\nValidation: PASSED")