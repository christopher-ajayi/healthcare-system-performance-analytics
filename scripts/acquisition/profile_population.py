from pathlib import Path
from zipfile import ZipFile

import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

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
# Load data
# ---------------------------------------------------------

with ZipFile(RAW_FILE, "r") as zip_file:

    with zip_file.open(DATA_FILE) as file:

        df = pd.read_csv(file)


# ---------------------------------------------------------
# Profile dimensions
# ---------------------------------------------------------

print("=" * 70)
print("POPULATION DATA — DIMENSION PROFILE")
print("=" * 70)


print("\n1. YEAR RANGE")
print("-" * 70)

print(f"Minimum year: {df['REF_DATE'].min()}")
print(f"Maximum year: {df['REF_DATE'].max()}")


print("\n2. GEOGRAPHIES")
print("-" * 70)

print(
    df["GEO"]
    .drop_duplicates()
    .sort_values()
    .to_string(index=False)
)


print("\n3. GENDER")
print("-" * 70)

print(
    df["Gender"]
    .drop_duplicates()
    .sort_values()
    .to_string(index=False)
)


print("\n4. AGE GROUPS")
print("-" * 70)

print(
    df["Age group"]
    .drop_duplicates()
    .to_string(index=False)
)


print("\n5. UNITS")
print("-" * 70)

print(
    df["UOM"]
    .drop_duplicates()
    .to_string(index=False)
)


print("\n6. RECORD COUNTS BY GENDER")
print("-" * 70)

print(
    df["Gender"]
    .value_counts()
)


print("\n7. RECORD COUNTS BY UNIT")
print("-" * 70)

print(
    df["UOM"]
    .value_counts()
)


print("\n" + "=" * 70)
print("PROFILE COMPLETE")
print("=" * 70)