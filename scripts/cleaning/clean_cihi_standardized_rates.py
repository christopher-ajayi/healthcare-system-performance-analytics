"""
clean_cihi_standardized_rates.py

Purpose
-------
Clean CIHI Table 2 — Inpatient Hospitalizations:
Standardized Rates, 1995–1996 to 2023–2024.

Input
-----
data/raw/demand/hospitalizations_1995-2023.xlsx

Sheet
-----
Table 2

Output
------
data/processed/demand/cihi_standardized_rates_clean.csv

Important methodological issue
-------------------------------
CIHI changed the standard population used for direct
standardization beginning in 2014–2015.

1995–1996 through 2013–2014:
    2001 Canadian population estimates

2014–2015 onward:
    2011 Canadian population estimates

Therefore, hospitalization rates before and after
2014–2015 should NOT be directly compared as one
continuous standardized-rate series.

This script preserves the full structural dataset,
including suppressed/unavailable observations.

Expected source structure
-------------------------
29 fiscal years
14 jurisdictions per year
406 structural records

Expected available hospitalization rates:
402

Expected suppressed/unavailable hospitalization rates:
4

The four suppressed observations are associated with
Nunavut in:
    2002–2003
    2016–2017
    2019–2020
    2020–2021
"""

from pathlib import Path
import re
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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "demand"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "cihi_standardized_rates_clean.csv"
)

SHEET_NAME = "Table 2"


# ============================================================
# EXPECTED SOURCE COVERAGE
# ============================================================

EXPECTED_YEARS = 29

EXPECTED_REGIONS = 14

EXPECTED_STRUCTURAL_ROWS = 406

EXPECTED_AVAILABLE_RATE_ROWS = 402

EXPECTED_SUPPRESSED_RATE_ROWS = 4


# ============================================================
# EXPECTED JURISDICTIONS
# ============================================================

EXPECTED_REGIONS_SET = {
    "Alberta",
    "British Columbia",
    "Canada",
    "Manitoba",
    "New Brunswick",
    "Newfoundland and Labrador",
    "Northwest Territories",
    "Nova Scotia",
    "Nunavut",
    "Ontario",
    "Prince Edward Island",
    "Quebec",
    "Saskatchewan",
    "Yukon",
}


# ============================================================
# SOURCE COLUMN NAMES
# ============================================================

YEAR_COLUMN = "Discharge fiscal year"

REGION_COLUMN = "Province/territory"

RATE_COLUMN = (
    "Age–sex-standardized hospitalization rate "
    "(per 100,000 population)"
)

LOS_COLUMN = (
    "Age-standardized average "
    "length of stay (days)"
)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("CIHI TABLE 2 — STANDARDIZED RATES CLEANING")
print("=" * 70)

print(f"\nInput file:")
print(INPUT_FILE)

print(f"\nSheet:")
print(SHEET_NAME)


# ============================================================
# FILE CHECK
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )


# ============================================================
# LOAD RAW TABLE
# ============================================================

df = pd.read_excel(
    INPUT_FILE,
    sheet_name=SHEET_NAME,
    header=1
)

print(f"\nRaw shape: {df.shape}")


# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

def normalize_column_name(column):
    """
    Normalize line breaks and repeated whitespace while
    preserving the important CIHI wording.
    """

    column = str(column)

    column = column.replace("\n", " ")

    column = re.sub(
        r"\s+",
        " ",
        column
    )

    return column.strip()


df.columns = [
    normalize_column_name(column)
    for column in df.columns
]


print("\nDetected columns:")

for column in df.columns:
    print(f"  - {column}")


# ============================================================
# IDENTIFY TABLE 2 COLUMNS
# ============================================================

column_mapping = {}

for column in df.columns:

    if column == YEAR_COLUMN:

        column_mapping[column] = YEAR_COLUMN

    elif column == REGION_COLUMN:

        column_mapping[column] = REGION_COLUMN

    elif column.startswith(
        "Age–sex-standardized hospitalization rate"
    ):

        column_mapping[column] = RATE_COLUMN

    elif column.startswith(
        "Age-standardized average"
    ):

        column_mapping[column] = LOS_COLUMN


