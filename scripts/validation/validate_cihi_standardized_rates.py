"""
validate_cihi_standardized_rates.py

Purpose:
    Validate the transformed CIHI Table 2 — Inpatient Hospitalizations:
    Standardized Rates, 1995–1996 to 2023–2024.

Input:
    data/processed/demand/cihi_standardized_rates_transformed.csv

Validation focus:
    - Structural completeness
    - Fiscal-year coverage
    - Jurisdiction coverage
    - Duplicate records
    - Suppressed observations
    - Numeric integrity
    - Rate conversion
    - Standardization-period classification
    - 2014–2015 standardization break
    - Required columns
    - Output integrity

Important methodological note:
    CIHI changed the standard population used for direct
    standardization beginning in 2014–2015.

    1995–1996 through 2013–2014:
        2001 Canadian population estimates

    2014–2015 onward:
        2011 Canadian population estimates

    Rates across this break should not be directly compared.
"""

from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "demand"
    / "cihi_standardized_rates_transformed.csv"
)


# ============================================================
# EXPECTED STRUCTURE
# ============================================================

EXPECTED_COLUMNS = [
    "fiscal_year",
    "fiscal_year_start",
    "fiscal_year_end",
    "region",
    "standardized_hospitalization_rate",
    "standardized_hospitalization_rate_per_1000",
    "age_standardized_avg_los_days",
    "rate_available",
    "standardization_period",
    "standardization_break",
]


EXPECTED_REGIONS = {
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


EXPECTED_YEARS = [
    f"{year}–{year + 1}"
    for year in range(1995, 2024)
]


EXPECTED_STANDARDIZATION_PERIODS = {
    "2001_standard_population",
    "2011_standard_population",
}


# Known CIHI suppressed/unavailable observations
EXPECTED_SUPPRESSED = {
    ("2002–2003", "Nunavut"),
    ("2016–2017", "Nunavut"),
    ("2019–2020", "Nunavut"),
    ("2020–2021", "Nunavut"),
}


EXPECTED_ROWS = 406
EXPECTED_AVAILABLE_RATES = 402
EXPECTED_SUPPRESSED_RATES = 4


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("CIHI TABLE 2 — STANDARDIZED RATES VALIDATION")
print("=" * 70)

print(f"\nInput file:\n{INPUT_FILE}")


# ============================================================
# FILE CHECK
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nTransformed Table 2 file not found:\n{INPUT_FILE}"
    )


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print(f"\nInput shape: {df.shape}")


# ============================================================
# 1. COLUMN VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("1. COLUMN VALIDATION")
print("-" * 70)

actual_columns = list(df.columns)

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in actual_columns
]

unexpected_columns = [
    column
    for column in actual_columns
    if column not in EXPECTED_COLUMNS
]

if missing_columns:
    raise ValueError(
        "Missing required columns:\n"
        + "\n".join(
            f"  - {column}"
            for column in missing_columns
        )
    )

if unexpected_columns:
    raise ValueError(
        "Unexpected columns detected:\n"
        + "\n".join(
            f"  - {column}"
            for column in unexpected_columns
        )
    )

print("Column validation passed.")

print("\nColumns:")
for column in df.columns:
    print(f"  - {column}")


# ============================================================
# 2. RECORD COUNT
# ============================================================

print("\n" + "-" * 70)
print("2. RECORD COUNT")
print("-" * 70)

actual_rows = len(df)

print(f"Actual records:   {actual_rows}")
print(f"Expected records: {EXPECTED_ROWS}")

if actual_rows != EXPECTED_ROWS:
    raise ValueError(
        f"Unexpected record count: {actual_rows}. "
        f"Expected {EXPECTED_ROWS}."
    )

print("Record-count validation passed.")


# ============================================================
# 3. FISCAL YEAR VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("3. FISCAL YEAR VALIDATION")
print("-" * 70)

actual_years = set(
    df["fiscal_year"].dropna().unique()
)

expected_years = set(EXPECTED_YEARS)

missing_years = expected_years - actual_years
unexpected_years = actual_years - expected_years

if missing_years:
    raise ValueError(
        "Missing fiscal years:\n"
        + "\n".join(
            f"  - {year}"
            for year in sorted(missing_years)
        )
    )

