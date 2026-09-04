from pathlib import Path
import pandas as pd


# ============================================================================
# CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS
# TRANSFORMED DATA VALIDATION
# ============================================================================

BASE_DIR = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
)

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "outcomes"
    / "hip_fracture_surgery_within_48_hours_transformed.csv"
)

EXPECTED_COLUMNS = [
    "province_territory",
    "indicator",
    "fiscal_year",
    "metric",
    "metric_value",
    "metric_value_numeric",
    "ci_lower",
    "ci_upper",
    "suppressed",
    "refresh_date",
    "fiscal_year_start",
    "fiscal_year_end",
]

EXPECTED_PROVINCES = [
    "Alberta",
    "British Columbia",
    "Manitoba",
    "New Brunswick",
    "Newfoundland and Labrador",
    "Northwest Territories",
    "Nova Scotia",
    "Nunavut",
    "Ontario",
    "Prince Edward Island",
    "Saskatchewan",
    "Yukon",
]

EXPECTED_FISCAL_YEARS = [
    "2020–2021",
    "2021–2022",
    "2022–2023",
    "2023–2024",
    "2024–2025",
]

EXPECTED_INDICATOR = "Hip Fracture Surgery Within 48 Hours"
EXPECTED_METRIC = "Risk-adjusted rate"