df = df.rename(
    columns=column_mapping
)


# ============================================================
# VERIFY REQUIRED COLUMNS
# ============================================================

required_columns = [
    YEAR_COLUMN,
    REGION_COLUMN,
    RATE_COLUMN,
    LOS_COLUMN,
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "\nRequired Table 2 columns are missing:\n"
        + "\n".join(
            f"  - {column}"
            for column in missing_columns
        )
    )


# ============================================================
# SELECT TABLE 2 VARIABLES
# ============================================================

df = df[
    required_columns
].copy()


# ============================================================
# REMOVE NON-DATA ROWS
# ============================================================

"""
CIHI places Notes, Sources and explanatory text below
the actual data table.

A valid fiscal-year record follows the pattern:

    YYYY–YYYY

We therefore identify actual data rows using the fiscal
year pattern rather than dropping rows based on whether
the rate is non-null.

This is important because some legitimate jurisdiction-year
records have suppressed/unavailable rates.
"""

fiscal_year_pattern = re.compile(
    r"^\d{4}–\d{4}$"
)


is_valid_fiscal_year = (
    df[YEAR_COLUMN]
    .astype(str)
    .str.strip()
    .apply(
        lambda value:
        bool(
            fiscal_year_pattern.match(value)
        )
    )
)


df = df[
    is_valid_fiscal_year
].copy()


print(
    "\nRows after removing CIHI notes/non-data rows:"
)

print(
    len(df)
)


# ============================================================
# RENAME VARIABLES
# ============================================================

df = df.rename(
    columns={
        YEAR_COLUMN: "fiscal_year",
        REGION_COLUMN: "region",
        RATE_COLUMN:
            "standardized_hospitalization_rate",
        LOS_COLUMN:
            "age_standardized_avg_los_days",
    }
)


# ============================================================
# CLEAN TEXT VARIABLES
# ============================================================

df["fiscal_year"] = (
    df["fiscal_year"]
    .astype(str)
    .str.strip()
)

df["region"] = (
    df["region"]
    .astype(str)
    .str.strip()
)


# ============================================================
# CREATE FISCAL YEAR START
# ============================================================

"""
Extract the first four digits from the fiscal year.

Example:

    2023–2024 -> 2023
    2014–2015 -> 2014
    1995–1996 -> 1995
"""

df["fiscal_year_start"] = (
    df["fiscal_year"]
    .str.extract(
        r"^(\d{4})",
        expand=False
    )
    .astype(int)
)


# ============================================================
# CREATE FISCAL YEAR END
# ============================================================

df["fiscal_year_end"] = (
    df["fiscal_year"]
    .str.extract(
        r"–(\d{4})$",
        expand=False
    )
    .astype(int)
)


# ============================================================
# VALIDATE FISCAL YEAR PAIRS
# ============================================================

invalid_year_pairs = df[
    df["fiscal_year_end"]
    != df["fiscal_year_start"] + 1
]

if not invalid_year_pairs.empty:

    print(
        "\nInvalid fiscal-year pairs detected:"
    )

    print(
        invalid_year_pairs[
            [
                "fiscal_year",
                "fiscal_year_start",
                "fiscal_year_end",
            ]
        ].to_string(index=False)
    )

    raise ValueError(
        "\nInvalid fiscal-year structure detected."
    )


# ============================================================
# CONVERT NUMERIC VARIABLES
# ============================================================

