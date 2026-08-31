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
# Standardize columns
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
# Clean fields
# =========================================================

df["year"] = pd.to_numeric(
    df["year"],
    errors="coerce",
)

df["current_dollars"] = pd.to_numeric(
    df["current_dollars"],
    errors="coerce",
)

df["current_dollars_per_capita"] = pd.to_numeric(
    df["current_dollars_per_capita"],
    errors="coerce",
)

for column in [
    "province",
    "sector",
    "use_of_funds",
    "forecast_category",
]:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# =========================================================
# Restrict to Total
# =========================================================

total_df = df[
    df["use_of_funds"].eq("Total")
].copy()


# =========================================================
# Header
# =========================================================

print("=" * 70)
print("CIHI NHEX 2025 — SECTOR RELATIONSHIP VALIDATION")
print("=" * 70)


# =========================================================
# 1. Basic Total-level structure
# =========================================================

print("\n1. TOTAL-LEVEL SECTOR STRUCTURE")
print("-" * 70)

print(
    total_df["sector"]
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# 2. Reshape sectors into columns
# =========================================================

relationship_df = (
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
    .pivot(
        index=[
            "year",
            "province",
            "forecast_category",
        ],
        columns="sector",
        values=[
            "current_dollars",
            "current_dollars_per_capita",
        ],
    )
    .reset_index()
)


# Flatten MultiIndex columns
relationship_df.columns = [
    "_".join(
        str(part)
        for part in column
        if str(part) != ""
    ).strip("_")
    if isinstance(column, tuple)
    else str(column)
    for column in relationship_df.columns
]


# =========================================================
# 3. Display resulting structure
# =========================================================

print("\n2. RELATIONSHIP DATASET COLUMNS")
print("-" * 70)

for column in relationship_df.columns:
    print(f"  - {column}")


# =========================================================
# 4. Government relationship
# =========================================================

print("\n3. PUBLIC vs GOVERNMENT RELATIONSHIP")
print("-" * 70)

public_col = "current_dollars_Public"
provincial_col = "current_dollars_Provincial Government"
territorial_col = "current_dollars_Territorial Government"

relationship_df["government_total"] = (
    relationship_df.get(
        provincial_col,
        0,
    ).fillna(0)
    +
    relationship_df.get(
        territorial_col,
        0,
    ).fillna(0)
)


relationship_df["public_minus_government"] = (
    relationship_df[public_col]
    - relationship_df["government_total"]
)


relationship_df["public_equals_government"] = (
    relationship_df["public_minus_government"]
    .abs()
    < 0.01
)


print(
    "Public = Provincial Government + Territorial Government"
)

print(
    relationship_df[
        "public_equals_government"
    ].value_counts()
    .to_string()
)


# =========================================================
# 5. Difference statistics
# =========================================================

print("\n4. PUBLIC − GOVERNMENT DIFFERENCE")
print("-" * 70)

difference = (
    relationship_df[
        "public_minus_government"
    ]
)

print(
    f"Minimum difference: "
    f"{difference.min():,.2f}"
)

print(
    f"Maximum difference: "
    f"{difference.max():,.2f}"
)

print(
    f"Mean difference: "
    f"{difference.mean():,.2f}"
)

print(
    f"Median difference: "
    f"{difference.median():,.2f}"
)


# =========================================================
# 6. Largest differences
# =========================================================

print("\n5. LARGEST PUBLIC / GOVERNMENT DIFFERENCES")
print("-" * 70)

largest_differences = (
    relationship_df[
        [
            "year",
            "province",
            "current_dollars_Public",
            "government_total",
            "public_minus_government",
        ]
    ]
    .assign(
        absolute_difference=lambda x:
            x["public_minus_government"].abs()
    )
    .sort_values(
        "absolute_difference",
        ascending=False,
    )
    .head(20)
)

print(
    largest_differences.to_string(
        index=False
    )
)


# =========================================================
# 7. Private + Public relationship
# =========================================================

print("\n6. PUBLIC + PRIVATE STRUCTURE")
print("-" * 70)

private_col = "current_dollars_Private"

relationship_df["public_plus_private"] = (
    relationship_df[public_col]
    + relationship_df[private_col]
)

print(
    "Public + Private calculated successfully."
)

print(
    relationship_df[
        [
            "year",
            "province",
            public_col,
            private_col,
            "public_plus_private",
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# =========================================================
# 8. Check for missing sector combinations
# =========================================================

print("\n7. MISSING SECTOR COMBINATIONS")
print("-" * 70)

expected_sectors = {
    "Public",
    "Private",
    "Provincial Government",
    "Territorial Government",
}

observed_by_group = (
    total_df
    .groupby(
        [
            "year",
            "province",
        ]
    )["sector"]
    .apply(set)
)

missing_combinations = []

for (year, province), sectors in observed_by_group.items():

    missing = expected_sectors - sectors

    # Some jurisdictions legitimately do not have
    # provincial or territorial government classifications.
    if missing:
        missing_combinations.append(
            {
                "year": year,
                "province": province,
                "missing_sectors": ", ".join(
                    sorted(missing)
                ),
            }
        )

missing_df = pd.DataFrame(
    missing_combinations
)

if missing_df.empty:
    print("No missing sector combinations.")
else:
    print(
        missing_df
        .groupby("missing_sectors")
        .size()
        .sort_values(ascending=False)
        .to_string()
    )


# =========================================================
# 9. Per-capita relationship
# =========================================================

print("\n8. PER-CAPITA RELATIONSHIP")
print("-" * 70)

public_pc = (
    "current_dollars_per_capita_Public"
)

provincial_pc = (
    "current_dollars_per_capita_Provincial Government"
)

territorial_pc = (
    "current_dollars_per_capita_Territorial Government"
)

relationship_df["government_per_capita"] = (
    relationship_df.get(
        provincial_pc,
        0,
    ).fillna(0)
    +
    relationship_df.get(
        territorial_pc,
        0,
    ).fillna(0)
)

relationship_df["pc_difference"] = (
    relationship_df[public_pc]
    - relationship_df["government_per_capita"]
)

relationship_df["pc_equals_government"] = (
    relationship_df["pc_difference"]
    .abs()
    < 0.01
)

print(
    relationship_df[
        "pc_equals_government"
    ]
    .value_counts()
    .to_string()
)


# =========================================================
# 10. Final interpretation summary
# =========================================================

print("\n9. VALIDATION SUMMARY")
print("-" * 70)

total_groups = len(relationship_df)

matching_groups = (
    relationship_df[
        "public_equals_government"
    ].sum()
)

print(
    f"Province-year Total groups: "
    f"{total_groups:,}"
)

print(
    f"Public = government groups: "
    f"{matching_groups:,}"
)

print(
    f"Non-matching groups: "
    f"{total_groups - matching_groups:,}"
)

print(
    "\nThe results above determine whether Public can "
    "be treated as the aggregate government measure."
)

print("\n" + "=" * 70)
print("SECTOR RELATIONSHIP VALIDATION COMPLETE")
print("=" * 70)