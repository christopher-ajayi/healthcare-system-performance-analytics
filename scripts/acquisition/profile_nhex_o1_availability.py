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
# Clean columns
# =========================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# =========================================================
# Keep actual observations only
# =========================================================

df["Year_numeric"] = pd.to_numeric(
    df["Year"],
    errors="coerce"
)

df = df[
    df["Year_numeric"].notna()
].copy()

df["Year"] = df["Year_numeric"].astype(int)

df.drop(columns=["Year_numeric"], inplace=True)


# =========================================================
# Convert financial fields temporarily
# =========================================================

financial_columns = [
    "Current dollars",
    "Current dollars per capita",
    "Constant 2010 dollars",
    "Constant 2010 dollars per capita",
]

for column in financial_columns:

    df[column + "_numeric"] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# =========================================================
# Header
# =========================================================

print("=" * 70)
print("CIHI NHEX 2025 — O.1 FINANCIAL AVAILABILITY PROFILE")
print("=" * 70)


# =========================================================
# 1. Records by sector and use of funds
# =========================================================

print("\n1. RECORDS BY SECTOR × USE OF FUNDS")
print("-" * 70)

sector_use_counts = (
    df
    .groupby(
        ["Sector", "Use of Funds"]
    )
    .size()
    .reset_index(name="Records")
)

print(
    sector_use_counts
    .to_string(index=False)
)


# =========================================================
# 2. Constant-dollar availability
# =========================================================

print("\n2. CONSTANT-DOLLAR AVAILABILITY BY SECTOR")
print("-" * 70)

constant_sector = (
    df
    .assign(
        Available=df["Constant 2010 dollars_numeric"].notna()
    )
    .groupby("Sector")["Available"]
    .agg(
        Total="size",
        Available="sum"
    )
)

constant_sector["Unavailable"] = (
    constant_sector["Total"]
    - constant_sector["Available"]
)

print(
    constant_sector
    .to_string()
)


# =========================================================
# 3. Constant-dollar availability by use of funds
# =========================================================

print("\n3. CONSTANT-DOLLAR AVAILABILITY BY USE OF FUNDS")
print("-" * 70)

constant_use = (
    df
    .assign(
        Available=df["Constant 2010 dollars_numeric"].notna()
    )
    .groupby("Use of Funds")["Available"]
    .agg(
        Total="size",
        Available="sum"
    )
)

constant_use["Unavailable"] = (
    constant_use["Total"]
    - constant_use["Available"]
)

print(
    constant_use
    .sort_values("Available", ascending=False)
    .to_string()
)


# =========================================================
# 4. Constant-dollar availability by year
# =========================================================

print("\n4. CONSTANT-DOLLAR AVAILABILITY BY YEAR")
print("-" * 70)

constant_year = (
    df
    .assign(
        Available=df["Constant 2010 dollars_numeric"].notna()
    )
    .groupby("Year")["Available"]
    .agg(
        Total="size",
        Available="sum"
    )
)

constant_year["Unavailable"] = (
    constant_year["Total"]
    - constant_year["Available"]
)

print(
    constant_year
    .to_string()
)


# =========================================================
# 5. Exact records containing constant-dollar values
# =========================================================

print("\n5. DIMENSIONS WITH CONSTANT-DOLLAR VALUES")
print("-" * 70)

constant_records = df[
    df["Constant 2010 dollars_numeric"].notna()
].copy()

constant_dimensions = (
    constant_records[
        [
            "Province",
            "Sector",
            "Use of Funds"
        ]
    ]
    .drop_duplicates()
    .sort_values(
        [
            "Province",
            "Sector",
            "Use of Funds"
        ]
    )
)

print(
    constant_dimensions
    .to_string(index=False)
)


# =========================================================
# 6. Zero current-dollar records
# =========================================================

print("\n6. ZERO CURRENT-DOLLAR RECORDS")
print("-" * 70)

zero_records = df[
    df["Current dollars_numeric"] == 0
].copy()

print(
    f"Number of zero records: "
    f"{len(zero_records):,}"
)

print("\nZero records by sector:")

print(
    zero_records["Sector"]
    .value_counts()
    .to_string()
)

print("\nZero records by use of funds:")

print(
    zero_records["Use of Funds"]
    .value_counts()
    .to_string()
)

print("\nZero records:")

print(
    zero_records[
        [
            "Year",
            "Province",
            "Sector",
            "Use of Funds",
            "Current dollars",
            "Current dollars per capita"
        ]
    ]
    .to_string(index=False)
)


# =========================================================
# 7. Current dollars vs per capita
# =========================================================

print("\n7. CURRENT-DOLLAR / PER-CAPITA CONSISTENCY")
print("-" * 70)

valid_pair = (
    df["Current dollars_numeric"].notna()
    &
    df["Current dollars per capita_numeric"].notna()
    &
    (df["Current dollars per capita_numeric"] > 0)
)

print(
    f"Records with both measures available: "
    f"{valid_pair.sum():,}"
)


# =========================================================
# Completion
# =========================================================

print("\n" + "=" * 70)
print("O.1 FINANCIAL AVAILABILITY PROFILE COMPLETE")
print("=" * 70)