if unexpected_years:
    raise ValueError(
        "Unexpected fiscal years:\n"
        + "\n".join(
            f"  - {year}"
            for year in sorted(unexpected_years)
        )
    )

if len(actual_years) != 29:
    raise ValueError(
        f"Unexpected fiscal-year count: "
        f"{len(actual_years)}. Expected 29."
    )

print("Fiscal-year validation passed.")
print("  Fiscal years: 29")
print("  Coverage: 1995–1996 → 2023–2024")


# ============================================================
# 4. JURISDICTION VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("4. JURISDICTION VALIDATION")
print("-" * 70)

actual_regions = set(
    df["region"].dropna().unique()
)

missing_regions = (
    EXPECTED_REGIONS - actual_regions
)

unexpected_regions = (
    actual_regions - EXPECTED_REGIONS
)

if missing_regions:
    raise ValueError(
        "Missing expected jurisdictions:\n"
        + "\n".join(
            f"  - {region}"
            for region in sorted(missing_regions)
        )
    )

if unexpected_regions:
    raise ValueError(
        "Unexpected jurisdictions:\n"
        + "\n".join(
            f"  - {region}"
            for region in sorted(unexpected_regions)
        )
    )

if len(actual_regions) != 14:
    raise ValueError(
        f"Unexpected jurisdiction count: "
        f"{len(actual_regions)}. Expected 14."
    )

print("Jurisdiction validation passed.")
print("  Jurisdictions: 14")


# ============================================================
# 5. YEAR × REGION COVERAGE
# ============================================================

print("\n" + "-" * 70)
print("5. YEAR × REGION COVERAGE")
print("-" * 70)

coverage = (
    df.groupby("fiscal_year")["region"]
    .nunique()
)

incomplete_years = coverage[
    coverage != 14
]

if not incomplete_years.empty:

    print(
        "Incomplete fiscal-year coverage:"
    )

    print(
        incomplete_years.to_string()
    )

    raise ValueError(
        "One or more fiscal years do not contain "
        "all 14 expected jurisdictions."
    )

print(
    "Year × jurisdiction coverage passed."
)

print(
    "  29 years × 14 jurisdictions = 406 records"
)


# ============================================================
# 6. DUPLICATE VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("6. DUPLICATE VALIDATION")
print("-" * 70)

duplicate_count = df.duplicated(
    subset=[
        "fiscal_year",
        "region",
    ]
).sum()

print(
    f"Duplicate fiscal-year × region records: "
    f"{duplicate_count}"
)

if duplicate_count > 0:

    duplicates = df[
        df.duplicated(
            subset=[
                "fiscal_year",
                "region",
            ],
            keep=False,
        )
    ]

    print("\nDuplicate records:")
    print(
        duplicates.to_string(index=False)
    )

    raise ValueError(
        "Duplicate fiscal-year × region records detected."
    )

print("Duplicate validation passed.")


# ============================================================
# 7. FISCAL YEAR START / END VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("7. FISCAL YEAR START / END VALIDATION")
print("-" * 70)

if not pd.api.types.is_numeric_dtype(
    df["fiscal_year_start"]
):
    raise ValueError(
        "fiscal_year_start must be numeric."
    )

if not pd.api.types.is_numeric_dtype(
    df["fiscal_year_end"]
):
    raise ValueError(
        "fiscal_year_end must be numeric."
    )

year_logic_valid = (
    df["fiscal_year_end"]
    == df["fiscal_year_start"] + 1
)

if not year_logic_valid.all():
    print(
        df.loc[
            ~year_logic_valid,
            [
                "fiscal_year",
                "fiscal_year_start",
                "fiscal_year_end",
            ],
        ].to_string(index=False)
    )

    raise ValueError(
        "Fiscal-year start/end relationship is invalid."
    )

print(
    "Fiscal-year start/end validation passed."
)


# ============================================================
# 8. RATE AVAILABILITY VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("8. RATE AVAILABILITY VALIDATION")
print("-" * 70)

available_count = int(
    df["rate_available"].sum()
)

suppressed_count = int(
    (~df["rate_available"]).sum()
)

print(f"Available rates:   {available_count}")
print(f"Suppressed rates:  {suppressed_count}")

if available_count != EXPECTED_AVAILABLE_RATES:
    raise ValueError(
        f"Unexpected available-rate count: "
        f"{available_count}. "
        f"Expected {EXPECTED_AVAILABLE_RATES}."
    )

