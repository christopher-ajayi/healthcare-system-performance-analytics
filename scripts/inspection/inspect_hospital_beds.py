from pathlib import Path

import pandas as pd


# ============================================================
# CIHI HOSPITAL BEDS — RAW WORKBOOK INSPECTION
# ============================================================

print("=" * 70)
print("CIHI HOSPITAL BEDS 2024–2025 — RAW WORKBOOK INSPECTION")
print("=" * 70)


# ============================================================
# 1. PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "capacity"
    / "cihi_hospital_beds_2024_2025.xlsx"
)


# ============================================================
# 2. FILE CHECK
# ============================================================

if not RAW_FILE.exists():
    raise FileNotFoundError(
        f"Raw hospital beds file not found:\n{RAW_FILE}"
    )

print("\n1. FILE")
print("-" * 70)
print(RAW_FILE)

print(f"File size: {RAW_FILE.stat().st_size / (1024 * 1024):.2f} MB")


# ============================================================
# 3. WORKBOOK SHEETS
# ============================================================

print("\n2. WORKBOOK SHEETS")
print("-" * 70)

excel_file = pd.ExcelFile(RAW_FILE)

print(f"Number of sheets: {len(excel_file.sheet_names)}")

for i, sheet in enumerate(excel_file.sheet_names, start=1):
    print(f"{i:>3}. {sheet}")


# ============================================================
# 4. INSPECT EACH SHEET
# ============================================================

print("\n3. SHEET STRUCTURE")
print("-" * 70)

for sheet in excel_file.sheet_names:

    print("\n" + "-" * 70)
    print(f"SHEET: {sheet}")
    print("-" * 70)

    df = pd.read_excel(
        RAW_FILE,
        sheet_name=sheet,
        header=None
    )

    print(f"Shape: {df.shape}")

    print("\nFirst 20 rows:")
    print(
        df.head(20)
        .to_string()
    )


# ============================================================
# 5. FINAL
# ============================================================

print("\n" + "=" * 70)
print("HOSPITAL BEDS WORKBOOK INSPECTION COMPLETE")
print("=" * 70)