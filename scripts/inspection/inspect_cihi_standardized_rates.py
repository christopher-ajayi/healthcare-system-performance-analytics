from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "demand"
    / "hospitalizations_1995-2023.xlsx"
)

SHEET_NAME = "Table 2"


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("CIHI TABLE 2 — STANDARDIZED RATES INSPECTION")
print("=" * 70)

print(f"\nInput file:\n{INPUT_FILE}")
print(f"Sheet: {SHEET_NAME}")


# ============================================================
# FILE CHECK
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )

print(f"File size: {INPUT_FILE.stat().st_size / (1024 * 1024):.2f} MB")


# ============================================================
# LOAD SHEET
# ============================================================

df = pd.read_excel(
    INPUT_FILE,
    sheet_name=SHEET_NAME,
    header=None
)


# ============================================================
# BASIC STRUCTURE
# ============================================================

print("\n" + "-" * 70)
print("SHEET STRUCTURE")
print("-" * 70)

print(f"Shape: {df.shape}")

print("\nFirst 15 rows:")
print(df.head(15).to_string(index=False, header=False))


# ============================================================
# COLUMN INSPECTION
# ============================================================

print("\n" + "-" * 70)
print("COLUMN INSPECTION")
print("-" * 70)

for i, column in enumerate(df.columns, start=1):
    print(f"Column {i}: {column}")


# ============================================================
# IDENTIFY HEADER ROW
# ============================================================

print("\n" + "-" * 70)
print("HEADER INSPECTION")
print("-" * 70)

header_candidates = []

for index, row in df.iterrows():

    row_values = row.astype(str).str.strip().tolist()

    if "Discharge fiscal year" in row_values:
        header_candidates.append(index)

if not header_candidates:
    raise ValueError(
        "Could not locate the Table 2 header row."
    )

header_row = header_candidates[0]

print(f"Detected header row: {header_row}")

print("\nDetected headers:")

for value in df.iloc[header_row]:
    print(f"  - {value}")


# ============================================================
# CREATE DATAFRAME USING DETECTED HEADER
# ============================================================

table = pd.read_excel(
    INPUT_FILE,
    sheet_name=SHEET_NAME,
    header=header_row
)

print("\nDataframe shape after applying header:")
print(table.shape)


# ============================================================
# COLUMN NAMES
# ============================================================

print("\n" + "-" * 70)
print("COLUMN NAMES")
print("-" * 70)

for i, column in enumerate(table.columns, start=1):
    print(f"{i}. {repr(column)}")


# ============================================================
# MISSING VALUES
# ============================================================

print("\n" + "-" * 70)
print("MISSING VALUES")
print("-" * 70)

missing = table.isna().sum()

print(missing)


# ============================================================
# DUPLICATE ROWS
# ============================================================

print("\n" + "-" * 70)
print("DUPLICATE ROWS")
print("-" * 70)

duplicate_rows = table.duplicated().sum()

print(f"Duplicate rows: {duplicate_rows}")


# ============================================================
# IDENTIFY POTENTIAL DATA RECORDS
# ============================================================

year_column = "Discharge fiscal year"

if year_column not in table.columns:
    raise ValueError(
        f"Expected column '{year_column}' was not found."
    )

data_rows = table[
    table[year_column].notna()
].copy()


# ============================================================
# FISCAL YEAR COVERAGE
# ============================================================

print("\n" + "-" * 70)
print("FISCAL YEAR COVERAGE")
print("-" * 70)

years = data_rows[year_column].astype(str).str.strip()

print(f"Number of fiscal years: {years.nunique()}")

print("\nFiscal years:")

for year in years.drop_duplicates():
    print(f"  - {year}")


# ============================================================
# REGION / JURISDICTION INSPECTION
# ============================================================

region_column = "Province/territory"

if region_column in data_rows.columns:

    regions = (
        data_rows[region_column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    print("\n" + "-" * 70)
    print("JURISDICTION COVERAGE")
    print("-" * 70)

    print(f"Number of jurisdictions: {regions.nunique()}")

    print("\nJurisdictions:")

    for region in sorted(regions.unique()):
        print(f"  - {region}")


# ============================================================
# YEAR × REGION COVERAGE
# ============================================================

if region_column in data_rows.columns:

    coverage = (
        data_rows
        .groupby(year_column)[region_column]
        .nunique()
    )

    print("\n" + "-" * 70)
    print("JURISDICTION COUNT BY FISCAL YEAR")
    print("-" * 70)

    print(coverage.to_string())


# ============================================================
# UNIQUE VALUES IN NUMERIC FIELDS
# ============================================================

print("\n" + "-" * 70)
print("DATA TYPE INSPECTION")
print("-" * 70)

print(table.dtypes)


# ============================================================
# POTENTIAL NOTES / NON-DATA ROWS
# ============================================================

print("\n" + "-" * 70)
print("NON-DATA / NOTES INSPECTION")
print("-" * 70)

for index, row in table.iterrows():

    value = row[year_column]

    if pd.notna(value):
        value = str(value).strip()

        if not any(char.isdigit() for char in value):
            print(
                f"Row {index}: "
                f"{value}"
            )


# ============================================================
# DUPLICATE YEAR + REGION CHECK
# ============================================================

if region_column in data_rows.columns:

    duplicate_keys = data_rows.duplicated(
        subset=[
            year_column,
            region_column
        ],
        keep=False
    )

    duplicate_key_count = duplicate_keys.sum()

    print("\n" + "-" * 70)
    print("DUPLICATE YEAR + REGION CHECK")
    print("-" * 70)

    print(
        f"Duplicate year-region records: "
        f"{duplicate_key_count}"
    )

    if duplicate_key_count > 0:

        print("\nPotential duplicate records:")

        print(
            data_rows.loc[
                duplicate_keys
            ].to_string(index=False)
        )


# ============================================================
# SAMPLE DATA
# ============================================================

print("\n" + "-" * 70)
print("FIRST 10 DATA RECORDS")
print("-" * 70)

print(
    data_rows
    .head(10)
    .to_string(index=False)
)


print("\n" + "-" * 70)
print("LAST 10 DATA RECORDS")
print("-" * 70)

print(
    data_rows
    .tail(10)
    .to_string(index=False)
)


# ============================================================
# COMPLETION
# ============================================================

print("\n" + "=" * 70)
print("CIHI TABLE 2 INSPECTION COMPLETE")
print("=" * 70)