from pathlib import Path
from zipfile import ZipFile
from io import BytesIO

import numpy as np
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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "spending"
)

OUTPUT_FILE = OUTPUT_DIR / "nhex_health_expenditure.csv"


# =========================================================
# Load source table
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
    .str.lower()
    .str.replace(" ", "_")
)


# =========================================================
# Remove metadata rows
# =========================================================

df = df[
    df["year"].apply(
        lambda x: isinstance(
            x,
            (int, float, np.integer, np.floating),
        )
    )
].copy()

df["year"] = df["year"].astype(int)


# =========================================================
# Standardize financial fields
# =========================================================

financial_columns = [
    "current_dollars",
    "current_dollars_per_capita",
    "constant_2010_dollars",
    "constant_2010_dollars_per_capita",
]

for column in financial_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )


# =========================================================
# Restrict to Total Use of Funds
# =========================================================

total_df = df[
    df["use_of_funds"].eq("Total")
].copy()


# =========================================================
# Keep only required fields
# =========================================================

total_df = total_df[
    [
        "year",
        "forecast_category",
        "province",
        "sector",
        "current_dollars",
        "current_dollars_per_capita",
        "constant_2010_dollars",
        "constant_2010_dollars_per_capita",
    ]
].copy()


# =========================================================
# Pivot sector values
# =========================================================

processed = (
    total_df
    .pivot_table(
        index=[
            "year",
            "province",
            "forecast_category",
        ],
        columns="sector",
        values=[
            "current_dollars",
            "current_dollars_per_capita",
            "constant_2010_dollars",
            "constant_2010_dollars_per_capita",
        ],
        aggfunc="first",
    )
    .reset_index()
)


# =========================================================
# Flatten MultiIndex columns
# =========================================================

processed.columns = [
    "_".join(
        [
            str(part)
            for part in column
            if str(part) != ""
        ]
    ).strip("_")
    if isinstance(column, tuple)
    else str(column)
    for column in processed.columns
]


# =========================================================
# Rename sector columns
# =========================================================

rename_map = {
    # Current dollars
    "current_dollars_Public":
        "public_total",

    "current_dollars_Private":
        "private_total",

    "current_dollars_Provincial Government":
        "provincial_government_total",

    "current_dollars_Territorial Government":
        "territorial_government_total",

    # Current dollars per capita
    "current_dollars_per_capita_Public":
        "public_per_capita",

    "current_dollars_per_capita_Private":
        "private_per_capita",

    "current_dollars_per_capita_Provincial Government":
        "provincial_government_per_capita",

    "current_dollars_per_capita_Territorial Government":
        "territorial_government_per_capita",

    # Constant 2010 dollars
    "constant_2010_dollars_Public":
        "public_constant_2010",

    "constant_2010_dollars_Private":
        "private_constant_2010",

    "constant_2010_dollars_Provincial Government":
        "provincial_government_constant_2010",

    "constant_2010_dollars_Territorial Government":
        "territorial_government_constant_2010",

    # Constant 2010 dollars per capita
    "constant_2010_dollars_per_capita_Public":
        "public_constant_2010_per_capita",

    "constant_2010_dollars_per_capita_Private":
        "private_constant_2010_per_capita",

    "constant_2010_dollars_per_capita_Provincial Government":
        "provincial_government_constant_2010_per_capita",

    "constant_2010_dollars_per_capita_Territorial Government":
        "territorial_government_constant_2010_per_capita",
}

processed = processed.rename(
    columns=rename_map
)


# =========================================================
# Calculate total health expenditure
# =========================================================
#
# NHEX Total = Public + Private
#
# This is the top-level financing reconciliation
# established during validation.
# =========================================================

processed["total_health_expenditure"] = (
    processed["public_total"]
    + processed["private_total"]
)


# =========================================================
# Calculate total expenditure per capita
# =========================================================

processed["total_health_expenditure_per_capita"] = (
    processed["public_per_capita"]
    + processed["private_per_capita"]
)


# =========================================================
# Calculate financing shares
# =========================================================

processed["public_share_pct"] = (
    processed["public_total"]
    / processed["total_health_expenditure"]
    * 100
)

processed["private_share_pct"] = (
    processed["private_total"]
    / processed["total_health_expenditure"]
    * 100
)


