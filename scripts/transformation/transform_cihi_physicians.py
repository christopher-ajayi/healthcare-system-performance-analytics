# scripts/transformation/transform_cihi_physicians.py

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
    / "workforce"
    / "cihi_physicians_clean.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "workforce"
    / "cihi_physicians_transformed.csv"
)


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("CIHI PHYSICIAN WORKFORCE TRANSFORMATION")
print("=" * 70)

print(f"\nInput:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"File not found:\n{INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)


# ============================================================
# STANDARDIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.replace("\n", " ", regex=False)
    .str.replace("–", "-", regex=False)
    .str.replace("—", "-", regex=False)
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Year",
    "Jurisdiction",
    "Health region",
    "Specialty",
    "Specialty sort",
    "Physician-to-100,000 population ratio",
    "Number of physicians",
    "Number male",
    "Number female",
    "Number sex unknown",
    "Average age",
    "Median age",
    "Number in rural/remote areas",
    "Number in urban areas",
    "Number unknown urban or rural/remote",
    "Place of MD graduation: Canada",
    "Place of MD graduation: Foreign",
    "Place of MD graduation: Unknown",
    "Years since graduation: Fewer than 6",
    "Years since graduation: 6-10",
    "Years since graduation: 11-15",
    "Years since graduation: 16-20",
    "Years since graduation: 21-25",
    "Years since graduation: 26-30",
    "Years since graduation: 31-35",
    "Years since graduation: 36 and more",
    "Years since graduation: Unknown",
    "Median years since graduation",
    "Number of physicians who returned from abroad",
    "Number of physicians who moved abroad",
    "Net migration between Canadian jurisdictions",
    "Statistics Canada population",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Required columns are missing: {missing_columns}"
    )


# ============================================================
# RENAME CORE VARIABLES
# ============================================================

column_map = {
    "Year": "year",
    "Jurisdiction": "jurisdiction",
    "Health region": "health_region",
    "Specialty": "specialty",
    "Specialty sort": "specialty_sort",
    "Physician-to-100,000 population ratio": "physicians_per_100k",
    "Number of physicians": "physician_count",
    "Number male": "male_physicians",
    "Number female": "female_physicians",
    "Number sex unknown": "sex_unknown_physicians",
    "Average age": "average_age",
    "Median age": "median_age",
    "Number in rural/remote areas": "rural_remote_physicians",
    "Number in urban areas": "urban_physicians",
    "Number unknown urban or rural/remote": "location_unknown_physicians",
    "Place of MD graduation: Canada": "md_graduates_canada",
    "Place of MD graduation: Foreign": "md_graduates_foreign",
    "Place of MD graduation: Unknown": "md_graduates_unknown",
    "Years since graduation: Fewer than 6": "years_since_grad_under_6",
    "Years since graduation: 6-10": "years_since_grad_6_10",
    "Years since graduation: 11-15": "years_since_grad_11_15",
    "Years since graduation: 16-20": "years_since_grad_16_20",
    "Years since graduation: 21-25": "years_since_grad_21_25",
    "Years since graduation: 26-30": "years_since_grad_26_30",
    "Years since graduation: 31-35": "years_since_grad_31_35",
    "Years since graduation: 36 and more": "years_since_grad_36_plus",
    "Years since graduation: Unknown": "years_since_grad_unknown",
    "Median years since graduation": "median_years_since_graduation",
    "Number of physicians who returned from abroad": "physicians_returned_from_abroad",
    "Number of physicians who moved abroad": "physicians_moved_abroad",
    "Net migration between Canadian jurisdictions": "net_interprovincial_migration",
    "Statistics Canada population": "population",
}

df = df.rename(columns=column_map)


# ============================================================
# STANDARDIZE TEXT VARIABLES
# ============================================================

text_columns = [
    "jurisdiction",
    "health_region",
    "specialty",
]

for column in text_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# ============================================================
# STANDARDIZE JURISDICTION NAMES
# ============================================================

jurisdiction_map = {
    "Alta.": "Alberta",
    "B.C.": "British Columbia",
    "Man.": "Manitoba",
    "N.B.": "New Brunswick",
    "N.L.": "Newfoundland and Labrador",
    "N.S.": "Nova Scotia",
    "N.W.T.": "Northwest Territories",
    "Nun.": "Nunavut",
    "Ont.": "Ontario",
    "P.E.I.": "Prince Edward Island",
    "Que.": "Quebec",
    "Sask.": "Saskatchewan",
    "Y.T.": "Yukon",
    "Canada": "Canada",
}

df["jurisdiction"] = df["jurisdiction"].replace(
    jurisdiction_map
)


# ============================================================
# STANDARDIZE NUMERIC VARIABLES
# ============================================================

