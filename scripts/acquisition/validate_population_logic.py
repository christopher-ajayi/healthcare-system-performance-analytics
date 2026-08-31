from pathlib import Path
from zipfile import ZipFile

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "demographics"
    / "statcan_17100005_raw.zip"
)

DATA_FILE = "17100005.csv"


# ---------------------------------------------------------
# Load source data
# ---------------------------------------------------------

with ZipFile(RAW_FILE, "r") as zip_file:
    with zip_file.open(DATA_FILE) as file:
        df = pd.read_csv(file)


# ---------------------------------------------------------
# Filter population observations
# ---------------------------------------------------------

population = df[
    (df["UOM"] == "Persons")
    & (df["Gender"] == "Total - gender")
].copy()


# ---------------------------------------------------------
# Check total population
# ---------------------------------------------------------

all_ages = population[
    population["Age group"] == "All ages"
].copy()


print("=" * 70)
print("POPULATION AGGREGATION VALIDATION")
print("=" * 70)

print("\nAll-ages population records:")
print(len(all_ages))

print("\nYears:")
print(
    all_ages["REF_DATE"].min(),
    "to",
    all_ages["REF_DATE"].max()
)


# ---------------------------------------------------------
# Check 65+
# ---------------------------------------------------------

age_65 = population[
    population["Age group"] == "65 years and older"
]

print("\n65+ records:")
print(len(age_65))


# ---------------------------------------------------------
# Check 80+ components
# ---------------------------------------------------------

age_80_components = population[
    population["Age group"].isin(
        [
            "80 to 84 years",
            "85 to 89 years",
            "90 years and older",
        ]
    )
]

print("\n80+ component records:")
print(len(age_80_components))


# ---------------------------------------------------------
# Check 85+ components
# ---------------------------------------------------------

age_85_components = population[
    population["Age group"].isin(
        [
            "85 to 89 years",
            "90 years and older",
        ]
    )
]

print("\n85+ component records:")
print(len(age_85_components))


# ---------------------------------------------------------
# Check geographic coverage
# ---------------------------------------------------------

print("\nGeographies:")
print(
    all_ages["GEO"]
    .drop_duplicates()
    .sort_values()
    .to_string(index=False)
)


# ---------------------------------------------------------
# Check duplicate analytical keys
# ---------------------------------------------------------

key_columns = [
    "REF_DATE",
    "GEO",
    "Gender",
    "Age group",
    "UOM",
]

duplicates = population.duplicated(
    subset=key_columns
).sum()

print("\nDuplicate analytical records:")
print(duplicates)


print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)