numeric_columns = [
    "standardized_hospitalization_rate",
    "age_standardized_avg_los_days",
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# RATE AVAILABILITY FLAG
# ============================================================

"""
Do NOT remove rows with missing rates.

CIHI suppresses certain observations. These records remain
part of the structural dataset but their rate is unavailable.

The boolean flag allows downstream analysis to distinguish:

    True  = rate available
    False = rate suppressed/unavailable
"""

df["rate_available"] = (
    df["standardized_hospitalization_rate"]
    .notna()
)


# ============================================================
# EXPECTED FISCAL YEARS
# ============================================================

expected_years = {
    f"{year}–{year + 1}"
    for year in range(1995, 2024)
}

actual_years = set(
    df["fiscal_year"].unique()
)


missing_years = (
    expected_years
    - actual_years
)

unexpected_years = (
    actual_years
    - expected_years
)


if missing_years:

    raise ValueError(
        "\nMissing fiscal years:\n"
        + "\n".join(
            f"  - {year}"
            for year in sorted(missing_years)
        )
    )


if unexpected_years:

    raise ValueError(
        "\nUnexpected fiscal years:\n"
        + "\n".join(
            f"  - {year}"
            for year in sorted(unexpected_years)
        )
    )


# ============================================================
# STANDARDIZATION PERIOD
# ============================================================

"""
CIHI methodology:

1995–1996 through 2013–2014:
    2001 Canadian population standard

2014–2015 onward:
    2011 Canadian population standard
"""

df["standardization_period"] = (
    df["fiscal_year_start"]
    .apply(
        lambda year:
        "2001_standard_population"
        if year <= 2013
        else "2011_standard_population"
    )
)


# ============================================================
# STANDARDIZATION BREAK FLAG
# ============================================================

"""
2014–2015 is the first year using the 2011 Canadian
population estimates.

This flag identifies that methodological break.
"""

df["standardization_break"] = (
    df["fiscal_year_start"] == 2014
)


# ============================================================
# DUPLICATE CHECK
# ============================================================

duplicate_count = df.duplicated(
    subset=[
        "fiscal_year",
        "region",
    ]
).sum()


print(
    "\nDuplicate fiscal-year/region records:"
)

print(
    duplicate_count
)


if duplicate_count > 0:

    duplicates = df[
        df.duplicated(
            subset=[
                "fiscal_year",
                "region",
            ],
            keep=False
        )
    ]

    print(
        "\nDuplicate records:"
    )

    print(
        duplicates.to_string(
            index=False
        )
    )

    raise ValueError(
        "\nDuplicate fiscal-year/region "
        "records detected."
    )


# ============================================================
# JURISDICTION VALIDATION
# ============================================================

actual_regions = set(
    df["region"].unique()
)


unexpected_regions = (
    actual_regions
    - EXPECTED_REGIONS_SET
)


missing_regions = (
    EXPECTED_REGIONS_SET
    - actual_regions
)


if unexpected_regions:

    raise ValueError(
        "\nUnexpected jurisdictions detected:\n"
        + "\n".join(
            f"  - {region}"
            for region in sorted(
                unexpected_regions
            )
        )
    )


if missing_regions:

    raise ValueError(
        "\nExpected jurisdictions missing:\n"
        + "\n".join(
            f"  - {region}"
            for region in sorted(
                missing_regions
            )
        )
    )


# ============================================================
# STRUCTURAL COVERAGE VALIDATION
# ============================================================

year_count = (
    df["fiscal_year"]
    .nunique()
)

region_count = (
    df["region"]
    .nunique()
)

actual_rows = len(df)


print("\nCoverage:")
print(
    f"  Fiscal years: {year_count}"
)
print(
    f"  Jurisdictions: {region_count}"
)
print(
    f"  Structural rows: {actual_rows}"
)


# ============================================================
# STRUCTURAL COVERAGE COUNTS
# ============================================================

if year_count != EXPECTED_YEARS:

    raise ValueError(
        f"\nUnexpected fiscal-year count: "
        f"{year_count}. "
        f"Expected {EXPECTED_YEARS}."
    )


if region_count != EXPECTED_REGIONS:

    raise ValueError(
        f"\nUnexpected jurisdiction count: "
        f"{region_count}. "
        f"Expected {EXPECTED_REGIONS}."
    )


if actual_rows != EXPECTED_STRUCTURAL_ROWS:

    raise ValueError(
        f"\nUnexpected structural row count: "
        f"{actual_rows}. "
        f"Expected {EXPECTED_STRUCTURAL_ROWS}."
    )


# ============================================================
# YEAR × JURISDICTION COVERAGE
# ============================================================

coverage = (
    df.groupby(
        "fiscal_year"
    )["region"]
    .nunique()
)


incomplete_years = coverage[
    coverage != EXPECTED_REGIONS
]


if not incomplete_years.empty:

    print(
        "\nFiscal years with incomplete "
        "jurisdiction coverage:"
    )

    print(
        incomplete_years.to_string()
    )

    raise ValueError(
        "\nOne or more fiscal years do not "
        "contain all 14 jurisdictions."
    )


print(
    "\nStructural coverage validation passed:"
)

print(
    "  29 fiscal years"
)

print(
    "  14 jurisdictions per year"
)

print(
    "  406 structural records"
)


# ============================================================
# AVAILABLE VS SUPPRESSED RATES
# ============================================================

available_rate_rows = (
    df[
        "standardized_hospitalization_rate"
    ].notna().sum()
)


suppressed_rate_rows = (
    df[
        "standardized_hospitalization_rate"
    ].isna().sum()
)


print(
    "\nHospitalization-rate availability:"
)

print(
    f"  Available: {available_rate_rows}"
)

print(
    f"  Suppressed/unavailable: "
    f"{suppressed_rate_rows}"
)


if available_rate_rows != EXPECTED_AVAILABLE_RATE_ROWS:

    raise ValueError(
        f"\nUnexpected number of available "
        f"hospitalization rates: "
        f"{available_rate_rows}. "
        f"Expected "
        f"{EXPECTED_AVAILABLE_RATE_ROWS}."
    )


if suppressed_rate_rows != EXPECTED_SUPPRESSED_RATE_ROWS:

    raise ValueError(
        f"\nUnexpected number of suppressed/"
        f"unavailable rates: "
        f"{suppressed_rate_rows}. "
        f"Expected "
        f"{EXPECTED_SUPPRESSED_RATE_ROWS}."
    )


# ============================================================
# IDENTIFY SUPPRESSED OBSERVATIONS
# ============================================================

suppressed_records = df[
    ~df["rate_available"]
].copy()


if not suppressed_records.empty:

    print(
        "\nSuppressed/unavailable observations:"
    )

    print(
        suppressed_records[
            [
                "fiscal_year",
                "region",
                "standardized_hospitalization_rate",
                "rate_available",
            ]
        ].to_string(index=False)
    )


# ============================================================
# MISSING VALUE CHECK
# ============================================================

print(
    "\nMissing values:"
)

missing_summary = (
    df.isna().sum()
)


print(
    missing_summary.to_string()
)


# ============================================================
# NUMERIC VALIDATION
# ============================================================

print(
    "\nNumeric ranges:"
)


for column in numeric_columns:

    available_values = (
        df[column]
        .dropna()
    )

    print(
        f"\n{column}"
    )

    print(
        f"  Available values: "
        f"{len(available_values)}"
    )

    if available_values.empty:

        print(
            "  No available numeric values."
        )

        continue

    print(
        f"  Minimum: "
        f"{available_values.min()}"
    )

    print(
        f"  Maximum: "
        f"{available_values.max()}"
    )

    if (
        available_values < 0
    ).any():

        raise ValueError(
            f"\nNegative values detected "
            f"in {column}."
        )


# ============================================================
# STANDARDIZATION PERIOD VALIDATION
# ============================================================

period_counts = (
    df[
        "standardization_period"
    ].value_counts()
)


print(
    "\nStandardization periods:"
)

print(
    period_counts.to_string()
)


expected_2001_records = (
    19 * EXPECTED_REGIONS
)

expected_2011_records = (
    10 * EXPECTED_REGIONS
)


actual_2001_records = (
    df[
        "standardization_period"
    ]
    .eq(
        "2001_standard_population"
    )
    .sum()
)


actual_2011_records = (
    df[
        "standardization_period"
    ]
    .eq(
        "2011_standard_population"
    )
    .sum()
)


if actual_2001_records != expected_2001_records:

    raise ValueError(
        "\nUnexpected number of records "
        "using the 2001 standard population: "
        f"{actual_2001_records}. "
        f"Expected {expected_2001_records}."
    )


if actual_2011_records != expected_2011_records:

    raise ValueError(
        "\nUnexpected number of records "
        "using the 2011 standard population: "
        f"{actual_2011_records}. "
        f"Expected {expected_2011_records}."
    )


# ============================================================
# STANDARDIZATION BREAK VALIDATION
# ============================================================

break_rows = (
    df[
        "standardization_break"
    ].sum()
)


expected_break_rows = (
    EXPECTED_REGIONS
)


print(
    "\nRows in standardization-break "
    "year (2014–2015):"
)

print(
    break_rows
)


if break_rows != expected_break_rows:

    raise ValueError(
        "\nUnexpected number of records "
        "flagged as the 2014–2015 "
        "standardization break: "
        f"{break_rows}. "
        f"Expected {expected_break_rows}."
    )


# ============================================================
# EXPLICIT METHODOLOGICAL VALIDATION
# ============================================================

"""
Ensure that:

    <= 2013 -> 2001 standard population

    >= 2014 -> 2011 standard population
"""

invalid_standardization_periods = df[
    (
        (
            df["fiscal_year_start"] <= 2013
        )
        &
        (
            df["standardization_period"]
            != "2001_standard_population"
        )
    )
    |
    (
        (
            df["fiscal_year_start"] >= 2014
        )
        &
        (
            df["standardization_period"]
            != "2011_standard_population"
        )
    )
]


if not invalid_standardization_periods.empty:

    print(
        "\nInvalid standardization-period "
        "assignments:"
    )

    print(
        invalid_standardization_periods[
            [
                "fiscal_year",
                "fiscal_year_start",
                "standardization_period",
            ]
        ].to_string(index=False)
    )

    raise ValueError(
        "\nInvalid standardization-period "
        "assignment detected."
    )


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    by=[
        "fiscal_year_start",
        "region",
    ]
).reset_index(
    drop=True
)


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

