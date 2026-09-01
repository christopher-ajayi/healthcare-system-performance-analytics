from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(
    "data/raw/demand/hospitalizations_1995-2023.xlsx"
)

OUTPUT_FILE = Path(
    "data/processed/demand/cihi_hospitalizations_clean.csv"
)


# ============================================================
# SETUP
# ============================================================

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("CIHI HOSPITALIZATION DATA CLEANING")
print("=" * 70)

print(f"\nInput:")
print(INPUT_FILE)


# ============================================================
# LOAD TABLE 1
# ============================================================

raw = pd.read_excel(
    INPUT_FILE,
    sheet_name="Table 1",
    header=None
)

# First two rows contain title/header information.
df = raw.iloc[1:].copy()

df.columns = [
    "year",
    "jurisdiction",
    "age_group",
    "sex",
    "number_of_discharges",
    "total_length_of_stay_days",
    "average_length_of_stay_days"
]

# Remove header rows and notes
df = df[
    df["year"].notna()
].copy()

# Keep only actual fiscal-year records
df = df[
    df["year"].astype(str).str.match(r"^\d{4}–\d{4}$")
].copy()


# ============================================================
# STANDARDIZE TEXT
# ============================================================

for col in [
    "year",
    "jurisdiction",
    "age_group",
    "sex"
]:
    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
    )


# ============================================================
# STANDARDIZE YEAR
# ============================================================

df["year_start"] = (
    df["year"]
    .str[:4]
    .astype(int)
)

df["year_end"] = (
    df["year"]
    .str[-4:]
    .astype(int)
)


# ============================================================
# STANDARDIZE JURISDICTIONS
# ============================================================

df["jurisdiction"] = (
    df["jurisdiction"]
    .replace({
        "Newfoundland and Labrador": "Newfoundland and Labrador",
        "Prince Edward Island": "Prince Edward Island",
        "Nova Scotia": "Nova Scotia",
        "New Brunswick": "New Brunswick",
        "Quebec": "Quebec",
        "Ontario": "Ontario",
        "Manitoba": "Manitoba",
        "Saskatchewan": "Saskatchewan",
        "Alberta": "Alberta",
        "British Columbia": "British Columbia",
        "Yukon": "Yukon",
        "Northwest Territories": "Northwest Territories",
        "Nunavut": "Nunavut",
    })
)


# ============================================================
# NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "number_of_discharges",
    "total_length_of_stay_days",
    "average_length_of_stay_days"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# ============================================================
# REMOVE INVALID RECORDS
# ============================================================

df = df[
    df["jurisdiction"].notna()
].copy()

df = df[
    df["age_group"].notna()
].copy()

df = df[
    df["sex"].notna()
].copy()


# ============================================================
# DUPLICATE CHECK
# ============================================================

duplicate_count = df.duplicated().sum()

print(f"\nDuplicate records: {duplicate_count}")

if duplicate_count > 0:
    df = df.drop_duplicates()


# ============================================================
# COLUMN ORDER
# ============================================================

df = df[
    [
        "year",
        "year_start",
        "year_end",
        "jurisdiction",
        "age_group",
        "sex",
        "number_of_discharges",
        "total_length_of_stay_days",
        "average_length_of_stay_days"
    ]
]


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    [
        "year_start",
        "jurisdiction",
        "age_group",
        "sex"
    ]
).reset_index(drop=True)


# ============================================================
# REPORT
# ============================================================

print("\n--- CLEANED DATA ---")

print(f"Shape: {df.shape}")

print("\nYears:")
print(
    f"{df['year_start'].min()}–{df['year_end'].max()}"
)

print("\nJurisdictions:")
print(
    df["jurisdiction"]
    .value_counts()
    .sort_index()
)

print("\nAge groups:")
print(
    df["age_group"]
    .value_counts()
    .sort_index()
)

print("\nSex:")
print(
    df["sex"]
    .value_counts()
)

print("\nMissing values:")
print(
    df.isna()
    .sum()
    .loc[lambda x: x > 0]
)

print("\nOutput:")
print(OUTPUT_FILE)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 70)
print("CIHI HOSPITALIZATION DATA CLEANING COMPLETE")
print("=" * 70)