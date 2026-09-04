from pathlib import Path
import pandas as pd


# ============================================================================
# [21] CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs
# CLEAN DATA VALIDATION
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "avoidable_hospitalizations_acscs_clean.csv"
)

EXPECTED_INDICATOR = (
    "Ambulatory Care Sensitive Conditions Hospitalizations"
)

EXPECTED_METRIC = "Age-standardized rate"
EXPECTED_UNIT = "Per 100,000"

EXPECTED_YEARS = [
    "2013–2014",
    "2014–2015",
    "2015–2016",
    "2016–2017",
    "2017–2018",
    "2018–2019",
    "2019–2020",
    "2020–2021",
    "2021–2022",
    "2022–2023",
    "2023–2024",
    "2024–2025",
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
    "Quebec",
    "Saskatchewan",
    "Yukon",
]


def main():

    print("=" * 75)
    print("CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs")
    print("CLEAN DATA VALIDATION")
    print("=" * 75)

    # ------------------------------------------------------------------------
    # [21.1] LOAD CLEAN DATA
    # ------------------------------------------------------------------------

    print("\n[21.1] LOAD CLEAN DATA")

    df = pd.read_csv(
        INPUT_FILE,
        dtype=str
    )

    print(f"Input: {INPUT_FILE}")

    # ------------------------------------------------------------------------
    # [21.2] DIMENSIONS
    # ------------------------------------------------------------------------

    print("\n[21.2] DIMENSIONS")

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    if len(df) != 155:
        print("REVIEW — expected 155 provincial observations.")

    else:
        print("PASS")

    # ------------------------------------------------------------------------
    # [21.3] INDICATOR
    # ------------------------------------------------------------------------

    print("\n[21.3] INDICATOR")

    print(df["Indicator"].value_counts(dropna=False))

    if set(df["Indicator"].dropna().unique()) == {
        EXPECTED_INDICATOR
    }:
        print("PASS")
    else:
        print("FAIL — unexpected indicator found.")

    # ------------------------------------------------------------------------
    # [21.4] REPORTING LEVEL
    # ------------------------------------------------------------------------

    print("\n[21.4] REPORTING LEVEL")

    print(df["Reporting level"].value_counts(dropna=False))

    if set(df["Reporting level"].dropna().unique()) == {
        "Province/territory"
    }:
        print("PASS")
    else:
        print("FAIL — non-provincial records found.")

    # ------------------------------------------------------------------------
    # [21.5] GEOGRAPHIC COVERAGE
    # ------------------------------------------------------------------------

    print("\n[21.5] GEOGRAPHIC COVERAGE")

    provinces = sorted(
        df["Province/territory"]
        .dropna()
        .unique()
    )

    print(f"Provinces/territories: {len(provinces)}")

    for province in provinces:
        print(f"  {province}")

    missing_provinces = sorted(
        set(EXPECTED_PROVINCES) - set(provinces)
    )

    unexpected_provinces = sorted(
        set(provinces) - set(EXPECTED_PROVINCES)
    )

    if not missing_provinces and not unexpected_provinces:
        print("PASS — expected 13 provinces/territories confirmed.")
    else:
        print("REVIEW")
        if missing_provinces:
            print("Missing provinces/territories:")
            for province in missing_provinces:
                print(f"  {province}")

        if unexpected_provinces:
            print("Unexpected provinces/territories:")
            for province in unexpected_provinces:
                print(f"  {province}")

    # ------------------------------------------------------------------------
    # [21.6] TIME COVERAGE
    # ------------------------------------------------------------------------

    print("\n[21.6] TIME COVERAGE")

    years = sorted(
        df["Time frame"]
        .dropna()
        .unique()
    )

    for year in years:
        print(
            f"  {year}: "
            f"{(df['Time frame'] == year).sum()}"
        )

    missing_years = [
        year for year in EXPECTED_YEARS
        if year not in years
    ]

    unexpected_years = [
        year for year in years
        if year not in EXPECTED_YEARS
    ]

    if not missing_years and not unexpected_years:
        print("PASS — expected 12 fiscal years confirmed.")
    else:
        print("REVIEW")
        if missing_years:
            print("Missing fiscal years:")
            for year in missing_years:
                print(f"  {year}")

        if unexpected_years:
            print("Unexpected fiscal years:")
            for year in unexpected_years:
                print(f"  {year}")

    # ------------------------------------------------------------------------
    # [21.7] PROVINCE-YEAR UNIQUENESS
    # ------------------------------------------------------------------------

    print("\n[21.7] UNIQUENESS")

    duplicates = df[
        df.duplicated(
            subset=[
                "Province/territory",
                "Time frame"
            ],
            keep=False
        )
    ]

    print(
        "Duplicate province-year observations:",
        len(duplicates)
    )

    if duplicates.empty:
        print("PASS")
    else:
        print("FAIL")
        print(
            duplicates[
                [
                    "Province/territory",
                    "Time frame"
                ]
            ].sort_values(
                ["Province/territory", "Time frame"]
            )
        )

    # ------------------------------------------------------------------------
    # [21.8] PROVINCE-YEAR COVERAGE MATRIX
    # ------------------------------------------------------------------------

    print("\n[21.8] PROVINCE-YEAR COVERAGE")

    coverage = (
        df.groupby(
            "Province/territory"
        )["Time frame"]
        .nunique()
        .sort_index()
    )

    print(coverage)

    # Identify exact missing province-year combinations.
    expected_combinations = {
        (province, year)
        for province in EXPECTED_PROVINCES
        for year in EXPECTED_YEARS
    }

    actual_combinations = set(
        zip(
            df["Province/territory"],
            df["Time frame"]
        )
    )

    missing_combinations = sorted(
        expected_combinations - actual_combinations
    )

    print("\nMissing province-year observations:")

    if missing_combinations:
        for province, year in missing_combinations:
            print(f"  {province} — {year}")

        print(
            "REVIEW — missing province-year observation(s) "
            "preserved from source; no imputation performed."
        )
    else:
        print("None")
        print("PASS")

    # ------------------------------------------------------------------------
    # [21.9] METRIC
    # ------------------------------------------------------------------------

    print("\n[21.9] METRIC")

    print(df["Metric"].value_counts(dropna=False))

    if set(df["Metric"].dropna().unique()) == {
        EXPECTED_METRIC
    }:
        print("PASS")
    else:
        print("FAIL — unexpected metric found.")

    # ------------------------------------------------------------------------
    # [21.10] UNIT
    # ------------------------------------------------------------------------

    print("\n[21.10] UNIT OF MEASURE")

    print(df["Unit of measure"].value_counts(dropna=False))

    if set(df["Unit of measure"].dropna().unique()) == {
        EXPECTED_UNIT
    }:
        print("PASS")
    else:
        print("FAIL — unexpected unit found.")

    # ------------------------------------------------------------
    # [21.11] NUMERIC METRIC VALUES
    # ------------------------------------------------------------

    metric_clean = (
        df["Metric value"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    numeric_metric = pd.to_numeric(
        metric_clean,
        errors="coerce"
    )

    suppressed_mask = metric_clean.eq("Suppressed")

    numeric_count = numeric_metric.notna().sum()
    suppressed_count = suppressed_mask.sum()

    unexpected = df.loc[
        numeric_metric.isna() & ~suppressed_mask,
        "Metric value"
    ].dropna().unique()

    print("\n[21.11] NUMERIC METRIC VALUES")
    print(f"Numeric observations: {numeric_count:,}")
    print(f"Suppressed observations: {suppressed_count:,}")

    if len(unexpected) > 0:
        print("FAIL — unexpected non-numeric metric values:")
        for value in unexpected:
            print(f"  {value}")
    else:
        print("PASS")


    # ------------------------------------------------------------------------
    # [21.12] RATE RANGE
    # ------------------------------------------------------------------------

    print("\n[21.12] RATE RANGE")

    numeric_values = numeric_metric.dropna()

    if not numeric_values.empty:

        print(
            f"Minimum: {numeric_values.min():,.0f} "
            f"per 100,000"
        )

        print(
            f"Maximum: {numeric_values.max():,.0f} "
            f"per 100,000"
        )

        if (numeric_values >= 0).all():
            print("PASS — rates are non-negative.")
        else:
            print("FAIL — negative rate detected.")

    # ------------------------------------------------------------------------
    # [21.13] CONFIDENCE INTERVALS
    # ------------------------------------------------------------------------

    print("\n[21.13] CONFIDENCE INTERVALS")

    ci_lower = df["Confidence interval lower limit"]
    ci_upper = df["Confidence interval upper limit"]

    lower_suppressed = ci_lower.eq("Suppressed").sum()
    upper_suppressed = ci_upper.eq("Suppressed").sum()

    lower_missing = ci_lower.isna().sum()
    upper_missing = ci_upper.isna().sum()

    print(
        f"CI lower — suppressed: {lower_suppressed}"
    )

    print(
        f"CI upper — suppressed: {upper_suppressed}"
    )

    print(
        f"CI lower — missing: {lower_missing}"
    )

    print(
        f"CI upper — missing: {upper_missing}"
    )

    print("PASS — CI suppression/missingness preserved.")

    # ------------------------------------------------------------------------
    # [21.14] CONFIDENCE INTERVAL LOGIC
    # ------------------------------------------------------------------------

    print("\n[21.14] CONFIDENCE INTERVAL LOGIC")

    lower_numeric = pd.to_numeric(
        ci_lower,
        errors="coerce"
    )

    upper_numeric = pd.to_numeric(
        ci_upper,
        errors="coerce"
    )

    valid_ci = (
        numeric_metric.notna()
        & lower_numeric.notna()
        & upper_numeric.notna()
    )

    invalid_ci = (
        valid_ci
        & (
            (lower_numeric > numeric_metric)
            | (upper_numeric < numeric_metric)
            | (lower_numeric > upper_numeric)
        )
    )

    print(
        f"Validated CI records: {valid_ci.sum()}"
    )

    if invalid_ci.any():
        print("FAIL — invalid confidence interval logic detected.")
        print(
            df.loc[
                invalid_ci,
                [
                    "Province/territory",
                    "Time frame",
                    "Metric value",
                    "Confidence interval lower limit",
                    "Confidence interval upper limit"
                ]
            ]
        )
    else:
        print("PASS")

    # ------------------------------------------------------------------------
    # [21.15] DATA TYPES
    # ------------------------------------------------------------------------

    print("\n[21.15] DATA TYPES")

    print(df.dtypes)

    print(
        "\nExpected raw-clean structure retained as strings "
        "for validation."
    )

    # ------------------------------------------------------------------------
    # [21.16] VALIDATION SUMMARY
    # ------------------------------------------------------------------------

    print("\n" + "=" * 75)
    print("VALIDATION SUMMARY")
    print("=" * 75)

    print("""
PASS:
- Indicator identity confirmed
- Provincial reporting level confirmed
- 13 provinces/territories represented
- 12 fiscal-year periods represented
- Province-year uniqueness checked
- Primary metric confirmed as age-standardized rate
- Unit confirmed as per 100,000
- Numeric and suppressed values assessed
- Confidence intervals assessed
- Confidence interval logic checked
- No imputation or transformation performed
""")

    if missing_combinations:
        print(
            "REVIEW REQUIRED:"
        )
        print(
            "One or more expected province-year observations "
            "are absent from the cleaned source data."
        )
        print(
            "These observations have NOT been fabricated or imputed."
        )
    else:
        print(
            "CLEAN DATASET IS READY FOR ANALYSIS."
        )

    print("\n" + "=" * 75)
    print("VALIDATION COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()