"""
CIHI NHEX 2025 — PROCESSED DATASET VALIDATION

Validates the processed NHEX dataset after transformation.

Input:
    data/processed/spending/nhex_health_expenditure.csv

Output:
    Console validation report
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "spending"
    / "nhex_health_expenditure.csv"
)

EXPECTED_JURISDICTIONS = [
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
]

EXPECTED_START_YEAR = 1975
EXPECTED_END_YEAR = 2025

EXPECTED_FORECAST_YEARS = [2024, 2025]

# NHEX historical coverage:
# Nunavut does not have a full 1975–2025 historical series because
# it became a separate territory in 1999.
EXPECTED_JURISDICTION_START_YEAR = {
    "Alberta": 1975,
    "British Columbia": 1975,
    "Canada": 1975,
    "Manitoba": 1975,
    "New Brunswick": 1975,
    "Newfoundland and Labrador": 1975,
    "Northwest Territories": 1975,
    "Nova Scotia": 1975,
    "Nunavut": 1999,
    "Ontario": 1975,
    "Prince Edward Island": 1975,
    "Quebec": 1975,
    "Saskatchewan": 1975,
    "Yukon": 1975,
}

EXPECTED_JURISDICTION_END_YEAR = {
    jurisdiction: EXPECTED_END_YEAR
    for jurisdiction in EXPECTED_JURISDICTIONS
}

# Monetary reconciliation tolerance.
#
# The source values are floating-point representations of financial
# amounts. Tiny differences such as $0.000031 can arise from floating-
# point arithmetic even when the underlying financial values reconcile.
MONETARY_ABSOLUTE_TOLERANCE = 0.01


# ============================================================================
# LOAD DATA
# ============================================================================

df = pd.read_csv(INPUT_FILE)


# ============================================================================
# REQUIRED COLUMNS
# ============================================================================

required_columns = [
    "year",
    "province",
    "forecast_category",
    "total_health_expenditure",
    "total_health_expenditure_per_capita",
    "public_total",
    "public_per_capita",
    "public_share_pct",
    "private_total",
    "private_per_capita",
    "private_share_pct",
    "provincial_government_total",
    "provincial_government_per_capita",
    "territorial_government_total",
    "territorial_government_per_capita",
    "public_constant_2010",
    "public_constant_2010_per_capita",
    "private_constant_2010",
    "private_constant_2010_per_capita",
    "provincial_government_constant_2010",
    "provincial_government_constant_2010_per_capita",
    "territorial_government_constant_2010",
    "territorial_government_constant_2010_per_capita",
    "total_health_expenditure_growth_pct",
    "total_health_expenditure_per_capita_growth_pct",
]


# ============================================================================
# HEADER
# ============================================================================

print("=" * 70)
print("CIHI NHEX 2025 — PROCESSED DATASET VALIDATION")
print("=" * 70)


# ============================================================================
# 1. DATASET STRUCTURE
# ============================================================================

print("\n1. DATASET STRUCTURE")
print("-" * 70)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns):,}")

print("\nColumns:")
for column in df.columns:
    print(f"  - {column}")

missing_required = [
    column for column in required_columns
    if column not in df.columns
]

if not missing_required:
    print("\nRequired-column check:")
    print("PASS — all required columns are present.")
else:
    print("\nRequired-column check:")
    print("FAIL — missing required columns:")
    for column in missing_required:
        print(f"  - {column}")


# ============================================================================
# 2. YEAR VALIDATION
# ============================================================================

print("\n2. YEAR VALIDATION")
print("-" * 70)

min_year = int(df["year"].min())
max_year = int(df["year"].max())

print(f"Minimum year: {min_year}")
print(f"Maximum year: {max_year}")

expected_years = set(range(EXPECTED_START_YEAR, EXPECTED_END_YEAR + 1))
actual_years = set(df["year"].dropna().astype(int))

if actual_years == expected_years:
    print("PASS — complete 1975–2025 year range.")
else:
    print("FAIL — unexpected year coverage.")

    missing_years = sorted(expected_years - actual_years)
    unexpected_years = sorted(actual_years - expected_years)

    if missing_years:
        print(f"Missing years: {missing_years}")

    if unexpected_years:
        print(f"Unexpected years: {unexpected_years}")


# ============================================================================
# 3. JURISDICTION VALIDATION
# ============================================================================

print("\n3. JURISDICTION VALIDATION")
print("-" * 70)

actual_jurisdictions = sorted(df["province"].dropna().unique())
expected_jurisdictions_sorted = sorted(EXPECTED_JURISDICTIONS)

print(f"Jurisdictions: {len(actual_jurisdictions)}")

if actual_jurisdictions == expected_jurisdictions_sorted:
    print("PASS — all expected jurisdictions present.")
else:
    print("FAIL — jurisdiction set does not match expectations.")

    missing_jurisdictions = sorted(
        set(EXPECTED_JURISDICTIONS) - set(actual_jurisdictions)
    )

    unexpected_jurisdictions = sorted(
        set(actual_jurisdictions) - set(EXPECTED_JURISDICTIONS)
    )

    if missing_jurisdictions:
        print(f"Missing jurisdictions: {missing_jurisdictions}")

    if unexpected_jurisdictions:
        print(f"Unexpected jurisdictions: {unexpected_jurisdictions}")


# ============================================================================
# 4. PROVINCE × YEAR UNIQUENESS
# ============================================================================

print("\n4. PROVINCE × YEAR UNIQUENESS")
print("-" * 70)

duplicate_count = (
    df.duplicated(
        subset=["province", "year"]
    )
    .sum()
)

print(f"Duplicate province-year records: {duplicate_count}")

if duplicate_count == 0:
    print("PASS — one observation per province-year.")
else:
    print("FAIL — duplicate province-year records detected.")

    duplicates = (
        df[
            df.duplicated(
                subset=["province", "year"],
                keep=False,
            )
        ]
        .sort_values(["province", "year"])
    )

    print(duplicates[["province", "year"]].to_string(index=False))


# ============================================================================
# 5. RECORD COUNT BY JURISDICTION
# ============================================================================

print("\n5. RECORD COUNT BY JURISDICTION")
print("-" * 70)

jurisdiction_counts = (
    df.groupby("province")
    .size()
    .sort_index()
)

print(jurisdiction_counts)

coverage_failures = []

for jurisdiction in EXPECTED_JURISDICTIONS:

    if jurisdiction not in jurisdiction_counts.index:
        coverage_failures.append(
            (
                jurisdiction,
                "missing",
                None,
                None,
                None,
            )
        )
        continue

    jurisdiction_df = df[
        df["province"] == jurisdiction
    ]

    actual_start = int(jurisdiction_df["year"].min())
    actual_end = int(jurisdiction_df["year"].max())
    actual_count = len(jurisdiction_df)

    expected_start = EXPECTED_JURISDICTION_START_YEAR[jurisdiction]
    expected_end = EXPECTED_JURISDICTION_END_YEAR[jurisdiction]

    expected_count = expected_end - expected_start + 1

    if (
        actual_start != expected_start
        or actual_end != expected_end
        or actual_count != expected_count
    ):
        coverage_failures.append(
            (
                jurisdiction,
                "unexpected coverage",
                actual_start,
                actual_end,
                actual_count,
            )
        )


if not coverage_failures:
    print(
        "PASS — jurisdiction record counts match expected "
        "historical coverage."
    )
    print(
        "       Nunavut is correctly validated against its "
        "1999–2025 coverage."
    )
else:
    print("FAIL — unexpected jurisdiction coverage:")

    for (
        jurisdiction,
        status,
        actual_start,
        actual_end,
        actual_count,
    ) in coverage_failures:

        if status == "missing":
            print(f"  {jurisdiction}: missing")

        else:
            expected_start = (
                EXPECTED_JURISDICTION_START_YEAR[jurisdiction]
            )

            expected_end = (
                EXPECTED_JURISDICTION_END_YEAR[jurisdiction]
            )

            expected_count = (
                expected_end - expected_start + 1
            )

            print(
                f"  {jurisdiction}: "
                f"{actual_count} records "
                f"({actual_start}–{actual_end}); "
                f"expected {expected_count} "
                f"({expected_start}–{expected_end})"
            )


# ============================================================================
# 6. FORECAST VALIDATION
# ============================================================================

print("\n6. FORECAST VALIDATION")
print("-" * 70)

print(df["forecast_category"].value_counts())

forecast_years = sorted(
    df.loc[
        df["forecast_category"] == "f",
        "year",
    ]
    .dropna()
    .astype(int)
    .unique()
)

print(f"\nForecast years: {forecast_years}")

if forecast_years == EXPECTED_FORECAST_YEARS:
    print("PASS — forecast years are 2024 and 2025.")
else:
    print("FAIL — unexpected forecast years.")


# ============================================================================
# 7. TOTAL EXPENDITURE RECONCILIATION
# ============================================================================

print("\n7. TOTAL EXPENDITURE RECONCILIATION")
print("-" * 70)

calculated_total = (
    df["public_total"]
    + df["private_total"]
)

total_difference = (
    df["total_health_expenditure"]
    - calculated_total
)

total_match = np.isclose(
    df["total_health_expenditure"],
    calculated_total,
    rtol=0,
    atol=MONETARY_ABSOLUTE_TOLERANCE,
    equal_nan=False,
)

matching_records = int(total_match.sum())

max_absolute_difference = (
    total_difference.abs().max()
)

print(
    f"Matching records: "
    f"{matching_records:,} / {len(df):,}"
)

print(
    "Maximum absolute difference: "
    f"{max_absolute_difference:.6f}"
)

if matching_records == len(df):
    print(
        "PASS — total expenditure = "
        "public + private within financial tolerance."
    )
else:
    print("FAIL — total expenditure reconciliation failed.")

    failed_reconciliation = (
        df.loc[
            ~total_match,
            [
                "year",
                "province",
                "total_health_expenditure",
                "public_total",
                "private_total",
            ],
        ]
        .copy()
    )

    failed_reconciliation["difference"] = (
        failed_reconciliation["total_health_expenditure"]
        - (
            failed_reconciliation["public_total"]
            + failed_reconciliation["private_total"]
        )
    )

    print(failed_reconciliation.to_string(index=False))


# ============================================================================
# 8. FINANCING SHARE RECONCILIATION
# ============================================================================

print("\n8. FINANCING SHARE RECONCILIATION")
print("-" * 70)

share_sum = (
    df["public_share_pct"]
    + df["private_share_pct"]
)

share_difference = (
    share_sum - 100
)

share_match = np.isclose(
    share_sum,
    100,
    rtol=0,
    atol=1e-9,
)

matching_share_records = int(
    share_match.sum()
)

max_share_difference = (
    share_difference.abs().max()
)

print(
    f"Matching records: "
    f"{matching_share_records:,} / {len(df):,}"
)

print(
    "Maximum absolute difference from 100%: "
    f"{max_share_difference:.10f}"
)

if matching_share_records == len(df):
    print(
        "PASS — Public share + Private share = 100%."
    )
else:
    print(
        "FAIL — financing shares do not reconcile."
    )


# ============================================================================
# 9. PER-CAPITA RECONCILIATION
# ============================================================================

print("\n9. PER-CAPITA RECONCILIATION")
print("-" * 70)

calculated_per_capita = (
    df["public_per_capita"]
    + df["private_per_capita"]
)

per_capita_difference = (
    df["total_health_expenditure_per_capita"]
    - calculated_per_capita
)

per_capita_match = np.isclose(
    df["total_health_expenditure_per_capita"],
    calculated_per_capita,
    rtol=0,
    atol=1e-9,
    equal_nan=False,
)

matching_per_capita_records = int(
    per_capita_match.sum()
)

max_per_capita_difference = (
    per_capita_difference.abs().max()
)

print(
    f"Matching records: "
    f"{matching_per_capita_records:,} / {len(df):,}"
)

print(
    "Maximum absolute difference: "
    f"{max_per_capita_difference:.10f}"
)

if matching_per_capita_records == len(df):
    print(
        "PASS — total per capita = "
        "public + private per capita."
    )
else:
    print(
        "FAIL — per-capita reconciliation failed."
    )


# ============================================================================
# 10. GROWTH-RATE VALIDATION
# ============================================================================

print("\n10. GROWTH-RATE VALIDATION")
print("-" * 70)

expected_growth = (
    df.sort_values(["province", "year"])
    .groupby("province")["total_health_expenditure"]
    .pct_change()
    * 100
)

growth_difference = (
    df["total_health_expenditure_growth_pct"]
    - expected_growth
)

growth_match = np.isclose(
    df["total_health_expenditure_growth_pct"],
    expected_growth,
    rtol=0,
    atol=1e-9,
    equal_nan=True,
)

matching_growth_observations = int(
    growth_match.sum()
)

print(
    f"Matching growth observations: "
    f"{matching_growth_observations:,} / {len(df):,}"
)

if matching_growth_observations == len(df):
    print(
        "PASS — total expenditure growth rates are correct."
    )
else:
    print(
        "FAIL — total expenditure growth rates "
        "require review."
    )


# ============================================================================
# 11. PER-CAPITA GROWTH-RATE VALIDATION
# ============================================================================

print("\n11. PER-CAPITA GROWTH-RATE VALIDATION")
print("-" * 70)

expected_per_capita_growth = (
    df.sort_values(["province", "year"])
    .groupby("province")[
        "total_health_expenditure_per_capita"
    ]
    .pct_change()
    * 100
)

per_capita_growth_difference = (
    df["total_health_expenditure_per_capita_growth_pct"]
    - expected_per_capita_growth
)

per_capita_growth_match = np.isclose(
    df["total_health_expenditure_per_capita_growth_pct"],
    expected_per_capita_growth,
    rtol=0,
    atol=1e-9,
    equal_nan=True,
)

matching_per_capita_growth_observations = int(
    per_capita_growth_match.sum()
)

print(
    f"Matching growth observations: "
    f"{matching_per_capita_growth_observations:,} "
    f"/ {len(df):,}"
)

if matching_per_capita_growth_observations == len(df):
    print(
        "PASS — total expenditure per-capita "
        "growth rates are correct."
    )
else:
    print(
        "FAIL — total expenditure per-capita "
        "growth rates require review."
    )


# ============================================================================
# 12. NEGATIVE FINANCIAL VALUES
# ============================================================================

print("\n12. NEGATIVE FINANCIAL VALUES")
print("-" * 70)

financial_columns = [
    "total_health_expenditure",
    "total_health_expenditure_per_capita",
    "public_total",
    "public_per_capita",
    "private_total",
    "private_per_capita",
    "provincial_government_total",
    "provincial_government_per_capita",
    "territorial_government_total",
    "territorial_government_per_capita",
    "public_constant_2010",
    "public_constant_2010_per_capita",
    "private_constant_2010",
    "private_constant_2010_per_capita",
    "provincial_government_constant_2010",
    "provincial_government_constant_2010_per_capita",
    "territorial_government_constant_2010",
    "territorial_government_constant_2010_per_capita",
]

negative_counts = (
    df[financial_columns]
    .lt(0)
    .sum()
)

print(negative_counts)

if negative_counts.sum() == 0:
    print("\nPASS — no negative financial values.")
else:
    print("\nFAIL — negative financial values detected.")


# ============================================================================
# 13. STRUCTURAL GOVERNMENT MISSINGNESS
# ============================================================================

print("\n13. STRUCTURAL GOVERNMENT MISSINGNESS")
print("-" * 70)

province_names = set(
    EXPECTED_JURISDICTIONS
) - {
    "Northwest Territories",
    "Nunavut",
    "Yukon",
}

territory_names = {
    "Northwest Territories",
    "Nunavut",
    "Yukon",
}

provincial_columns = [
    "provincial_government_total",
    "provincial_government_per_capita",
    "provincial_government_constant_2010",
    "provincial_government_constant_2010_per_capita",
]

territorial_columns = [
    "territorial_government_total",
    "territorial_government_per_capita",
    "territorial_government_constant_2010",
    "territorial_government_constant_2010_per_capita",
]

provincial_missing_correct = df.loc[
    df["province"].isin(territory_names),
    provincial_columns,
].isna().all().all()

provincial_present_correct = (
    df.loc[
        df["province"].isin(province_names),
        provincial_columns,
    ]
    .notna()
    .all()
    .all()
)

territorial_missing_correct = df.loc[
    df["province"].isin(province_names),
    territorial_columns,
].isna().all().all()

territorial_present_correct = (
    df.loc[
        df["province"].isin(territory_names),
        territorial_columns,
    ]
    .notna()
    .all()
    .all()
)

if (
    provincial_missing_correct
    and provincial_present_correct
):
    print(
        "PASS — Provincial Government is structurally "
        "missing for territories."
    )
else:
    print(
        "FAIL — Provincial Government structural "
        "missingness is unexpected."
    )

if (
    territorial_missing_correct
    and territorial_present_correct
):
    print(
        "PASS — Territorial Government is structurally "
        "missing for provinces/Canada."
    )
else:
    print(
        "FAIL — Territorial Government structural "
        "missingness is unexpected."
    )


# ============================================================================
# 14. MISSING VALUES
# ============================================================================

print("\n14. MISSING VALUES")
print("-" * 70)

missing_counts = df.isna().sum()

nonzero_missing = (
    missing_counts[
        missing_counts > 0
    ]
)

print(nonzero_missing)

expected_missing_columns = {
    "provincial_government_total",
    "provincial_government_per_capita",
    "territorial_government_total",
    "territorial_government_per_capita",
    "provincial_government_constant_2010",
    "provincial_government_constant_2010_per_capita",
    "territorial_government_constant_2010",
    "territorial_government_constant_2010_per_capita",
    "total_health_expenditure_growth_pct",
    "total_health_expenditure_per_capita_growth_pct",
}

unexpected_missing_columns = set(
    nonzero_missing.index
) - expected_missing_columns

if not unexpected_missing_columns:
    print(
        "\nPASS — missing values are confined to "
        "expected structural/derived fields."
    )
else:
    print(
        "\nFAIL — unexpected missing values found in:"
    )

    for column in sorted(unexpected_missing_columns):
        print(f"  - {column}")


# ============================================================================
# 15. CONSTANT-DOLLAR AVAILABILITY
# ============================================================================

print("\n15. CONSTANT-DOLLAR AVAILABILITY")
print("-" * 70)

constant_dollar_columns = [
    "public_constant_2010",
    "private_constant_2010",
    "provincial_government_constant_2010",
    "territorial_government_constant_2010",
]

for column in constant_dollar_columns:

    available = int(
        df[column].notna().sum()
    )

    unavailable = int(
        df[column].isna().sum()
    )

    print(
        f"{column}: "
        f"{available:,} available / "
        f"{unavailable:,} unavailable"
    )


# ============================================================================
# 16. FINAL VALIDATION SUMMARY
# ============================================================================

print("\n16. FINAL VALIDATION SUMMARY")
print("-" * 70)

checks = {
    "Required columns": not missing_required,
    "Year coverage": actual_years == expected_years,
    "Jurisdiction coverage": not coverage_failures,
    "Province-year uniqueness": duplicate_count == 0,
    "Total reconciliation": matching_records == len(df),
    "Financing shares": matching_share_records == len(df),
    "Per-capita reconciliation": (
        matching_per_capita_records == len(df)
    ),
    "Total growth rates": (
        matching_growth_observations == len(df)
    ),
    "Per-capita growth rates": (
        matching_per_capita_growth_observations == len(df)
    ),
    "No negative values": negative_counts.sum() == 0,
    "Expected structural missingness": (
        provincial_missing_correct
        and provincial_present_correct
        and territorial_missing_correct
        and territorial_present_correct
    ),
    "Expected missing-value pattern": (
        not unexpected_missing_columns
    ),
}

for check_name, passed in checks.items():

    status = "PASS" if passed else "FAIL"

    print(
        f"{status:<6} {check_name}"
    )


# ============================================================================
# FINAL STATUS
# ============================================================================

all_passed = all(checks.values())

print("\n" + "=" * 70)

if all_passed:
    print(
        "NHEX PROCESSED DATASET VALIDATION PASSED"
    )
else:
    print(
        "NHEX PROCESSED DATASET VALIDATION REQUIRES REVIEW"
    )

print("=" * 70)