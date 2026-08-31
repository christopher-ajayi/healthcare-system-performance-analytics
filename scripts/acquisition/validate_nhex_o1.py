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
# Validation header
# =========================================================

print("=" * 70)
print("CIHI NHEX 2025 — TABLE O.1 VALIDATION")
print("=" * 70)


# =========================================================
# 1. Initial shape
# =========================================================

print("\n1. INITIAL DATASET")
print("-" * 70)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")


# =========================================================
# 2. Identify actual observations
# =========================================================

print("\n2. ACTUAL OBSERVATIONS")
print("-" * 70)

numeric_year = pd.to_numeric(df["Year"], errors="coerce")

actual_mask = numeric_year.notna()

actual_df = df.loc[actual_mask].copy()

metadata_df = df.loc[~actual_mask].copy()

print(f"Actual observations: {len(actual_df):,}")
print(f"Metadata rows: {len(metadata_df):,}")

print("\nMetadata rows:")

print(
    df.loc[~actual_mask, "Year"]
    .to_string(index=False)
)


# =========================================================
# 3. Convert Year temporarily for validation
# =========================================================

actual_df["Year"] = pd.to_numeric(
    actual_df["Year"],
    errors="coerce"
).astype("Int64")


print("\n3. YEAR VALIDATION")
print("-" * 70)

print(f"Minimum year: {actual_df['Year'].min()}")
print(f"Maximum year: {actual_df['Year'].max()}")

print("\nYear frequency:")

