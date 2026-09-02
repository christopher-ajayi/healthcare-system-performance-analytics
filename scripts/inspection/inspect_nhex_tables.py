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


WORKBOOK = "nhex-open-data-2025-en.xlsx"

TARGET_SHEETS = [
    "Table O.1",
    "Table O.2",
]


# =========================================================
# Load workbook
# =========================================================

with ZipFile(RAW_FILE, "r") as zip_file:

    workbook_bytes = zip_file.read(WORKBOOK)

    excel_file = pd.ExcelFile(
        BytesIO(workbook_bytes)
    )


# =========================================================
# Inspect tables
# =========================================================

print("=" * 70)
print("CIHI NHEX 2025 — OPEN DATA TABLE INSPECTION")
print("=" * 70)


for sheet_name in TARGET_SHEETS:

    print("\n" + "=" * 70)
    print(sheet_name)
    print("=" * 70)

    df = pd.read_excel(
        BytesIO(workbook_bytes),
        sheet_name=sheet_name,
        header=None,
    )

    print(f"\nShape: {df.shape}")

    print("\nFirst 25 rows:")
    print("-" * 70)

    print(
        df.head(25).to_string(
            index=True,
            header=False
        )
    )


print("\n" + "=" * 70)
print("TABLE INSPECTION COMPLETE")
print("=" * 70)