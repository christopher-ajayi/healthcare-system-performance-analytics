from pathlib import Path
from datetime import datetime

import requests


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

TABLE_ID = "17100005"
LANGUAGE = "en"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "demographics"
RAW_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RAW_DIR / f"statcan_{TABLE_ID}_raw.zip"


# ---------------------------------------------------------
# Statistics Canada WDS endpoint
# ---------------------------------------------------------

WDS_URL = (
    "https://www150.statcan.gc.ca/"
    f"t1/wds/rest/getFullTableDownloadCSV/{TABLE_ID}/{LANGUAGE}"
)


# ---------------------------------------------------------
# Request download URL
# ---------------------------------------------------------

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

response = requests.get(
    WDS_URL,
    headers=headers,
    timeout=60,
)


print(f"Status code: {response.status_code}")
print(f"Response content type: {response.headers.get('Content-Type')}")

if response.status_code != 200:
    print("\nStatistics Canada response:")
    print(response.text[:1000])

response.raise_for_status()

result = response.json()

download_url = result["object"]

print(f"\nOfficial download URL:")
print(download_url)


# ---------------------------------------------------------
# Download the raw file
# ---------------------------------------------------------

download_response = requests.get(
    download_url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=120,
)

download_response.raise_for_status()

OUTPUT_FILE.write_bytes(download_response.content)


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

file_size_mb = OUTPUT_FILE.stat().st_size / (1024 ** 2)

assert OUTPUT_FILE.exists()
assert OUTPUT_FILE.stat().st_size > 0

print("\nPopulation acquisition complete.")
print(f"Source: Statistics Canada")
print(f"Table: {TABLE_ID}")
print(f"Downloaded: {datetime.now():%Y-%m-%d %H:%M:%S}")
print(f"File: {OUTPUT_FILE}")
print(f"Size: {file_size_mb:.2f} MB")
print("Validation: PASSED")