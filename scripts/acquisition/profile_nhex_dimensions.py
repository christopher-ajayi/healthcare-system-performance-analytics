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
SHEET = "Table O.1"


# =========================================================
# Load Table O.1
# =========================================================

with ZipFile(RAW_FILE, "r") as zip_file:

    workbook_bytes = zip_file.read(WORKBOOK)

df = pd.read_excel(
    BytesIO(workbook_bytes),
    sheet_name=SHEET,
    header=2,
)


# =========================================================
# Clean column names
# =========================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# =========================================================
# Dimension profile
# =========================================================

print("=" * 70)
print("CIHI NHEX 2025 — TABLE O.1 DIMENSION PROFILE")
print("=" * 70)


print("\nShape:")
print(df.shape)


print("\nColumns:")
print("-" * 70)

for column in df.columns:
    print(column)


# ---------------------------------------------------------
# Years
# ---------------------------------------------------------

print("\nYEAR RANGE")
print("-" * 70)

# Convert only for profiling.
# The original Year column is not modified.

year_numeric = pd.to_numeric(
    df["Year"],
    errors="coerce"
)

print(f"Minimum year: {year_numeric.min():.0f}")
print(f"Maximum year: {year_numeric.max():.0f}")


# ---------------------------------------------------------
# Non-numeric year values
# ---------------------------------------------------------

print("\nNON-NUMERIC YEAR VALUES")
print("-" * 70)

non_numeric_years = (
    df.loc[
        year_numeric.isna() & df["Year"].notna(),
        "Year"
    ]
    .drop_duplicates()
)

if non_numeric_years.empty:
    print("None")
else:
    print(
        non_numeric_years
        .to_string(index=False)
    )


# ---------------------------------------------------------
# Forecast category
# ---------------------------------------------------------

print("\nFORECAST CATEGORY")
print("-" * 70)

print(
    df["Forecast Category"]
    .value_counts(dropna=False)
    .to_string()
)


# ---------------------------------------------------------
# Provinces
# ---------------------------------------------------------

print("\nPROVINCES / JURISDICTIONS")
print("-" * 70)

print(
    df["Province"]
    .drop_duplicates()
    .sort_values()
    .to_string(index=False)
)


# ---------------------------------------------------------
# Sectors
# ---------------------------------------------------------

print("\nSECTORS")
print("-" * 70)

print(
    df["Sector"]
    .value_counts(dropna=False)
    .to_string()
)


# ---------------------------------------------------------
# Use of funds
# ---------------------------------------------------------

print("\nUSE OF FUNDS")
print("-" * 70)

print(
    df["Use of Funds"]
    .value_counts(dropna=False)
    .to_string()
)


# ---------------------------------------------------------
# Missing values
# ---------------------------------------------------------

print("\nMISSING VALUES")
print("-" * 70)

print(
    df.isna()
    .sum()
    .to_string()
)


# ---------------------------------------------------------
# Data types
# ---------------------------------------------------------

print("\nDATA TYPES")
print("-" * 70)

print(df.dtypes)


# ---------------------------------------------------------
# Year value types
# ---------------------------------------------------------

print("\nYEAR VALUE TYPES")
print("-" * 70)

print(
    df["Year"]
    .map(type)
    .value_counts()
    .to_string()
)


# ---------------------------------------------------------
# Year frequency
# ---------------------------------------------------------

print("\nYEAR FREQUENCY")
print("-" * 70)

year_frequency = (
    df["Year"]
    .value_counts(dropna=False)
    .rename("Records")
    .to_frame()
)

year_frequency["_sort_year"] = pd.to_numeric(
    year_frequency.index,
    errors="coerce"
)

year_frequency = (
    year_frequency
    .sort_values(
        by="_sort_year",
        na_position="last"
    )
    .drop(columns="_sort_year")
)

print(year_frequency.to_string())


# ---------------------------------------------------------
# First and last records
# ---------------------------------------------------------

print("\nFIRST 5 RECORDS")
print("-" * 70)

print(
    df.head(5)
    .to_string(index=False)
)


print("\nLAST 5 RECORDS")
print("-" * 70)

print(
    df.tail(5)
    .to_string(index=False)
)


print("\n" + "=" * 70)
print("DIMENSION PROFILE COMPLETE")
print("=" * 70)