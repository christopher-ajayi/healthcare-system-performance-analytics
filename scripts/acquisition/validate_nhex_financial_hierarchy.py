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
# Standardize column names
# =========================================================

df.columns = [
    "year",
    "forecast_category",
    "province",
    "sector",
    "use_of_funds",
    "current_dollars",
    "current_dollars_per_capita",
    "constant_2010_dollars",
    "constant_2010_dollars_per_capita",
]


# =========================================================
# Remove metadata rows
# =========================================================

metadata_markers = {
    "Note",
    "f: Forecast.",
    ".. Actual data.",
    "— Data is not applicable or does not exist.",
    "Source",
    "End of worksheet (go to Table of contents)",
}

df = df[
    ~df["year"].astype(str).str.strip().isin(metadata_markers)
].copy()


# =========================================================
# Clean dimensions
# =========================================================

dimension_columns = [
    "province",
    "sector",
    "use_of_funds",
]

for column in dimension_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


df["year"] = pd.to_numeric(
    df["year"],
    errors="coerce",
)


# =========================================================
# Convert financial fields
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
# Header
# =========================================================

print("=" * 70)
print("CIHI NHEX 2025 — FINANCIAL HIERARCHY VALIDATION")
print("=" * 70)


# =========================================================
# 1. Sector structure
# =========================================================

print("\n1. SECTOR STRUCTURE")
print("-" * 70)

print(
    df["sector"]
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# 2. Use-of-funds structure
# =========================================================

print("\n2. USE-OF-FUNDS STRUCTURE")
print("-" * 70)

print(
    df["use_of_funds"]
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# 3. Sector × Use of Funds hierarchy
# =========================================================

print("\n3. SECTOR × USE-OF-FUNDS COMBINATIONS")
print("-" * 70)

sector_use = (
    df[
        [
            "sector",
            "use_of_funds",
        ]
    ]
    .drop_duplicates()
    .sort_values(
        [
            "sector",
            "use_of_funds",
        ]
    )
)

for sector, group in sector_use.groupby("sector"):
    print(f"\n{sector}")

    for use in group["use_of_funds"]:
        print(f"  - {use}")


# =========================================================
# 4. Aggregate categories
# =========================================================

print("\n4. AGGREGATE USE-OF-FUNDS CATEGORIES")
print("-" * 70)

aggregate_categories = [
    "Sub-Total",
    "Total",
]

for category in aggregate_categories:

    records = df[
        df["use_of_funds"].eq(category)
    ]

    print(
        f"{category}: "
        f"{len(records):,} records"
    )


# =========================================================
# 5. Detailed categories
# =========================================================

print("\n5. DETAILED USE-OF-FUNDS CATEGORIES")
print("-" * 70)

detail_categories = [
    x
    for x in df["use_of_funds"].dropna().unique()
    if x not in aggregate_categories
]

for category in sorted(detail_categories):
    print(f"  - {category}")


# =========================================================
# 6. Sector totals by province
# =========================================================

print("\n6. SECTOR TOTAL RECORD STRUCTURE")
print("-" * 70)

sector_totals = (
    df[
        df["use_of_funds"].eq("Total")
    ]
    [
        [
            "province",
            "sector",
            "year",
            "current_dollars",
        ]
    ]
    .sort_values(
        [
            "province",
            "sector",
            "year",
        ]
    )
)

print(
    "\nRecords by sector at Use of Funds = Total:"
)

print(
    sector_totals["sector"]
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# 7. Public vs government relationship
# =========================================================

print("\n7. PUBLIC / GOVERNMENT SECTOR STRUCTURE")
print("-" * 70)

public_sectors = {
    "Public",
    "Provincial Government",
    "Territorial Government",
}

print(
    "Observed public-sector labels:"
)

for sector in sorted(
    set(df["sector"].dropna())
    .intersection(public_sectors)
):
    print(f"  - {sector}")


# =========================================================
# 8. Province-specific government sectors
# =========================================================

print("\n8. GOVERNMENT SECTOR BY JURISDICTION")
print("-" * 70)

government_df = df[
    df["sector"].isin(
        [
            "Provincial Government",
            "Territorial Government",
        ]
    )
]

government_structure = (
    government_df[
        [
            "province",
            "sector",
        ]
    ]
    .drop_duplicates()
    .sort_values(
        [
            "province",
            "sector",
        ]
    )
)

for province, group in government_structure.groupby(
    "province"
):
    sectors = ", ".join(
        group["sector"].tolist()
    )

    print(
        f"{province}: {sectors}"
    )


# =========================================================
# 9. Current-dollar comparison at Total level
# =========================================================

print("\n9. TOTAL EXPENDITURE — SECTOR COMPARISON")
print("-" * 70)

total_df = df[
    df["use_of_funds"].eq("Total")
].copy()

sector_summary = (
    total_df
    .groupby("sector", dropna=False)
    ["current_dollars"]
    .agg(
        records="count",
        total="sum",
    )
    .sort_index()
)

print(
    sector_summary.to_string()
)


# =========================================================
# 10. Check whether Public appears to represent
#     Provincial + Territorial Government + other public
# =========================================================

print(
    "\n10. PUBLIC vs GOVERNMENT TOTAL CHECK"
)
print("-" * 70)

public_total = total_df[
    total_df["sector"].eq("Public")
]

provincial_total = total_df[
    total_df["sector"].eq(
        "Provincial Government"
    )
]

territorial_total = total_df[
    total_df["sector"].eq(
        "Territorial Government"
    )
]

print(
    f"Public records: "
    f"{len(public_total):,}"
)

print(
    f"Provincial Government records: "
    f"{len(provincial_total):,}"
)

print(
    f"Territorial Government records: "
    f"{len(territorial_total):,}"
)


# =========================================================
# 11. Check common province-year coverage
# =========================================================

print(
    "\n11. PROVINCE-YEAR-SECTOR COVERAGE"
)
print("-" * 70)

coverage = (
    total_df
    .groupby(
        [
            "province",
            "year",
        ]
    )
    ["sector"]
    .nunique()
)

print(
    "Sector counts at Use of Funds = Total:"
)

print(
    coverage
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# 12. Check for unexpected sector values
# =========================================================

print(
    "\n12. UNEXPECTED SECTOR VALUES"
)
print("-" * 70)

expected_sectors = {
    "Public",
    "Private",
    "Provincial Government",
    "Territorial Government",
}

unexpected_sectors = sorted(
    set(df["sector"].dropna())
    - expected_sectors
)

if unexpected_sectors:
    for value in unexpected_sectors:
        print(f"  - {value}")
else:
    print("None")


# =========================================================
# 13. Check for unexpected Use-of-Funds values
# =========================================================

print(
    "\n13. UNEXPECTED USE-OF-FUNDS VALUES"
)
print("-" * 70)

expected_use_of_funds = {
    "Hospitals",
    "Other Institutions",
    "Physicians",
    "Other Professionals",
    "Drugs",
    "Public Health",
    "Administration",
    "Other health spending: Home and community care (HCC)",
    "Other Health Spending: Net of HCC",
    "COVID-19 Response Funding",
    "Sub-Total",
    "Capital",
    "Total",
}

unexpected_use = sorted(
    set(df["use_of_funds"].dropna())
    - expected_use_of_funds
)

if unexpected_use:
    for value in unexpected_use:
        print(f"  - {value}")
else:
    print("None")


# =========================================================
# Complete
# =========================================================

print("\n" + "=" * 70)
print("FINANCIAL HIERARCHY VALIDATION COMPLETE")
print("=" * 70)