"""
CIHI Hospitalization Data Inspection

Purpose:
    Inspect the downloaded CIHI hospitalization workbook before cleaning.

Input:
    data/raw/demand/

Output:
    Console inspection report only.
"""

from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RAW_DIR = Path("data/raw/demand")


# ============================================================
# FIND EXCEL FILE
# ============================================================

excel_files = list(RAW_DIR.glob("*.xlsx")) + list(RAW_DIR.glob("*.xls"))

if not excel_files:
    raise FileNotFoundError(
        f"No Excel workbook found in: {RAW_DIR.resolve()}"
    )

if len(excel_files) > 1:
    print("Multiple Excel files found:")
    for i, file in enumerate(excel_files, 1):
        print(f"{i}. {file.name}")

    print("\nUsing the first workbook:")
    
input_file = excel_files[0]


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("CIHI HOSPITALIZATION DATA INSPECTION")
print("=" * 70)

print(f"\nInput file:")
print(input_file)

print(f"\nFile size:")
print(f"{input_file.stat().st_size / (1024 * 1024):.2f} MB")


# ============================================================
# WORKBOOK SHEETS
# ============================================================

excel = pd.ExcelFile(input_file)

print("\n--- SHEETS ---")
for i, sheet in enumerate(excel.sheet_names, 1):
    print(f"{i:>3}. {sheet}")


# ============================================================
# INSPECT EACH SHEET
# ============================================================

print("\n--- SHEET INSPECTION ---")

for sheet in excel.sheet_names:

    print("\n" + "-" * 70)
    print(f"SHEET: {sheet}")
    print("-" * 70)

    try:
        df = pd.read_excel(
            input_file,
            sheet_name=sheet,
            header=None
        )

        print(f"Shape: {df.shape}")

        print("\nFirst 10 rows:")
        print(df.head(10).to_string(index=False, header=False))

    except Exception as e:
        print(f"ERROR reading sheet: {e}")


# ============================================================
# IDENTIFY LIKELY DATA SHEETS
# ============================================================

print("\n" + "=" * 70)
print("POTENTIAL DATA SHEETS")
print("=" * 70)

keywords = [
    "hospital",
    "hospitalization",
    "stay",
    "childbirth",
    "discharge",
    "rate",
    "length"
]

for sheet in excel.sheet_names:

    sheet_lower = sheet.lower()

    if any(keyword in sheet_lower for keyword in keywords):
        print(f"Potential data sheet: {sheet}")


# ============================================================
# DETAILED INSPECTION OF EACH SHEET
# ============================================================

print("\n" + "=" * 70)
print("COLUMN / YEAR / JURISDICTION INSPECTION")
print("=" * 70)

for sheet in excel.sheet_names:

    try:
        df = pd.read_excel(
            input_file,
            sheet_name=sheet
        )

        print("\n" + "-" * 70)
        print(f"SHEET: {sheet}")
        print("-" * 70)

        print(f"Shape: {df.shape}")

        print("\nColumns:")

        for i, col in enumerate(df.columns, 1):
            print(f"{i:>3}. {col}")

        # ----------------------------------------------------
        # Potential year columns
        # ----------------------------------------------------

        year_columns = []

        for col in df.columns:

            col_str = str(col)

            if (
                "year" in col_str.lower()
                or "period" in col_str.lower()
                or "fiscal" in col_str.lower()
            ):
                year_columns.append(col)

        if year_columns:

            print("\nPotential year columns:")

            for col in year_columns:
                print(f"  {col}")

                values = (
                    df[col]
                    .dropna()
                    .astype(str)
                    .drop_duplicates()
                    .tolist()
                )

                print(f"  Values: {values[:30]}")

        # ----------------------------------------------------
        # Potential jurisdiction columns
        # ----------------------------------------------------

        jurisdiction_columns = []

        jurisdiction_keywords = [
            "province",
            "territory",
            "jurisdiction",
            "region"
        ]

        for col in df.columns:

            col_str = str(col).lower()

            if any(
                keyword in col_str
                for keyword in jurisdiction_keywords
            ):
                jurisdiction_columns.append(col)

        if jurisdiction_columns:

            print("\nPotential jurisdiction columns:")

            for col in jurisdiction_columns:
                print(f"  {col}")

                values = (
                    df[col]
                    .dropna()
                    .astype(str)
                    .drop_duplicates()
                    .tolist()
                )

                print(f"  Values: {values[:30]}")

        # ----------------------------------------------------
        # Missing values
        # ----------------------------------------------------

        print("\nMissing values:")

        missing = df.isna().sum()

        missing = missing[missing > 0]

        if len(missing) == 0:
            print("  None")

        else:
            print(missing.to_string())

        # ----------------------------------------------------
        # Duplicate rows
        # ----------------------------------------------------

        print(f"\nDuplicate rows: {df.duplicated().sum()}")

    except Exception as e:
        print(f"\nERROR inspecting {sheet}: {e}")


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("CIHI HOSPITALIZATION DATA INSPECTION COMPLETE")
print("=" * 70)