from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen


# ============================================================
# CIHI HOSPITAL BEDS — ACQUISITION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "capacity"
RAW_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_URL = (
    "https://www.cihi.ca/sites/default/files/document/"
    "hospital-beds-2024-2025-data-tables-en.xlsx"
)

OUTPUT_FILE = RAW_DIR / "cihi_hospital_beds_2024_2025.xlsx"


print("=" * 70)
print("CIHI HOSPITAL BEDS 2024–2025 — ACQUISITION")
print("=" * 70)

print("\n1. SOURCE")
print("-" * 70)
print(SOURCE_URL)

print("\n2. OUTPUT")
print("-" * 70)
print(OUTPUT_FILE)


# ============================================================
# DOWNLOAD
# ============================================================

request = Request(
    SOURCE_URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
)

with urlopen(request, timeout=60) as response:
    data = response.read()

OUTPUT_FILE.write_bytes(data)


# ============================================================
# VALIDATE DOWNLOAD
# ============================================================

file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)

if file_size_mb < 0.01:
    raise ValueError(
        "Downloaded file is unexpectedly small."
    )


# XLSX files are ZIP containers and should begin with PK.
if data[:2] != b"PK":
    raise ValueError(
        "Downloaded content does not appear to be a valid XLSX file."
    )


print("\n3. DOWNLOAD")
print("-" * 70)
print("PASS — file downloaded successfully.")

print(f"File size: {file_size_mb:.2f} MB")

print("\n4. ACQUISITION METADATA")
print("-" * 70)
print(f"Acquisition timestamp (UTC): "
      f"{datetime.now(timezone.utc).isoformat()}")

print(f"Source: {SOURCE_URL}")
print(f"Local file: {OUTPUT_FILE}")

print("\n" + "=" * 70)
print("HOSPITAL BEDS ACQUISITION COMPLETE")
print("=" * 70)