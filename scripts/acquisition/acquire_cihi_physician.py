# scripts/acquisition/acquire_cihi_physician.py

from pathlib import Path
import requests


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "workforce"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "cihi_physicians_2001_2024.xlsx"
)


# ============================================================
# SOURCE
# ============================================================

SOURCE_URL = (
    "https://www.cihi.ca/sites/default/files/document/"
    "supply-distribution-migration-physicians-in-canada-"
    "2001-2024-data-tables-en.xlsx"
)


# ============================================================
# ACQUISITION
# ============================================================

print("=" * 70)
print("CIHI PHYSICIAN DATA ACQUISITION")
print("=" * 70)

print(f"\nSource:")
print(SOURCE_URL)

print(f"\nOutput:")
print(OUTPUT_FILE)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DOWNLOAD
# ============================================================

print("\n" + "-" * 70)
print("DOWNLOADING")
print("-" * 70)

response = requests.get(
    SOURCE_URL,
    timeout=60
)

response.raise_for_status()


# ============================================================
# VALIDATE RESPONSE
# ============================================================

content_type = response.headers.get(
    "Content-Type",
    ""
)

if not response.content:
    raise ValueError(
        "Downloaded file is empty."
    )


if not (
    "spreadsheet" in content_type.lower()
    or SOURCE_URL.lower().endswith(".xlsx")
):
    raise ValueError(
        f"Unexpected content type: {content_type}"
    )


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.write_bytes(
    response.content
)


# ============================================================
# VERIFY
# ============================================================

if not OUTPUT_FILE.exists():
    raise FileNotFoundError(
        f"Output file was not created:\n{OUTPUT_FILE}"
    )


file_size_mb = (
    OUTPUT_FILE.stat().st_size
    / 1024
    / 1024
)

if file_size_mb == 0:
    raise ValueError(
        "Output file is empty."
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("CIHI PHYSICIAN DATA ACQUISITION COMPLETE")
print("=" * 70)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(
    f"\nFile size: "
    f"{file_size_mb:.2f} MB"
)

print("\n" + "=" * 70)