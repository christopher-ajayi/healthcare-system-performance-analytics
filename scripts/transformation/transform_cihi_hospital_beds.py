from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "capacity"
    / "cihi_hospital_beds_clean.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "capacity"
    / "cihi_hospital_beds_transformed.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"File not found:\n{INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    ["province", "year"]
).reset_index(drop=True)


# ============================================================
# BED CHANGE
# ============================================================

df["bed_change"] = (
    df.groupby("province")["total_beds"]
    .diff()
)


# ============================================================
# BED GROWTH %
# ============================================================

df["bed_growth_pct"] = (
    df.groupby("province")["total_beds"]
    .pct_change()
    * 100
)


# ============================================================
# CAPACITY INDEX
# ============================================================

# Index = 100 in the first available year
# for each jurisdiction.

first_bed_value = (
    df.groupby("province")["total_beds"]
    .transform("first")
)

df["bed_capacity_index"] = (
    df["total_beds"]
    / first_bed_value
    * 100
)


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

df = df[
    [
        "year",
        "fiscal_year",
        "province",
        "total_beds",
        "bed_change",
        "bed_growth_pct",
        "bed_capacity_index",
    ]
]


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CIHI HOSPITAL BEDS TRANSFORMATION COMPLETE")
print("=" * 70)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(f"\nRows: {len(df):,}")

print("\nColumns:")
print(df.columns.tolist())

print("\nSample:")
print(
    df.head(15).to_string(index=False)
)

print("\nMissing values:")
print(df.isna().sum())

print("\n" + "=" * 70)