print(
    actual_df["Year"]
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# 4. Forecast category
# =========================================================

print("\n4. FORECAST CATEGORY")
print("-" * 70)

print(
    actual_df["Forecast Category"]
    .value_counts(dropna=False)
    .to_string()
)


# =========================================================
# 5. Provinces / jurisdictions
# =========================================================

print("\n5. PROVINCES / JURISDICTIONS")
print("-" * 70)

provinces = (
    actual_df["Province"]
    .dropna()
    .drop_duplicates()
    .sort_values()
)

print(
    provinces.to_string(index=False)
)

print(
    f"\nNumber of provinces/territories + Canada: "
    f"{len(provinces)}"
)


# =========================================================
# 6. Sectors
# =========================================================

print("\n6. SECTORS")
print("-" * 70)

print(
    actual_df["Sector"]
    .value_counts(dropna=False)
    .to_string()
)


# =========================================================
# 7. Use of Funds
# =========================================================

print("\n7. USE OF FUNDS")
print("-" * 70)

print(
    actual_df["Use of Funds"]
    .value_counts(dropna=False)
    .to_string()
)


# =========================================================
# 8. Sector × Use of Funds combinations
# =========================================================

print("\n8. SECTOR × USE OF FUNDS")
print("-" * 70)

sector_use = (
    actual_df[
        ["Sector", "Use of Funds"]
    ]
    .drop_duplicates()
    .sort_values(
        ["Sector", "Use of Funds"]
    )
)

print(
    sector_use.to_string(index=False)
)


# =========================================================
# 9. Financial columns
# =========================================================

financial_columns = [
    "Current dollars",
    "Current dollars per capita",
    "Constant 2010 dollars",
    "Constant 2010 dollars per capita",
]


print("\n9. FINANCIAL FIELD VALIDATION")
print("-" * 70)


for column in financial_columns:

    numeric_values = pd.to_numeric(
        actual_df[column],
        errors="coerce"
    )

    print(f"\n{column}")

    print(
        f"  Numeric values: "
        f"{numeric_values.notna().sum():,}"
    )

    print(
        f"  Non-numeric / unavailable: "
        f"{numeric_values.isna().sum():,}"
    )

    print(
        f"  Minimum numeric value: "
        f"{numeric_values.min()}"
    )

    print(
        f"  Maximum numeric value: "
        f"{numeric_values.max()}"
    )


# =========================================================
# 10. Missing values
# =========================================================

print("\n10. MISSING VALUES — ACTUAL OBSERVATIONS")
print("-" * 70)

print(
    actual_df.isna()
    .sum()
    .to_string()
)


# =========================================================
# 11. Duplicate records
# =========================================================

print("\n11. DUPLICATE RECORDS")
print("-" * 70)

dimension_columns = [
    "Year",
    "Forecast Category",
    "Province",
    "Sector",
    "Use of Funds",
]

duplicate_mask = actual_df.duplicated(
    subset=dimension_columns,
    keep=False,
)

duplicate_count = duplicate_mask.sum()

print(
    f"Duplicate dimension records: "
    f"{duplicate_count:,}"
)


if duplicate_count > 0:

    print("\nDuplicate records:")

    print(
        actual_df.loc[
            duplicate_mask,
            dimension_columns
        ]
        .sort_values(dimension_columns)
        .to_string(index=False)
    )


# =========================================================
# 12. Province-year coverage
# =========================================================

print("\n12. PROVINCE / YEAR COVERAGE")
print("-" * 70)

province_year_counts = (
    actual_df
    .groupby(
        ["Province", "Year"],
        dropna=False
    )
    .size()
)

print(
    province_year_counts
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# 13. Records per year
# =========================================================

print("\n13. RECORDS PER YEAR")
print("-" * 70)

records_per_year = (
    actual_df
    .groupby("Year")
    .size()
)

print(
    records_per_year
    .to_string()
)


# =========================================================
# 14. Forecast years
# =========================================================

print("\n14. FORECAST YEARS")
print("-" * 70)

forecast_df = actual_df[
    actual_df["Forecast Category"] == "f"
]

actual_category_df = actual_df[
    actual_df["Forecast Category"] == ".."
]

print(
    f"Actual records: "
    f"{len(actual_category_df):,}"
)

print(
    f"Forecast records: "
    f"{len(forecast_df):,}"
)


if not forecast_df.empty:

    print(
        f"Forecast minimum year: "
        f"{forecast_df['Year'].min()}"
    )

    print(
        f"Forecast maximum year: "
        f"{forecast_df['Year'].max()}"
    )

    print("\nForecast records by year:")

    print(
        forecast_df["Year"]
        .value_counts()
        .sort_index()
        .to_string()
    )


# =========================================================
# 15. Constant-dollar availability
# =========================================================

print("\n15. CONSTANT-DOLLAR AVAILABILITY")
print("-" * 70)

constant_column = "Constant 2010 dollars"

constant_numeric = pd.to_numeric(
    actual_df[constant_column],
    errors="coerce"
)

constant_available = constant_numeric.notna()

print(
    f"Available: "
    f"{constant_available.sum():,}"
)

print(
    f"Unavailable: "
    f"{(~constant_available).sum():,}"
)

if constant_available.any():

    print(
        f"Earliest year with constant-dollar data: "
        f"{actual_df.loc[constant_available, 'Year'].min()}"
    )

    print(
        f"Latest year with constant-dollar data: "
        f"{actual_df.loc[constant_available, 'Year'].max()}"
    )


# =========================================================
# 16. Per-capita availability
# =========================================================

print("\n16. PER-CAPITA AVAILABILITY")
print("-" * 70)

per_capita_columns = [
    "Current dollars per capita",
    "Constant 2010 dollars per capita",
]


for column in per_capita_columns:

    numeric_values = pd.to_numeric(
        actual_df[column],
        errors="coerce"
    )

    print(
        f"{column}: "
        f"{numeric_values.notna().sum():,} available / "
        f"{numeric_values.isna().sum():,} unavailable"
    )


# =========================================================
# 17. Negative values
# =========================================================

print("\n17. NEGATIVE FINANCIAL VALUES")
print("-" * 70)

for column in financial_columns:

    numeric_values = pd.to_numeric(
        actual_df[column],
        errors="coerce"
    )

    negative_count = (
        numeric_values < 0
    ).sum()

    print(
        f"{column}: "
        f"{negative_count:,} negative values"
    )


# =========================================================
# 18. Zero values
# =========================================================

print("\n18. ZERO FINANCIAL VALUES")
print("-" * 70)

for column in financial_columns:

    numeric_values = pd.to_numeric(
        actual_df[column],
        errors="coerce"
    )

    zero_count = (
        numeric_values == 0
    ).sum()

    print(
        f"{column}: "
        f"{zero_count:,} zero values"
    )


# =========================================================
# 19. Sample of actual records
# =========================================================

print("\n19. FIRST 10 ACTUAL RECORDS")
print("-" * 70)

print(
    actual_df
    .head(10)
    .to_string(index=False)
)


# =========================================================
# 20. Sample of latest records
# =========================================================

print("\n20. LAST 10 ACTUAL RECORDS")
print("-" * 70)

print(
    actual_df
    .tail(10)
    .to_string(index=False)
)


# =========================================================
# Completion
# =========================================================

print("\n" + "=" * 70)
print("TABLE O.1 VALIDATION COMPLETE")
print("=" * 70)