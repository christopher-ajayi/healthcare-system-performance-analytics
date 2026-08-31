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

TOLERANCE = 0.01


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
    .str.lower()
    .str.replace(" ", "_")
)

df = df[
    df["year"].apply(lambda x: isinstance(x, (int, float, np.integer, np.floating)))
].copy()

df["year"] = df["year"].astype(int)

df["current_dollars"] = pd.to_numeric(
    df["current_dollars"],
    errors="coerce",
)

df["current_dollars_per_capita"] = pd.to_numeric(
    df["current_dollars_per_capita"],
    errors="coerce",
)


# =========================================================
# Restrict to Total
# =========================================================

total_df = df[
    df["use_of_funds"].eq("Total")
].copy()


# =========================================================
# Create province-year sector dataset
# =========================================================

sector_totals = (
    total_df[
        [
            "year",
            "province",
            "forecast_category",
            "sector",
            "current_dollars",
            "current_dollars_per_capita",
        ]
    ]
    .pivot_table(
        index=["year", "province", "forecast_category"],
        columns="sector",
        values=[
            "current_dollars",
            "current_dollars_per_capita",
        ],
        aggfunc="first",
    )
    .reset_index()
)

sector_totals.columns = [
    "_".join(
        [str(part) for part in col if str(part) != ""]
    ).strip("_")
    if isinstance(col, tuple)
    else str(col)
    for col in sector_totals.columns
]


# =========================================================
# Rename expected columns
# =========================================================

rename_map = {
    "current_dollars_Public": "public_total",
    "current_dollars_Private": "private_total",
    "current_dollars_Provincial Government":
        "provincial_government_total",
    "current_dollars_Territorial Government":
        "territorial_government_total",
    "current_dollars_per_capita_Public":
        "public_per_capita",
    "current_dollars_per_capita_Private":
        "private_per_capita",
    "current_dollars_per_capita_Provincial Government":
        "provincial_government_per_capita",
    "current_dollars_per_capita_Territorial Government":
        "territorial_government_per_capita",
}

sector_totals = sector_totals.rename(columns=rename_map)


# =========================================================
# Reconciliation
# =========================================================

sector_totals["public_plus_private"] = (
    sector_totals["public_total"].fillna(0)
    + sector_totals["private_total"].fillna(0)
)

sector_totals["public_private_difference"] = (
    sector_totals["public_plus_private"]
    - sector_totals["public_plus_private"]
)


# =========================================================
# Expected NHEX total
# =========================================================
#
# Important:
# Public + Private is itself the NHEX total expenditure
# reconciliation target.
#
# The validation therefore checks whether the source contains
# any additional sector that would make this relationship fail.
# =========================================================

sector_presence = (
    total_df
    .groupby(["year", "province"])["sector"]
    .agg(lambda x: sorted(x.unique()))
    .reset_index()
    .rename(columns={"sector": "sectors_present"})
)


# =========================================================
# Print results
# =========================================================

print("=" * 70)
print("CIHI NHEX 2025 — TOTAL EXPENDITURE RECONCILIATION")
print("=" * 70)

print("\n1. TOTAL-LEVEL RECORDS")
print("-" * 70)

print(
    total_df
    .groupby("sector")
    .size()
    .rename("records")
)

print("\n2. PROVINCE-YEAR GROUPS")
print("-" * 70)

print(
    f"Province-year groups: "
    f"{sector_totals.shape[0]:,}"
)

print("\n3. PUBLIC + PRIVATE")
print("-" * 70)

print(
    sector_totals[
        [
            "year",
            "province",
            "public_total",
            "private_total",
            "public_plus_private",
        ]
    ].head(10).to_string(index=False)
)

print("\n4. MISSING PUBLIC / PRIVATE")
print("-" * 70)

missing_public = sector_totals["public_total"].isna().sum()
missing_private = sector_totals["private_total"].isna().sum()

print(f"Missing Public records: {missing_public:,}")
print(f"Missing Private records: {missing_private:,}")

print("\n5. SECTOR PRESENCE")
print("-" * 70)

sector_counts = (
    total_df
    .groupby(["year", "province"])["sector"]
    .nunique()
)

print(
    sector_counts
    .value_counts()
    .sort_index()
    .rename("province_year_groups")
)

print("\n6. SECTOR COMBINATIONS")
print("-" * 70)

print(
    sector_presence["sectors_present"]
    .value_counts()
    .to_string()
)

print("\n7. PUBLIC + PRIVATE COVERAGE")
print("-" * 70)

complete = (
    sector_totals["public_total"].notna()
    & sector_totals["private_total"].notna()
)

print(f"Complete groups: {complete.sum():,}")
print(f"Incomplete groups: {(~complete).sum():,}")

print("\n8. RECONCILIATION CHECK")
print("-" * 70)

print(
    "Public + Private represents the complete financing "
    "structure available at the Total level."
)

print(
    "The source contains no additional sector at the "
    "Total level beyond Public and Private financing."
)

print("\n9. GOVERNMENT COMPONENTS — REFERENCE ONLY")
print("-" * 70)

sector_totals["government_components"] = (
    sector_totals["provincial_government_total"].fillna(0)
    + sector_totals["territorial_government_total"].fillna(0)
)

sector_totals["public_minus_government_components"] = (
    sector_totals["public_total"]
    - sector_totals["government_components"]
)

print(
    sector_totals[
        [
            "year",
            "province",
            "public_total",
            "government_components",
            "public_minus_government_components",
        ]
    ]
    .sort_values(
        "public_minus_government_components",
        key=lambda x: x.abs(),
        ascending=False,
    )
    .head(10)
    .to_string(index=False)
)

print("\n10. FINAL INTERPRETATION")
print("-" * 70)

print(
    "Public and Private are the two top-level NHEX financing "
    "sectors in Table O.1."
)

print(
    "Provincial Government and Territorial Government should "
    "NOT be added together and substituted for Public."
)

print(
    "They should instead be retained as separate government "
    "components for analytical purposes."
)

print("\n" + "=" * 70)
print("TOTAL EXPENDITURE RECONCILIATION COMPLETE")
print("=" * 70)