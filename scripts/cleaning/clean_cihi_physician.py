# scripts/cleaning/clean_cihi_physician.py

from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "workforce"
    / "cihi_physicians_2001_2024.xlsx"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "workforce"
    / "cihi_physicians_clean.csv"
)


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("CIHI PHYSICIAN WORKFORCE CLEANING")
print("=" * 70)

print(f"\nInput:\n{INPUT_FILE}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"File not found:\n{INPUT_FILE}"
    )

df = pd.read_excel(
    INPUT_FILE,
    sheet_name="Table 1",
    header=2
)


# ============================================================
# BASIC CLEANING
# ============================================================

# Remove completely empty rows and columns.
df = df.dropna(
    axis=0,
    how="all"
)

df = df.dropna(
    axis=1,
    how="all"
)


# ============================================================
# STANDARDIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.replace("\n", " ", regex=False)
    .str.replace("–", "-", regex=False)
    .str.replace("—", "-", regex=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)


# ============================================================
# REMOVE DUPLICATE COLUMNS
# ============================================================

if df.columns.duplicated().any():
    duplicated_columns = df.columns[
        df.columns.duplicated()
    ].tolist()

    raise ValueError(
        f"Duplicate column names detected: "
        f"{duplicated_columns}"
    )


# ============================================================
# STANDARDIZE MISSING VALUES
# ============================================================

missing_values = [
    "",
    " ",
    "NA",
    "N/A",
    "na",
    "n/a",
    "NULL",
    "null",
    "nan",
    "NaN",
    "x",
    "X",
]

df = df.replace(
    missing_values,
    pd.NA
)


# ============================================================
# STANDARDIZE TEXT VARIABLES
# ============================================================

text_columns = [
    "Jurisdiction",
    "Health region",
    "Specialty",
]

for column in text_columns:

    if column in df.columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )


# ============================================================
# STANDARDIZE YEAR
# ============================================================

if "Year" not in df.columns:
    raise ValueError(
        "Expected 'Year' column was not found."
    )

df["Year"] = pd.to_numeric(
    df["Year"],
    errors="coerce"
).astype("Int64")


# ============================================================
# STANDARDIZE NUMERIC VARIABLES
# ============================================================

numeric_columns = [
    "Specialty sort",
    "Physician-to-100,000 population ratio",
    "Number of physicians",
    "Number male",
    "Number female",
    "Number sex unknown",
    "Average age",
    "Median age",
    "Age group: Younger than 30",
    "Age group: 30-39",
    "Age group: 40-49",
    "Age group: 50-59",
    "Age group: 60-64",
    "Age group: 65-69",
    "Age group: 70-74",
    "Age group: 75-79",
    "Age group: 80 and older",
    "Age group: Unknown",
    "Number in rural/remote areas",
    "Number in urban areas",
    "Number unknown urban or rural/remote",
    "Place of MD graduation: Canada",
    "Place of MD graduation: Foreign",
    "Place of MD graduation: Unknown",
    "University of graduation: Memorial University",
    "University of graduation: Dalhousie University",
    "University of graduation: Laval Region University",
    "University of graduation: McGill University",
    "University of graduation: University of Montréal Region",
    "University of graduation: University of Sherbrooke",
    "University of graduation: University of Ottawa",
    "University of graduation: Queen's University",
    "University of graduation: University of Toronto",
    "University of graduation: University of Western Ontario",
    "University of graduation: McMaster University",
    "University of graduation: Northern Ontario School of Medicine",
    "University of graduation: University of Manitoba",
    "University of graduation: University of Saskatchewan",
    "University of graduation: University of Alberta",
    "University of graduation: University of Calgary",
    "University of graduation: University of British Columbia",
    "University of graduation: Unknown",
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

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ============================================================
# REMOVE INVALID DATA ROWS
# ============================================================

df = df[
    df["Year"].notna()
    & df["Jurisdiction"].notna()
    & df["Specialty"].notna()
].copy()


# ============================================================
# YEAR RANGE CHECK
# ============================================================

invalid_years = df[
    ~df["Year"].between(2001, 2024)
]

if not invalid_years.empty:
    raise ValueError(
        "Unexpected years detected:\n"
        f"{invalid_years['Year'].unique()}"
    )


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    [
        "Year",
        "Jurisdiction",
        "Health region",
        "Specialty sort",
    ],
    na_position="last"
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
print("CIHI PHYSICIAN WORKFORCE CLEANING COMPLETE")
print("=" * 70)

print(f"\nOutput:\n{OUTPUT_FILE}")

print(f"\nRows: {len(df):,}")
print(f"Columns: {len(df.columns):,}")

print("\nColumns:")
print(df.columns.tolist())

print("\nYear coverage:")
print(
    f"{int(df['Year'].min())}–"
    f"{int(df['Year'].max())}"
)

print("\nJurisdictions:")
print(
    df["Jurisdiction"]
    .nunique()
)

print(
    df["Jurisdiction"]
    .value_counts()
    .sort_index()
)

print("\nMissing values:")
print(df.isna().sum())

print("\nFirst 10 rows:")
print(
    df.head(10)
    .to_string(index=False)
)

print("\n" + "=" * 70)