# =========================================================
# Validate financing shares
# =========================================================

share_sum = (
    processed["public_share_pct"]
    + processed["private_share_pct"]
)

share_difference = (
    share_sum - 100
).abs()

if share_difference.max() > 0.01:
    raise ValueError(
        "Public and private financing shares do not "
        "sum to approximately 100%."
    )


# =========================================================
# Calculate growth indicators
# =========================================================

processed = processed.sort_values(
    ["province", "year"]
).reset_index(drop=True)


processed["total_health_expenditure_growth_pct"] = (
    processed
    .groupby("province")["total_health_expenditure"]
    .pct_change()
    * 100
)


processed["total_health_expenditure_per_capita_growth_pct"] = (
    processed
    .groupby("province")[
        "total_health_expenditure_per_capita"
    ]
    .pct_change()
    * 100
)


# =========================================================
# Data-quality validation
# =========================================================

expected_key_columns = [
    "year",
    "province",
    "forecast_category",
]

if processed[expected_key_columns].duplicated().any():
    raise ValueError(
        "Duplicate province-year records detected."
    )


if processed["total_health_expenditure"].isna().any():
    raise ValueError(
        "Missing total health expenditure values detected."
    )


# =========================================================
# Reorder columns
# =========================================================

column_order = [
    "year",
    "province",
    "forecast_category",

    "total_health_expenditure",
    "total_health_expenditure_per_capita",

    "public_total",
    "public_per_capita",
    "public_share_pct",

    "private_total",
    "private_per_capita",
    "private_share_pct",

    "provincial_government_total",
    "provincial_government_per_capita",

    "territorial_government_total",
    "territorial_government_per_capita",

    "constant_2010_dollars",
    "constant_2010_dollars_per_capita",

    "public_constant_2010",
    "public_constant_2010_per_capita",

    "private_constant_2010",
    "private_constant_2010_per_capita",

    "provincial_government_constant_2010",
    "provincial_government_constant_2010_per_capita",

    "territorial_government_constant_2010",
    "territorial_government_constant_2010_per_capita",

    "total_health_expenditure_growth_pct",
    "total_health_expenditure_per_capita_growth_pct",
]


# =========================================================
# Keep only columns that actually exist
# =========================================================

column_order = [
    column
    for column in column_order
    if column in processed.columns
]

processed = processed[column_order]


# =========================================================
# Save processed dataset
# =========================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

processed.to_csv(
    OUTPUT_FILE,
    index=False,
)


# =========================================================
# Final report
# =========================================================

print("=" * 70)
print("CIHI NHEX 2025 — TRANSFORMATION COMPLETE")
print("=" * 70)

print("\n1. OUTPUT")
print("-" * 70)
print(OUTPUT_FILE)

print("\n2. SHAPE")
print("-" * 70)
print(f"Rows: {processed.shape[0]:,}")
print(f"Columns: {processed.shape[1]:,}")

print("\n3. YEAR RANGE")
print("-" * 70)
print(f"Minimum year: {processed['year'].min()}")
print(f"Maximum year: {processed['year'].max()}")

print("\n4. PROVINCES / JURISDICTIONS")
print("-" * 70)
print(
    processed["province"]
    .drop_duplicates()
    .sort_values()
    .to_string(index=False)
)

print("\n5. FORECAST CATEGORY")
print("-" * 70)
print(
    processed["forecast_category"]
    .value_counts()
    .sort_index()
)

print("\n6. TOTAL HEALTH EXPENDITURE")
print("-" * 70)
print(
    processed[
        [
            "year",
            "province",
            "total_health_expenditure",
            "total_health_expenditure_per_capita",
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\n7. FINANCING SHARES")
print("-" * 70)
print(
    processed[
        [
            "year",
            "province",
            "public_share_pct",
            "private_share_pct",
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\n8. MISSING VALUES")
print("-" * 70)

print(
    processed.isna()
    .sum()
    .sort_values(ascending=False)
    .head(15)
)

print("\n9. FINAL DATASET PREVIEW")
print("-" * 70)

print(
    processed.head(5).to_string(index=False)
)

print("\n" + "=" * 70)
print("NHEX PROCESSED DATASET CREATED SUCCESSFULLY")
print("=" * 70)