if suppressed_count != EXPECTED_SUPPRESSED_RATES:
    raise ValueError(
        f"Unexpected suppressed-rate count: "
        f"{suppressed_count}. "
        f"Expected {EXPECTED_SUPPRESSED_RATES}."
    )

print("Rate-availability validation passed.")


# ============================================================
# 9. SUPPRESSED OBSERVATION VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("9. SUPPRESSED OBSERVATION VALIDATION")
print("-" * 70)

suppressed_df = df[
    ~df["rate_available"]
].copy()

actual_suppressed = set(
    zip(
        suppressed_df["fiscal_year"],
        suppressed_df["region"],
    )
)

if actual_suppressed != EXPECTED_SUPPRESSED:

    print("\nExpected suppressed observations:")

    for record in sorted(EXPECTED_SUPPRESSED):
        print(f"  - {record}")

    print("\nActual suppressed observations:")

    for record in sorted(actual_suppressed):
        print(f"  - {record}")

    raise ValueError(
        "Suppressed/unavailable observations do not "
        "match the expected CIHI observations."
    )


# Suppressed rates must be NaN
if (
    suppressed_df[
        "standardized_hospitalization_rate"
    ].notna().any()
):
    raise ValueError(
        "Suppressed observations contain "
        "non-null hospitalization rates."
    )


if (
    suppressed_df[
        "standardized_hospitalization_rate_per_1000"
    ].notna().any()
):
    raise ValueError(
        "Suppressed observations contain "
        "non-null per-1,000 rates."
    )


print(
    "Suppressed observations validated:"
)

print(
    suppressed_df[
        [
            "fiscal_year",
            "region",
        ]
    ].to_string(index=False)
)

print(
    "\nSuppression validation passed."
)


# ============================================================
# 10. AVAILABLE OBSERVATION VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("10. AVAILABLE OBSERVATION VALIDATION")
print("-" * 70)

available_df = df[
    df["rate_available"]
].copy()

if available_df[
    "standardized_hospitalization_rate"
].isna().any():

    raise ValueError(
        "Available observations contain "
        "missing hospitalization rates."
    )


if available_df[
    "standardized_hospitalization_rate_per_1000"
].isna().any():

    raise ValueError(
        "Available observations contain "
        "missing per-1,000 rates."
    )


print(
    "Available-observation validation passed."
)


# ============================================================
# 11. RATE CONVERSION VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("11. RATE CONVERSION VALIDATION")
print("-" * 70)

expected_per_1000 = (
    available_df[
        "standardized_hospitalization_rate"
    ] / 100
)

actual_per_1000 = available_df[
    "standardized_hospitalization_rate_per_1000"
]

conversion_valid = np.isclose(
    actual_per_1000,
    expected_per_1000,
    rtol=1e-10,
    atol=1e-10,
)

if not conversion_valid.all():

    invalid = available_df.loc[
        ~conversion_valid,
        [
            "fiscal_year",
            "region",
            "standardized_hospitalization_rate",
            "standardized_hospitalization_rate_per_1000",
        ],
    ]

    print(
        invalid.to_string(index=False)
    )

    raise ValueError(
        "Rate-per-1,000 conversion validation failed."
    )

print(
    "Rate conversion validation passed."
)

print(
    "  Per-1,000 rate = per-100,000 rate ÷ 100"
)


# ============================================================
# 12. LENGTH OF STAY VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("12. LENGTH OF STAY VALIDATION")
print("-" * 70)

los = df["age_standardized_avg_los_days"]

# LOS may be missing only where CIHI has suppressed the
# corresponding hospitalization rate.
los_missing = df[
    los.isna()
]

actual_los_missing = set(
    zip(
        los_missing["fiscal_year"],
        los_missing["region"],
    )
)

if actual_los_missing != EXPECTED_SUPPRESSED:

    print("\nUnexpected LOS-missing observations:")

    for record in sorted(actual_los_missing):
        print(f"  - {record}")

    print("\nExpected LOS-missing observations:")

    for record in sorted(EXPECTED_SUPPRESSED):
        print(f"  - {record}")

    raise ValueError(
        "Missing age-standardized average length-of-stay "
        "values occur outside the known CIHI-suppressed "
        "observations."
    )


