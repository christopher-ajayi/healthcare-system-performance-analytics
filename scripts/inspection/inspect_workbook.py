from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
)

FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "capacity"
    / "cihi_hospital_beds_2009_2023_series_d.xlsx"
)


# ============================================================
# HELPERS
# ============================================================

def contains_year(value, start_year=2009, end_year=2023):
    """
    Safely determine whether a cell contains
    one of the target years.
    """
    if pd.isna(value):
        return False

    value = str(value)

    return any(
        str(year) in value
        for year in range(start_year, end_year + 1)
    )


def print_non_empty_rows(df, n=20):
    """
    Print the first n rows containing at least
    one non-empty value.
    """
    non_empty = df.dropna(how="all")

    print(f"Shape: {df.shape}")
    print(f"Non-empty shape: {non_empty.shape}")
    print(f"\nFirst {n} non-empty rows:")

    print(
        non_empty.head(n).to_string(
            index=True,
            max_cols=30
        )
    )


# ============================================================
# FILE VALIDATION
# ============================================================

print("=" * 70)
print("CIHI HISTORICAL HOSPITAL BEDS — WORKBOOK INSPECTION")
print("=" * 70)

print(f"\nFile:")
print(FILE)

if not FILE.exists():
    raise FileNotFoundError(
        f"\nFile not found:\n{FILE}\n\n"
        "Check the filename in data/raw/capacity."
    )

print(f"\nFile size: {FILE.stat().st_size:,} bytes")


# ============================================================
# WORKBOOK LOAD
# ============================================================

excel = pd.ExcelFile(FILE)

print("\n" + "=" * 70)
print("WORKBOOK SHEETS")
print("=" * 70)

print(f"Number of sheets: {len(excel.sheet_names)}")

for i, sheet in enumerate(excel.sheet_names, start=1):
    print(f"  {i}. {sheet}")


# ============================================================
# SHEET INSPECTION
# ============================================================

for sheet in excel.sheet_names:

    print("\n" + "=" * 70)
    print(f"SHEET: {sheet}")
    print("=" * 70)

    df = pd.read_excel(
        FILE,
        sheet_name=sheet,
        header=None
    )

    print_non_empty_rows(df, n=20)


# ============================================================
# YEAR DETECTION
# ============================================================

print("\n" + "=" * 70)
print("YEAR REFERENCES DETECTED")
print("=" * 70)

for sheet in excel.sheet_names:

    df = pd.read_excel(
        FILE,
        sheet_name=sheet,
        header=None
    )

    matches = []

    for row_idx, row in df.iterrows():

        for col_idx, value in row.items():

            if contains_year(value):

                matches.append(
                    (
                        row_idx + 1,
                        col_idx + 1,
                        str(value)
                    )
                )

    if matches:

        print(f"\n{sheet}")
        print("-" * 70)

        for row, col, value in matches[:50]:
            print(
                f"Row {row}, Column {col}: {value}"
            )

        if len(matches) > 50:
            print(
                f"... {len(matches) - 50} additional "
                "year references omitted."
            )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("WORKBOOK INSPECTION COMPLETE")
print("=" * 70)