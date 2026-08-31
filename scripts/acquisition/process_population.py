from pathlib import Path
from zipfile import ZipFile

import pandas as pd


# =========================================================
# Configuration
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "demographics"
    / "statcan_17100005_raw.zip"
)

RAW_DATA_FILE = "17100005.csv"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "demographics"
)

OUTPUT_FILE = OUTPUT_DIR / "provincial_population_annual.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# Load raw data
# =========================================================

with ZipFile(RAW_FILE, "r") as zip_file:

    with zip_file.open(RAW_DATA_FILE) as file:

        df = pd.read_csv(file)


# =========================================================
# Filter population observations
# =========================================================

population = df[
    (df["UOM"] == "Persons")
    & (df["Gender"] == "Total - gender")
].copy()


# =========================================================
# Total population
# =========================================================

total_population = (
    population[
        population["Age group"] == "All ages"
    ][
        ["REF_DATE", "GEO", "VALUE"]
    ]
    .rename(
        columns={
            "REF_DATE": "year",
            "GEO": "province",
            "VALUE": "population",
        }
    )
)


# =========================================================
# Population 65+
# =========================================================

population_65_plus = (
    population[
        population["Age group"] == "65 years and older"
    ][
        ["REF_DATE", "GEO", "VALUE"]
    ]
    .rename(
        columns={
            "REF_DATE": "year",
            "GEO": "province",
            "VALUE": "population_65_plus",
        }
    )
)


# =========================================================
# Population 80+
# =========================================================

population_80_plus = (
    population[
        population["Age group"].isin(
            [
                "80 to 84 years",
                "85 to 89 years",
                "90 years and older",
            ]
        )
    ]
    .groupby(
        ["REF_DATE", "GEO"],
        as_index=False
    )["VALUE"]
    .sum()
    .rename(
        columns={
            "REF_DATE": "year",
            "GEO": "province",
            "VALUE": "population_80_plus",
        }
    )
)


# =========================================================
# Population 85+
# =========================================================

population_85_plus = (
    population[
        population["Age group"].isin(
            [
                "85 to 89 years",
                "90 years and older",
            ]
        )
    ]
    .groupby(
        ["REF_DATE", "GEO"],
        as_index=False
    )["VALUE"]
    .sum()
    .rename(
        columns={
            "REF_DATE": "year",
            "GEO": "province",
            "VALUE": "population_85_plus",
        }
    )
)


# =========================================================
# Merge demographic measures
# =========================================================

population_annual = (
    total_population
    .merge(
        population_65_plus,
        on=["year", "province"],
        how="left",
    )
    .merge(
        population_80_plus,
        on=["year", "province"],
        how="left",
    )
    .merge(
        population_85_plus,
        on=["year", "province"],
        how="left",
    )
)


# =========================================================
# Calculate demographic shares
# =========================================================

population_annual["population_65_share_pct"] = (
    population_annual["population_65_plus"]
    / population_annual["population"]
    * 100
)

population_annual["population_80_share_pct"] = (
    population_annual["population_80_plus"]
    / population_annual["population"]
    * 100
)

population_annual["population_85_share_pct"] = (
    population_annual["population_85_plus"]
    / population_annual["population"]
    * 100
)


# =========================================================
# Sort
# =========================================================

population_annual = (
    population_annual
    .sort_values(
        ["province", "year"]
    )
    .reset_index(drop=True)
)


# =========================================================
# Validation
# =========================================================

required_columns = [
    "year",
    "province",
    "population",
    "population_65_plus",
    "population_80_plus",
    "population_85_plus",
    "population_65_share_pct",
    "population_80_share_pct",
    "population_85_share_pct",
]

missing_columns = [
    column
    for column in required_columns
    if column not in population_annual.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# Check duplicate province-year records

duplicates = population_annual.duplicated(
    subset=["year", "province"]
).sum()

if duplicates > 0:
    raise ValueError(
        f"Found {duplicates} duplicate province-year records."
    )


# Check population hierarchy

invalid_65 = (
    population_annual["population_65_plus"]
    > population_annual["population"]
).sum()

invalid_80 = (
    population_annual["population_80_plus"]
    > population_annual["population_65_plus"]
).sum()

invalid_85 = (
    population_annual["population_85_plus"]
    > population_annual["population_80_plus"]
).sum()

if invalid_65 or invalid_80 or invalid_85:
    raise ValueError(
        "Invalid population hierarchy detected."
    )


# =========================================================
# Save processed dataset
# =========================================================

population_annual.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# Report
# =========================================================

print("=" * 70)
print("POPULATION PROCESSING COMPLETE")
print("=" * 70)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(f"\nRows: {len(population_annual):,}")
print(f"Columns: {len(population_annual.columns)}")

print(
    f"\nYear range: "
    f"{population_annual['year'].min()}–"
    f"{population_annual['year'].max()}"
)

print(
    f"\nProvinces/territories: "
    f"{population_annual['province'].nunique()}"
)

print("\nColumns:")
print(population_annual.columns.tolist())

print("\nSample:")
print(population_annual.head(10))

print("\nValidation:")
print("✓ Required columns present")
print("✓ No duplicate province-year records")
print("✓ Population hierarchy valid")
print("✓ Processed dataset saved")

print("\n" + "=" * 70)