# All non-suppressed observations must have LOS
available_los = df[
    df["rate_available"]
]["age_standardized_avg_los_days"]

if available_los.isna().any():

    raise ValueError(
        "Available observations contain missing "
        "age-standardized average length-of-stay values."
    )


# LOS must not be negative
if (available_los < 0).any():

    raise ValueError(
        "Negative length-of-stay values detected."
    )


print(
    "Length-of-stay validation passed."
)

print(
    f"  Available LOS values: {available_los.notna().sum()}"
)

print(
    f"  Suppressed LOS values: {los.isna().sum()}"
)

print(
    f"  Minimum: {available_los.min()}"
)

print(
    f"  Maximum: {available_los.max()}"
)

# ============================================================
# 13. HOSPITALIZATION RATE VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("13. HOSPITALIZATION RATE VALIDATION")
print("-" * 70)

rates = available_df[
    "standardized_hospitalization_rate"
]

if (rates < 0).any():
    raise ValueError(
        "Negative hospitalization rates detected."
    )

per_1000 = available_df[
    "standardized_hospitalization_rate_per_1000"
]

if (per_1000 < 0).any():
    raise ValueError(
        "Negative per-1,000 hospitalization rates detected."
    )

print(
    "Hospitalization-rate validation passed."
)

print(
    f"  Minimum per 100,000: {rates.min()}"
)

print(
    f"  Maximum per 100,000: {rates.max()}"
)

print(
    f"  Minimum per 1,000:   {per_1000.min()}"
)

print(
    f"  Maximum per 1,000:   {per_1000.max()}"
)


# ============================================================
# 14. STANDARDIZATION PERIOD VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("14. STANDARDIZATION PERIOD VALIDATION")
print("-" * 70)

actual_periods = set(
    df["standardization_period"].unique()
)

unexpected_periods = (
    actual_periods
    - EXPECTED_STANDARDIZATION_PERIODS
)

if unexpected_periods:

    raise ValueError(
        "Unexpected standardization periods:\n"
        + "\n".join(
            f"  - {period}"
            for period in sorted(unexpected_periods)
        )
    )


# 1995–2013 must use 2001 population
period_2001_valid = (
    df.loc[
        df["fiscal_year_start"] <= 2013,
        "standardization_period",
    ]
    == "2001_standard_population"
)

if not period_2001_valid.all():

    raise ValueError(
        "One or more records from 1995–1996 "
        "through 2013–2014 have an incorrect "
        "standardization period."
    )


# 2014 onward must use 2011 population
period_2011_valid = (
    df.loc[
        df["fiscal_year_start"] >= 2014,
        "standardization_period",
    ]
    == "2011_standard_population"
)

if not period_2011_valid.all():

    raise ValueError(
        "One or more records from 2014–2015 "
        "onward have an incorrect "
        "standardization period."
    )


print(
    "Standardization-period validation passed."
)

print(
    df["standardization_period"]
    .value_counts()
    .to_string()
)


# ============================================================
# 15. STANDARDIZATION BREAK VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("15. STANDARDIZATION BREAK VALIDATION")
print("-" * 70)

break_rows = df[
    df["standardization_break"]
]

break_count = len(break_rows)

print(
    f"Rows flagged as standardization break: "
    f"{break_count}"
)

if break_count != 14:
    raise ValueError(
        f"Unexpected number of standardization-break "
        f"rows: {break_count}. Expected 14."
    )


# Only 2014–2015 may be flagged
invalid_break_years = (
    break_rows["fiscal_year"].unique()
)

if set(invalid_break_years) != {"2014–2015"}:

    raise ValueError(
        "Standardization-break flag appears on "
        "unexpected fiscal years."
    )


# No other year may be flagged
other_breaks = df[
    (~df["standardization_break"])
    & (df["fiscal_year"] == "2014–2015")
]

if not other_breaks.empty:
    raise ValueError(
        "Not all 2014–2015 observations are "
        "flagged as standardization-break records."
    )


print(
    "Standardization-break validation passed."
)

print(
    "  2014–2015: 14 records flagged"
)


# ============================================================
# 16. DATA TYPE VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("16. DATA TYPE VALIDATION")
print("-" * 70)

