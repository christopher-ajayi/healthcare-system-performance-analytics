from pathlib import Path
from zipfile import ZipFile
from io import BytesIO

import pandas as pd


# =========================================================
# Configuration
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "spending"
    / "cihi_nhex_2025_raw.zip"
)


TARGET_FILES = [
    "nhex-open-data-2025-en.xlsx",
    "nhex-series-d1-2025-en.xlsx",
    "nhex-series-d4-2025-en.xlsx",
    "nhex-series-f-2025-en.xlsx",
]


# =========================================================
# Inspect workbooks
# =========================================================

print("=" * 70)
print("CIHI NHEX 2025 — WORKBOOK PROFILE")
print("=" * 70)


with ZipFile(RAW_FILE, "r") as zip_file:

    available_files = zip_file.namelist()

    for workbook_name in TARGET_FILES:

        print("\n" + "=" * 70)
        print(workbook_name)
        print("=" * 70)

        if workbook_name not in available_files:

            print("FILE NOT FOUND")
            continue

        workbook_bytes = zip_file.read(workbook_name)

        excel_file = pd.ExcelFile(
            BytesIO(workbook_bytes)
        )

        print("\nSheets:")
        print("-" * 70)

        for sheet in excel_file.sheet_names:

            print(sheet)


print("\n" + "=" * 70)
print("WORKBOOK PROFILE COMPLETE")
print("=" * 70)