numeric_columns = [
    "year",
    "specialty_sort",
    "physicians_per_100k",
    "physician_count",
    "male_physicians",
    "female_physicians",
    "sex_unknown_physicians",
    "average_age",
    "median_age",
    "rural_remote_physicians",
    "urban_physicians",
    "location_unknown_physicians",
    "md_graduates_canada",
    "md_graduates_foreign",
    "md_graduates_unknown",
    "years_since_grad_under_6",
    "years_since_grad_6_10",
    "years_since_grad_11_15",
    "years_since_grad_16_20",
    "years_since_grad_21_25",
    "years_since_grad_26_30",
    "years_since_grad_31_35",
    "years_since_grad_36_plus",
    "years_since_grad_unknown",
    "median_years_since_graduation",
    "physicians_returned_from_abroad",
    "physicians_moved_abroad",
    "net_interprovincial_migration",
    "population",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# DERIVED WORKFORCE VARIABLES
# ============================================================

# Female physician share
df["female_physician_share_pct"] = (
    df["female_physicians"]
    / df["physician_count"]
    * 100
).where(
    df["physician_count"] > 0
)


# Rural/remote physician share
df["rural_remote_physician_share_pct"] = (
    df["rural_remote_physicians"]
    / df["physician_count"]
    * 100
).where(
    df["physician_count"] > 0
)


# International medical graduate share
df["foreign_md_graduate_share_pct"] = (
    df["md_graduates_foreign"]
    / df["physician_count"]
    * 100
).where(
    df["physician_count"] > 0
)


# Physicians aged 65+
age_65_plus_columns = [
    "Age group: 65-69",
    "Age group: 70-74",
    "Age group: 75-79",
    "Age group: 80 and older",
]

for column in age_65_plus_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

df["physicians_age_65_plus"] = (
    df[age_65_plus_columns]
    .sum(axis=1, min_count=1)
)

df["physicians_age_65_plus_share_pct"] = (
    df["physicians_age_65_plus"]
    / df["physician_count"]
    * 100
).where(
    df["physician_count"] > 0
)


# ============================================================
# YEAR-OVER-YEAR PHYSICIAN GROWTH
# ============================================================

df = df.sort_values(
    [
        "jurisdiction",
        "health_region",
        "specialty_sort",
        "year",
    ]
).reset_index(drop=True)

group_columns = [
    "jurisdiction",
    "health_region",
    "specialty",
]

df["physician_count_yoy_change"] = (
    df.groupby(group_columns)["physician_count"]
    .diff()
)

df["physician_count_yoy_growth_pct"] = (
    df.groupby(group_columns)["physician_count"]
    .pct_change(fill_method=None)
    * 100
)


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

final_columns = [
    "year",
    "jurisdiction",
    "health_region",
    "specialty",
    "specialty_sort",
    "physician_count",
    "physicians_per_100k",
    "physician_count_yoy_change",
    "physician_count_yoy_growth_pct",
    "male_physicians",
    "female_physicians",
    "sex_unknown_physicians",
    "female_physician_share_pct",
    "average_age",
    "median_age",
    "physicians_age_65_plus",
    "physicians_age_65_plus_share_pct",
    "rural_remote_physicians",
    "urban_physicians",
    "location_unknown_physicians",
    "rural_remote_physician_share_pct",
    "md_graduates_canada",
    "md_graduates_foreign",
    "md_graduates_unknown",
    "foreign_md_graduate_share_pct",
    "years_since_grad_under_6",
    "years_since_grad_6_10",
    "years_since_grad_11_15",
    "years_since_grad_16_20",
    "years_since_grad_21_25",
    "years_since_grad_26_30",
    "years_since_grad_31_35",
    "years_since_grad_36_plus",
    "years_since_grad_unknown",
    "median_years_since_graduation",
    "physicians_returned_from_abroad",
    "physicians_moved_abroad",
    "net_interprovincial_migration",
    "population",
]

df = df[final_columns]


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    [
        "jurisdiction",
        "health_region",
        "specialty_sort",
        "year",
    ]
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
print("CIHI PHYSICIAN WORKFORCE TRANSFORMATION COMPLETE")
print("=" * 70)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(f"\nRows: {len(df):,}")

print(f"\nColumns: {len(df.columns)}")

print("\nColumn names:")
print(df.columns.tolist())

print("\nYear coverage:")
print(
    f"{int(df['year'].min())}–{int(df['year'].max())}"
)

print("\nJurisdictions:")
print(df["jurisdiction"].nunique())

print(
    df["jurisdiction"]
    .value_counts()
    .sort_index()
)

print("\nSpecialties:")
print(df["specialty"].nunique())

print("\nMissing values:")
print(df.isna().sum())

print("\nFirst 10 rows:")
print(
    df.head(10).to_string(index=False)
)

print("\n" + "=" * 70)
