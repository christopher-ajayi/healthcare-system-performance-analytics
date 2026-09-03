"""
transform_cihi_standardized_rates.py

Purpose:
    Transform cleaned CIHI Table 2 — Inpatient Hospitalizations:
    Standardized Rates, 1995–1996 to 2023–2024.

Input:
    data/processed/demand/cihi_standardized_rates_clean.csv

Output:
    data/processed/demand/cihi_standardized_rates_transformed.csv

Methodological considerations:
    CIHI changed the standard population used for direct
    standardization beginning in 2014–2015.

    1995–1996 through 2013–2014:
        2001 Canadian population estimates

    2014–2015 onward:
        2011 Canadian population estimates

    Rates across this break should NOT be directly compared.

    The CIHI hospitalization rate is reported per 100,000 population.
    A derived per-1,000 measure is created by dividing the CIHI rate
    by 100. The original CIHI rate is preserved unchanged.
"""

from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "demand"
    / "cihi_standardized_rates_clean.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "demand"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "cihi_standardized_rates_transformed.csv"
)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("CIHI TABLE 2 — STANDARDIZED RATES TRANSFORMATION")
print("=" * 70)

print(f"\nInput file:\n{INPUT_FILE}")
print(f"Output file:\n{OUTPUT_FILE}")


# ============================================================
# FILE CHECK
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Cleaned Table 2 file not found:\n{INPUT_FILE}"
    )


# ============================================================
# LOAD CLEAN DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print(f"\nInput shape: {df.shape}")


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
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

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "Required columns are missing from cleaned Table 2:\n"
        + "\n".join(
            f"  - {column}"
            for column in missing_columns
        )
    )


# ============================================================
# SELECT VARIABLES
# ============================================================

df = df[required_columns].copy()


# ============================================================
# DATA TYPES
# ============================================================

df["fiscal_year_start"] = pd.to_numeric(
    df["fiscal_year_start"],
    errors="coerce"
).astype("Int64")

df["fiscal_year_end"] = pd.to_numeric(
    df["fiscal_year_end"],
    errors="coerce"
).astype("Int64")

df["standardized_hospitalization_rate"] = pd.to_numeric(
    df["standardized_hospitalization_rate"],
    errors="coerce"
)

df["age_standardized_avg_los_days"] = pd.to_numeric(
    df["age_standardized_avg_los_days"],
    errors="coerce"
)

df["rate_available"] = df["rate_available"].astype(bool)

df["standardization_break"] = (
    df["standardization_break"].astype(bool)
)


# ============================================================
# DERIVED RATE — PER 1,000 POPULATION
# ============================================================

print("\nCreating derived hospitalization rate per 1,000...")

df["standardized_hospitalization_rate_per_1000"] = (
    df["standardized_hospitalization_rate"] / 100
)


# ============================================================
# RATE CONVERSION VALIDATION
# ============================================================

print("\nValidating rate conversion...")

available = df["rate_available"]

conversion_expected = (
    df.loc[available, "standardized_hospitalization_rate"]
    / 100
)

conversion_actual = (
    df.loc[available, "standardized_hospitalization_rate_per_1000"]
)

conversion_difference = (
    conversion_actual - conversion_expected
).abs()

MAX_TOLERANCE = 1e-10

if (
    not conversion_difference.empty
    and conversion_difference.max() > MAX_TOLERANCE
):
    raise ValueError(
        "Rate-per-1,000 conversion validation failed.\n"
        f"Maximum difference: "
        f"{conversion_difference.max()}"
    )

print(
    "Rate conversion validation passed."
)


# ============================================================
# SUPPRESSED / UNAVAILABLE RATE VALIDATION
# ============================================================

print("\nValidating suppressed observations...")

suppressed = ~available

suppressed_with_values = df.loc[
    suppressed,
    "standardized_hospitalization_rate_per_1000"
].notna().sum()

if suppressed_with_values > 0:
    raise ValueError(
        "Suppressed/unavailable records contain a derived "
        "per-1,000 hospitalization rate."
    )

print(
    f"Suppressed/unavailable observations: "
    f"{suppressed.sum()}"
)


# ============================================================
# STRUCTURAL COVERAGE
# ============================================================

expected_years = 29
expected_regions = 14
expected_rows = 406

year_count = df["fiscal_year"].nunique()
region_count = df["region"].nunique()
row_count = len(df)

print("\nStructural coverage:")
print(f"  Fiscal years: {year_count}")
print(f"  Jurisdictions: {region_count}")
print(f"  Records: {row_count}")

if year_count != expected_years:
    raise ValueError(
        f"Unexpected fiscal-year count: {year_count}. "
        f"Expected {expected_years}."
    )

if region_count != expected_regions:
    raise ValueError(
        f"Unexpected jurisdiction count: {region_count}. "
        f"Expected {expected_regions}."
    )