numeric_columns = [
    "fiscal_year_start",
    "fiscal_year_end",
    "standardized_hospitalization_rate",
    "standardized_hospitalization_rate_per_1000",
    "age_standardized_avg_los_days",
]

for column in numeric_columns:

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):

        raise ValueError(
            f"Column '{column}' is not numeric."
        )


boolean_columns = [
    "rate_available",
    "standardization_break",
]

for column in boolean_columns:

    if not pd.api.types.is_bool_dtype(
        df[column]
    ):

        raise ValueError(
            f"Column '{column}' is not boolean."
        )


print(
    "Data-type validation passed."
)


# ============================================================
# 17. MISSING VALUE VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("17. MISSING VALUE VALIDATION")
print("-" * 70)

missing_summary = df.isna().sum()

print(
    missing_summary.to_string()
)

# These columns may contain missing values only for the
# four CIHI-suppressed Nunavut observations.
allowed_missing_columns = {
    "standardized_hospitalization_rate",
    "standardized_hospitalization_rate_per_1000",
    "age_standardized_avg_los_days",
}

for column in df.columns:

    missing_count = df[column].isna().sum()

    if column in allowed_missing_columns:

        if missing_count != 4:

            raise ValueError(
                f"Unexpected missing-value count in "
                f"{column}: {missing_count}. "
                f"Expected 4."
            )

    else:

        if missing_count != 0:

            raise ValueError(
                f"Unexpected missing values detected "
                f"in column '{column}': {missing_count}"
            )


# Verify that all allowed missing values occur on the
# exact same four suppressed observations.
for column in allowed_missing_columns:

    missing_records = set(
        zip(
            df.loc[df[column].isna(), "fiscal_year"],
            df.loc[df[column].isna(), "region"],
        )
    )

    if missing_records != EXPECTED_SUPPRESSED:

        raise ValueError(
            f"Missing values in '{column}' do not match "
            f"the expected CIHI-suppressed observations."
        )


print(
    "Missing-value validation passed."
)

print(
    "\nMissing values are restricted to the four "
    "CIHI-suppressed Nunavut observations."
)

# ============================================================
# 18. STRUCTURAL UNIQUENESS VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("18. STRUCTURAL UNIQUENESS VALIDATION")
print("-" * 70)

expected_combinations = (
    len(EXPECTED_YEARS)
    * len(EXPECTED_REGIONS)
)

actual_combinations = (
    df[
        [
            "fiscal_year",
            "region",
        ]
    ]
    .drop_duplicates()
    .shape[0]
)

print(
    f"Expected combinations: {expected_combinations}"
)

print(
    f"Actual combinations:   {actual_combinations}"
)

if actual_combinations != expected_combinations:
    raise ValueError(
        "Structural year × jurisdiction "
        "combination count is incorrect."
    )

print(
    "Structural uniqueness validation passed."
)


# ============================================================
# 19. OUTPUT ORDER VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("19. OUTPUT ORDER VALIDATION")
print("-" * 70)

if actual_columns != EXPECTED_COLUMNS:

    raise ValueError(
        "Output column order does not match "
        "the expected analytical structure."
    )

print(
    "Output column order validation passed."
)


# ============================================================
# 20. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CIHI TABLE 2 VALIDATION COMPLETE")
print("=" * 70)

print("\nFINAL VALIDATION SUMMARY")

print(
    f"  Records:                  {len(df)}"
)

print(
    f"  Fiscal years:             {df['fiscal_year'].nunique()}"
)

print(
    f"  Jurisdictions:            {df['region'].nunique()}"
)

print(
    f"  Available rates:          "
    f"{df['rate_available'].sum()}"
)

print(
    f"  Suppressed rates:         "
    f"{(~df['rate_available']).sum()}"
)

print(
    f"  Standardization breaks:   "
    f"{df['standardization_break'].sum()}"
)

print(
    "\nStandardization periods:"
)

print(
    df["standardization_period"]
    .value_counts()
    .to_string()
)

print(
    "\nSuppressed observations:"
)

print(
    suppressed_df[
        [
            "fiscal_year",
            "region",
        ]
    ].to_string(index=False)
)

print(
    "\nAll Table 2 validation checks passed."
)

print(
    "\nValidated file:"
)

print(INPUT_FILE)

print("\n" + "=" * 70)
print("VALIDATION PASSED")
print("=" * 70)