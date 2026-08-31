from pathlib import Path

import pandas as pd


# =========================================================
# Configuration
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "capacity"
    / "cihi_hospital_beds_2023_2024.xlsx"
)


# =========================================================
# Validation
# =========================================================

if not FILE.exists():
    raise FileNotFoundError(f"File not found:\n{FILE}")


# =========================================================
# Workbook Inspection
# =========================================================

print("=" * 70)
print("CIHI HOSPITAL BEDS 2023–2024 — WORKBOOK INSPECTION")
print("=" * 70)

print("\n1. FILE")
print("-" * 70)
print(FILE)
print(f"File size: {FILE.stat().st_size / (1024 * 1024):.2f} MB")


xls = pd.ExcelFile(FILE)

print("\n2. WORKBOOK SHEETS")
print("-" * 70)

print(f"Number of sheets: {len(xls.sheet_names)}")

for i, sheet in enumerate(xls.sheet_names, start=1):
    print(f"  {i}. {sheet}")


# =========================================================
# Inspect only meaningful cells
# =========================================================

print("\n3. SHEET STRUCTURE")
print("-" * 70)

for sheet in xls.sheet_names:

    df = pd.read_excel(
        xls,
        sheet_name=sheet,
        header=None
    )

    print("\n" + "=" * 70)
    print(f"SHEET: {sheet}")
    print("=" * 70)

    print(f"Shape: {df.shape}")

    # Remove completely empty rows and columns
    cleaned = df.dropna(
        axis=0,
        how="all"
    ).dropna(
        axis=1,
        how="all"
    )

    print(f"Non-empty shape: {cleaned.shape}")

    print("\nFirst 15 non-empty rows:")

    print(
        cleaned.head(15).to_string(
            index=True,
            max_cols=30
        )
    )


print("\n" + "=" * 70)
print("HISTORICAL HOSPITAL BEDS WORKBOOK INSPECTION COMPLETE")
print("=" * 70)