df = df[
    [
        "fiscal_year",
        "fiscal_year_start",
        "fiscal_year_end",
        "region",
        "standardized_hospitalization_rate",
        "age_standardized_avg_los_days",
        "rate_available",
        "standardization_period",
        "standardization_break",
    ]
]


# ============================================================
# FINAL ROW COUNT VALIDATION
# ============================================================

if len(df) != EXPECTED_STRUCTURAL_ROWS:

    raise ValueError(
        "\nFinal dataset row count changed "
        "unexpectedly: "
        f"{len(df)}. "
        f"Expected "
        f"{EXPECTED_STRUCTURAL_ROWS}."
    )


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SAVE CLEAN DATA
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "CIHI TABLE 2 CLEANING COMPLETE"
)

print(
    "=" * 70
)


print(
    f"\nFinal shape: {df.shape}"
)


print(
    "\nFinal columns:"
)

for column in df.columns:

    print(
        f"  - {column}"
    )


print(
    f"\nOutput file:"
)

print(
    OUTPUT_FILE
)


print(
    "\nFinal coverage:"
)

print(
    f"  Fiscal years: "
    f"{df['fiscal_year'].nunique()}"
)

print(
    f"  Jurisdictions: "
    f"{df['region'].nunique()}"
)

print(
    f"  Structural records: "
    f"{len(df)}"
)

print(
    f"  Available rates: "
    f"{df['rate_available'].sum()}"
)

print(
    f"  Suppressed rates: "
    f"{(~df['rate_available']).sum()}"
)


print(
    "\nStandardization periods:"
)

print(
    df[
        "standardization_period"
    ]
    .value_counts()
    .to_string()
)


print(
    "\nRows in standardization-break "
    "year (2014–2015):"
)

print(
    df[
        "standardization_break"
    ].sum()
)


print(
    "\nSuppressed/unavailable records:"
)

if suppressed_records.empty:

    print(
        "  None"
    )

else:

    print(
        suppressed_records[
            [
                "fiscal_year",
                "region",
            ]
        ].to_string(index=False)
    )


print(
    "\nFirst 10 processed records:"
)

print(
    df.head(10).to_string(
        index=False
    )
)


print(
    "\n" + "=" * 70
)

print(
    "CLEANING COMPLETE"
)

print(
    "=" * 70
)