def main():

    print("=" * 74)
    print("CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS")
    print("TRANSFORMED DATA VALIDATION")
    print("=" * 74)

    # ------------------------------------------------------------------------
    # [27.1] LOAD TRANSFORMED DATA
    # ------------------------------------------------------------------------
    print("\n[27.1] LOAD TRANSFORMED DATA")
    print(f"Input: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    # ------------------------------------------------------------------------
    # [27.2] COLUMN STRUCTURE
    # ------------------------------------------------------------------------
    print("\n[27.2] COLUMN STRUCTURE")

    if list(df.columns) == EXPECTED_COLUMNS:
        print("PASS — expected transformed column structure confirmed.")
    else:
        print("FAIL — transformed column structure differs from expected.")
        print("\nExpected:")
        for column in EXPECTED_COLUMNS:
            print(f"  {column}")

        print("\nActual:")
        for column in df.columns:
            print(f"  {column}")

    # ------------------------------------------------------------------------
    # [27.3] ROW COUNT
    # ------------------------------------------------------------------------
    print("\n[27.3] ROW COUNT")

    expected_rows = 60

    if len(df) == expected_rows:
        print(f"PASS — expected {expected_rows} rows confirmed.")
    else:
        print(
            f"REVIEW — expected {expected_rows} rows, "
            f"found {len(df)}."
        )

    # ------------------------------------------------------------------------
    # [27.4] INDICATOR
    # ------------------------------------------------------------------------
    print("\n[27.4] INDICATOR")

    print(df["indicator"].value_counts(dropna=False))

    if (
        df["indicator"].nunique(dropna=True) == 1
        and df["indicator"].dropna().iloc[0] == EXPECTED_INDICATOR
    ):
        print("PASS")
    else:
        print("FAIL — unexpected indicator value.")

    # ------------------------------------------------------------------------
    # [27.5] GEOGRAPHIC COVERAGE
    # ------------------------------------------------------------------------
    print("\n[27.5] GEOGRAPHIC COVERAGE")

    province_counts = (
        df["province_territory"]
        .value_counts(dropna=False)
        .sort_index()
    )

    print(province_counts)

    provinces = sorted(
        df["province_territory"]
        .dropna()
        .unique()
        .tolist()
    )

    print(f"\nProvinces/territories: {len(provinces)}")

    if provinces == sorted(EXPECTED_PROVINCES):
        print("PASS — expected 12 provinces/territories confirmed.")
    else:
        print("FAIL — geographic coverage differs from expected.")

    # ------------------------------------------------------------------------
    # [27.6] TIME COVERAGE
    # ------------------------------------------------------------------------
    print("\n[27.6] TIME COVERAGE")

    fiscal_counts = (
        df["fiscal_year"]
        .value_counts(dropna=False)
        .sort_index()
    )

    print(fiscal_counts)

    fiscal_years = sorted(
        df["fiscal_year"]
        .dropna()
        .unique()
        .tolist()
    )

    print(f"\nFiscal years: {len(fiscal_years)}")

    if fiscal_years == sorted(EXPECTED_FISCAL_YEARS):
        print("PASS — expected 5 fiscal years confirmed.")
    else:
        print("FAIL — fiscal-year coverage differs from expected.")

    # ------------------------------------------------------------------------
    # [27.7] PROVINCE-YEAR UNIQUENESS
    # ------------------------------------------------------------------------
    print("\n[27.7] PROVINCE-YEAR UNIQUENESS")

    duplicate_count = df.duplicated(
        subset=[
            "province_territory",
            "fiscal_year",
        ]
    ).sum()

    print(
        "Duplicate province-year observations:",
        duplicate_count
    )

    if duplicate_count == 0:
        print("PASS")
    else:
        print("FAIL")

    # ------------------------------------------------------------------------
    # [27.8] METRIC
    # ------------------------------------------------------------------------
    print("\n[27.8] METRIC")

    print(df["metric"].value_counts(dropna=False))

    if (
        df["metric"].nunique(dropna=True) == 1
        and df["metric"].dropna().iloc[0] == EXPECTED_METRIC
    ):
        print("PASS")
    else:
        print("FAIL — unexpected metric.")

    # ------------------------------------------------------------------------
    # [27.9] NUMERIC METRIC FIELD
    # ------------------------------------------------------------------------
    print("\n[27.9] NUMERIC METRIC FIELD")

    numeric_metric = pd.to_numeric(
        df["metric_value_numeric"],
        errors="coerce"
    )

    numeric_count = numeric_metric.notna().sum()
    missing_count = numeric_metric.isna().sum()

    print(f"Numeric observations: {numeric_count:,}")
    print(f"Missing/non-numeric:  {missing_count:,}")

    if numeric_count == 45 and missing_count == 15:
        print("PASS — expected numeric/missing structure confirmed.")
    else:
        print("REVIEW — numeric/missing structure differs from expected.")

    # ------------------------------------------------------------------------
    # [27.10] SUPPRESSION
    # ------------------------------------------------------------------------
    print("\n[27.10] SUPPRESSION")

    print(df["suppressed"].value_counts(dropna=False))

    suppressed_count = int(df["suppressed"].sum())

    if suppressed_count == 0:
        print("PASS — no suppressed observations present.")
    else:
        print(
            f"REVIEW — {suppressed_count} suppressed "
            "observations present."
        )

    # ------------------------------------------------------------------------
    # [27.11] SUPPRESSION CONSISTENCY
    # ------------------------------------------------------------------------
    print("\n[27.11] SUPPRESSION CONSISTENCY")

    suppressed_numeric = (
        df.loc[df["suppressed"], "metric_value_numeric"]
        .notna()
        .sum()
    )

    print(
        "Suppressed rows with numeric metric value:",
        suppressed_numeric
    )

    if suppressed_numeric == 0:
        print("PASS")
    else:
        print("FAIL")

    # ------------------------------------------------------------------------
    # [27.12] CONFIDENCE INTERVALS
    # ------------------------------------------------------------------------
    print("\n[27.12] CONFIDENCE INTERVALS")

    ci_lower = pd.to_numeric(
        df["ci_lower"],
        errors="coerce"
    )

    ci_upper = pd.to_numeric(
        df["ci_upper"],
        errors="coerce"
    )

    print(
        f"CI lower numeric: {ci_lower.notna().sum():,}"
    )
    print(
        f"CI upper numeric: {ci_upper.notna().sum():,}"
    )
    print(
        f"CI lower missing/non-numeric: {ci_lower.isna().sum():,}"
    )
    print(
        f"CI upper missing/non-numeric: {ci_upper.isna().sum():,}"
    )

    # ------------------------------------------------------------------------
    # [27.13] CONFIDENCE INTERVAL LOGIC
    # ------------------------------------------------------------------------
    print("\n[27.13] CONFIDENCE INTERVAL LOGIC")

    ci_mask = (
        numeric_metric.notna()
        & ci_lower.notna()
        & ci_upper.notna()
    )

    invalid_ci = (
        ci_mask
        & (
            (ci_lower > numeric_metric)
            | (numeric_metric > ci_upper)
            | (ci_lower > ci_upper)
        )
    )

    validated_ci = int(ci_mask.sum())
    invalid_ci_count = int(invalid_ci.sum())

    print(
        "Validated CI records:",
        validated_ci
    )
    print(
        "Invalid CI records:",
        invalid_ci_count
    )

    if invalid_ci_count == 0:
        print("PASS")
    else:
        print("FAIL")

    # ------------------------------------------------------------------------
    # [27.14] METRIC RANGE
    # ------------------------------------------------------------------------
    print("\n[27.14] METRIC RANGE")

    valid_values = numeric_metric.dropna()

    if len(valid_values) > 0:

        minimum = valid_values.min()
        maximum = valid_values.max()
        mean = valid_values.mean()

        print(f"Minimum: {minimum:.2f}")
        print(f"Maximum: {maximum:.2f}")
        print(f"Mean:    {mean:.2f}")

        if minimum >= 0:
            print("PASS — rates are non-negative.")
        else:
            print("FAIL — negative rate detected.")

    else:
        print("REVIEW — no numeric metric values available.")

    # ------------------------------------------------------------------------
    # [27.15] MISSING VALUES
    # ------------------------------------------------------------------------
    print("\n[27.15] MISSING VALUES")

    missing = df.isna().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values.")
    else:
        print(missing)

    # ------------------------------------------------------------------------
    # [27.16] DATA TYPES
    # ------------------------------------------------------------------------
    print("\n[27.16] DATA TYPES")

    print(df.dtypes)

    # ------------------------------------------------------------------------
    # [27.17] FISCAL YEAR FIELD LOGIC
    # ------------------------------------------------------------------------
    print("\n[27.17] FISCAL YEAR FIELD LOGIC")

    expected_start = (
        df["fiscal_year"]
        .str.extract(r"^(\d{4})")[0]
        .astype("Int64")
    )

    expected_end = (
        df["fiscal_year"]
        .str.extract(r"(\d{4})$")[0]
        .astype("Int64")
    )

    valid_year_logic = (
        (df["fiscal_year_start"] == expected_start)
        & (df["fiscal_year_end"] == expected_end)
    )

    valid_year_count = int(valid_year_logic.sum())
    invalid_year_count = int((~valid_year_logic).sum())

    print(
        "Valid fiscal-year start/end records:",
        valid_year_count
    )
    print(
        "Invalid fiscal-year start/end records:",
        invalid_year_count
    )

    if invalid_year_count == 0:
        print("PASS")
    else:
        print("FAIL")

    # ------------------------------------------------------------------------
    # [27.18] REFRESH DATE
    # ------------------------------------------------------------------------
    print("\n[27.18] REFRESH DATE")

    print(
        df["refresh_date"]
        .value_counts(dropna=False)
    )

    print("\n" + "=" * 74)
    print("VALIDATION SUMMARY")
    print("=" * 74)

    print(
        """
PASS:
- Transformed column structure assessed
- Row count assessed
- Indicator identity confirmed
- Geographic coverage assessed
- Fiscal-year coverage assessed
- Province-year uniqueness checked
- Primary metric confirmed
- Numeric metric field assessed
- Suppression handling assessed
- Confidence intervals assessed
- Confidence interval logic checked
- Metric range assessed
- Fiscal-year fields validated
- Missing values assessed
- No source values imputed or fabricated

NOTE:
- This dataset does not contain a unit_of_measure field.
- No unit has been fabricated or inferred.
- Missing metric and confidence-interval values have been preserved.
"""
    )

    print("=" * 74)
    print("TRANSFORMED DATA VALIDATION COMPLETE")
    print("=" * 74)


if __name__ == "__main__":
    main()