if row_count != expected_rows:
    raise ValueError(
        f"Unexpected number of records: {row_count}. "
        f"Expected {expected_rows}."
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
    f"\nDuplicate fiscal-year/region records: "
    f"{duplicate_count}"
)

if duplicate_count > 0:
    raise ValueError(
        "Duplicate fiscal-year/region records detected."
    )


# ============================================================
# STANDARDIZATION PERIOD VALIDATION
# ============================================================

print("\nValidating standardization periods...")

expected_pre_break = (
    df["fiscal_year_start"] <= 2013
)

expected_post_break = (
    df["fiscal_year_start"] >= 2014
)

period_error = (
    (
        expected_pre_break
        & (
            df["standardization_period"]
            != "2001_standard_population"
        )
    )
    |
    (
        expected_post_break
        & (
            df["standardization_period"]
            != "2011_standard_population"
        )
    )
)

if period_error.any():
    raise ValueError(
        "Standardization-period classification failed."
    )

print(
    "Standardization-period validation passed."
)


# ============================================================
# STANDARDIZATION BREAK VALIDATION
# ============================================================

break_rows = df["standardization_break"].sum()

expected_break_rows = expected_regions

print(
    f"\nRows in standardization-break year "
    f"(2014–2015): {break_rows}"
)

if break_rows != expected_break_rows:
    raise ValueError(
        "Unexpected number of records flagged as the "
        "2014–2015 standardization break."
    )


# ============================================================
# RATE AVAILABILITY VALIDATION
# ============================================================

available_count = df["rate_available"].sum()
suppressed_count = (~df["rate_available"]).sum()

print("\nRate availability:")
print(f"  Available: {available_count}")
print(f"  Suppressed/unavailable: {suppressed_count}")

if available_count != 402:
    raise ValueError(
        f"Unexpected number of available rates: "
        f"{available_count}. Expected 402."
    )

if suppressed_count != 4:
    raise ValueError(
        f"Unexpected number of suppressed rates: "
        f"{suppressed_count}. Expected 4."
    )


# ============================================================
# VALIDATE KNOWN SUPPRESSED OBSERVATIONS
# ============================================================

expected_suppressed = {
    ("2002–2003", "Nunavut"),
    ("2016–2017", "Nunavut"),
    ("2019–2020", "Nunavut"),
    ("2020–2021", "Nunavut"),
}

actual_suppressed = set(
    zip(
        df.loc[~df["rate_available"], "fiscal_year"],
        df.loc[~df["rate_available"], "region"],
    )
)

if actual_suppressed != expected_suppressed:
    raise ValueError(
        "Suppressed observation pattern does not match "
        "the expected CIHI Table 2 structure."
    )

print(
    "Suppressed-observation validation passed."
)


# ============================================================
# NUMERIC VALIDATION
# ============================================================

print("\nNumeric validation:")

available_rates = df.loc[
    df["rate_available"],
    "standardized_hospitalization_rate"
]

available_per_1000 = df.loc[
    df["rate_available"],
    "standardized_hospitalization_rate_per_1000"
]

available_los = df.loc[
    df["rate_available"],
    "age_standardized_avg_los_days"
]

if (available_rates < 0).any():
    raise ValueError(
        "Negative hospitalization rates detected."
    )

if (available_per_1000 < 0).any():
    raise ValueError(
        "Negative per-1,000 hospitalization rates detected."
    )

if (available_los < 0).any():
    raise ValueError(
        "Negative average length-of-stay values detected."
    )

print(
    "  Hospitalization rates: valid"
)

print(
    "  Per-1,000 rates: valid"
)

print(
    "  Average length of stay: valid"
)


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    by=[
        "fiscal_year_start",
        "region",
    ]
).reset_index(drop=True)


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
        "standardized_hospitalization_rate_per_1000",
        "age_standardized_avg_los_days",
        "rate_available",
        "standardization_period",
        "standardization_break",
    ]
]


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("CIHI TABLE 2 TRANSFORMATION COMPLETE")
print("=" * 70)

print(f"\nFinal shape: {df.shape}")

print("\nFinal columns:")

for column in df.columns:
    print(f"  - {column}")

print("\nRate coverage:")
print(
    f"  Available: {df['rate_available'].sum()}"
)

print(
    f"  Suppressed: {(~df['rate_available']).sum()}"
)

print("\nStandardization periods:")

print(
    df["standardization_period"]
    .value_counts()
    .to_string()
)

print(
    "\nRows in standardization-break year "
    "(2014–2015):"
)

print(
    df["standardization_break"].sum()
)

print("\nOutput file:")
print(OUTPUT_FILE)

print("\nFirst 10 transformed records:")

print(
    df.head(10).to_string(index=False)
)

print("\n" + "=" * 70)
print("TRANSFORMATION COMPLETE")
print("=" * 70)