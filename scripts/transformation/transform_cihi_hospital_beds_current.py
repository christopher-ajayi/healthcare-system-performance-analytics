# scripts/transformation/transform_cihi_hospital_beds_current.py

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
    / "cihi_hospital_beds_current_clean.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "capacity"
    / "cihi_hospital_beds_current_transformed.csv"
)


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("CIHI CURRENT HOSPITAL BEDS TRANSFORMATION")
print("=" * 70)

print(f"\nInput:\n{INPUT_FILE}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"File not found:\n{INPUT_FILE}")

df = pd.read_csv(INPUT_FILE, dtype=str)


# ============================================================
# KEEP TABLE 1 ONLY
# ============================================================

df = df[df["source_sheet"].eq("Table 1")].copy()


if df.empty:
    raise ValueError("No Table 1 records found.")


# ============================================================
# RENAME POSITIONAL COLUMNS
# ============================================================

column_map = {
    "0": "province",
    "1": "zone",
    "2": "facility",
    "3": "teaching_status",
    "4": "icu_beds",
    "5": "obstetrics_beds",
    "6": "pediatrics_beds",
    "7": "other_acute_care_beds",
    "8": "total_acute_care_beds",
    "9": "mental_health_addictions_beds",
    "10": "rehabilitation_beds",
    "11": "long_term_care_beds",
    "12": "total_beds",
    "13": "beds_per_100k_population",
    "14": "reporting_basis",
}

missing_columns = [
    column for column in column_map
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Expected positional columns are missing: {missing_columns}"
    )

df = df.rename(columns=column_map)


# ============================================================
# REMOVE NON-DATA ROWS
# ============================================================

df["province"] = df["province"].astype(str).str.strip()
df["facility"] = df["facility"].astype(str).str.strip()

df = df[
    df["province"].notna()
    & ~df["province"].isin(["nan", ""])
    & df["facility"].notna()
    & ~df["facility"].isin(["nan", ""])
].copy()


# ============================================================
# STANDARDIZE TEXT
# ============================================================

text_columns = [
    "province",
    "zone",
    "facility",
    "teaching_status",
    "reporting_basis",
]

for column in text_columns:
    df[column] = (
        df[column]
        .replace({"nan": pd.NA, "NaN": pd.NA, "": pd.NA})
        .astype("string")
        .str.strip()
    )


# ============================================================
# STANDARDIZE NUMERIC VARIABLES
# ============================================================

numeric_columns = [
    "icu_beds",
    "obstetrics_beds",
    "pediatrics_beds",
    "other_acute_care_beds",
    "total_acute_care_beds",
    "mental_health_addictions_beds",
    "rehabilitation_beds",
    "long_term_care_beds",
    "total_beds",
    "beds_per_100k_population",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# STANDARDIZE SPECIAL MISSING VALUES
# ============================================================

# CIHI uses "x" where data is suppressed/not available.
# These are treated as missing rather than zero.

# Numeric conversion above already converts "x" to NaN.


# ============================================================
# ADD DATA YEAR
# ============================================================

df["year"] = 2024


# ============================================================
# COLUMN ORDER
# ============================================================

final_columns = [
    "year",
    "province",
    "zone",
    "facility",
    "teaching_status",
    "icu_beds",
    "obstetrics_beds",
    "pediatrics_beds",
    "mental_health_addictions_beds",
    "rehabilitation_beds",
    "long_term_care_beds",
    "other_acute_care_beds",
    "total_acute_care_beds",
    "total_beds",
    "beds_per_100k_population",
    "reporting_basis",
]

df = df[final_columns]


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    ["province", "zone", "facility"]
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CIHI CURRENT HOSPITAL BEDS TRANSFORMATION COMPLETE")
print("=" * 70)

print(f"\nOutput:\n{OUTPUT_FILE}")

print(f"\nRows: {len(df):,}")

print("\nColumns:")
print(df.columns.tolist())

print("\nProvinces/territories:")
print(df["province"].nunique())

print("\nRows by province:")
print(df["province"].value_counts().sort_index())

print("\nMissing values:")
print(df.isna().sum())

print("\nFirst 10 rows:")
print(df.head(10).to_string(index=False))

print("\n" + "=" * 70)