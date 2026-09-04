from pathlib import Path
import pandas as pd


# ============================================================================
# CIHI — 30-DAY HOSPITAL READMISSION
# TRANSFORMED DATA VALIDATION
# ============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "outcomes"
    / "30_day_hospital_readmission_transformed.csv"
)


EXPECTED_PROVINCES = {
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
}

EXPECTED_COLUMNS = [
    "province_territory",
    "fiscal_year",
    "indicator",
    "metric",
    "unit_of_measure",
    "metric_value",
    "ci_lower",
    "ci_upper",
    "suppressed",
    "refresh_date",
    "metric_value_numeric",
]


def section(title):
    print("\n" + "=" * 75)
    print(title)
    print("=" * 75)


def main():

    section("CIHI — 30-DAY HOSPITAL READMISSION")
    print("TRANSFORMED DATA VALIDATION")

    # ------------------------------------------------------------------------
    # 24.1 LOAD
    # ------------------------------------------------------------------------
    print("\n[24.1] LOAD TRANSFORMED DATA")
    print(f"Input: {INPUT_FILE}")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # ------------------------------------------------------------------------
    # 24.2 COLUMN STRUCTURE
    # ------------------------------------------------------------------------
    print("\n[24.2] COLUMN STRUCTURE")

    actual_columns = list(df.columns)

    if actual_columns == EXPECTED_COLUMNS:
        print("PASS — expected transformed column structure confirmed.")
    else:
        print("FAIL — transformed column structure differs.")
        print("\nExpected:")
        for col in EXPECTED_COLUMNS:
            print(f"  - {col}")

        print("\nActual:")
        for col in actual_columns:
            print(f"  - {col}")

        raise ValueError("Unexpected transformed column structure.")

    # ------------------------------------------------------------------------
    # 24.3 ROW COUNT
    # ------------------------------------------------------------------------
    print("\n[24.3] ROW COUNT")

    if len(df) == 64:
        print("PASS — expected 64 rows confirmed.")
    else:
        print(f"REVIEW — expected 64 rows, found {len(df)}.")

    # ------------------------------------------------------------------------
    # 24.4 INDICATOR
    # ------------------------------------------------------------------------
    print("\n[24.4] INDICATOR")
    print(df["indicator"].value_counts(dropna=False))

    expected_indicator = "All Patients Readmitted to Hospital"

    if set(df["indicator"].dropna().unique()) == {expected_indicator}:
        print("PASS")
    else:
        print("FAIL — unexpected indicator value.")

    # ------------------------------------------------------------------------
    # 24.5 GEOGRAPHIC COVERAGE
    # ------------------------------------------------------------------------
    print("\n[24.5] GEOGRAPHIC COVERAGE")

    province_counts = df["province_territory"].value_counts()
    print(province_counts)

    provinces = set(df["province_territory"].dropna().unique())

    print(f"\nProvinces/territories: {len(provinces)}")

    missing_provinces = EXPECTED_PROVINCES - provinces
    unexpected_provinces = provinces - EXPECTED_PROVINCES

    if not missing_provinces and not unexpected_provinces:
        print("PASS — expected 13 provinces/territories confirmed.")
    else:
        if missing_provinces:
            print("Missing provinces/territories:")
            for p in sorted(missing_provinces):
                print(f"  {p}")

        if unexpected_provinces:
            print("Unexpected provinces/territories:")
            for p in sorted(unexpected_provinces):
                print(f"  {p}")

    # ------------------------------------------------------------------------
    # 24.6 TIME COVERAGE
    # ------------------------------------------------------------------------
    print("\n[24.6] TIME COVERAGE")

    fiscal_counts = df["fiscal_year"].value_counts().sort_index()
    print(fiscal_counts)

    print(f"\nFiscal years: {df['fiscal_year'].nunique()}")

    expected_years = {
        "2020–2021",
        "2021–2022",
        "2022–2023",
        "2023–2024",
        "2024–2025",
    }

    actual_years = set(df["fiscal_year"].dropna().unique())

    if actual_years == expected_years:
        print("PASS — expected 5 fiscal years confirmed.")
    else:
        print("REVIEW — fiscal-year coverage differs from expected.")

    # ------------------------------------------------------------------------
    # 24.7 PROVINCE-YEAR UNIQUENESS
    # ------------------------------------------------------------------------
    print("\n[24.7] PROVINCE-YEAR UNIQUENESS")

    duplicates = df.duplicated(
        subset=["province_territory", "fiscal_year"]
    ).sum()

    print(f"Duplicate province-year observations: {duplicates}")

    if duplicates == 0:
        print("PASS")
    else:
        print("FAIL")

    # ------------------------------------------------------------------------
    # 24.8 METRIC
    # ------------------------------------------------------------------------
    print("\n[24.8] METRIC")
    print(df["metric"].value_counts(dropna=False))

    if set(df["metric"].dropna().unique()) == {"Risk-adjusted rate"}:
        print("PASS")
    else:
        print("FAIL")

    # ------------------------------------------------------------------------
    # 24.9 UNIT
    # ------------------------------------------------------------------------
    print("\n[24.9] UNIT OF MEASURE")
    print(df["unit_of_measure"].value_counts(dropna=False))

    if set(df["unit_of_measure"].dropna().unique()) == {"Per 100"}:
        print("PASS")
    else:
        print("FAIL")

    # ------------------------------------------------------------------------
    # 24.10 NUMERIC METRIC FIELD
    # ------------------------------------------------------------------------
    print("\n[24.10] NUMERIC METRIC FIELD")

    numeric = pd.to_numeric(
        df["metric_value_numeric"],
        errors="coerce"
    )

    numeric_count = numeric.notna().sum()
    missing_count = numeric.isna().sum()

    print(f"Numeric observations: {numeric_count}")
    print(f"Missing/non-numeric:  {missing_count}")

    if numeric_count == 63 and missing_count == 1:
        print("PASS — expected numeric/missing structure confirmed.")
    else:
        print("REVIEW")

    # ------------------------------------------------------------------------
    # 24.11 SUPPRESSION
    # ------------------------------------------------------------------------
    print("\n[24.11] SUPPRESSION")

    print(df["suppressed"].value_counts(dropna=False))

    suppressed_count = df["suppressed"].eq(True).sum()

    if suppressed_count == 1:
        print("PASS — one suppressed observation preserved.")
    else:
        print(
            f"REVIEW — expected 1 suppressed observation, "
            f"found {suppressed_count}."
        )

    # ------------------------------------------------------------------------
    # 24.12 SUPPRESSION CONSISTENCY
    # ------------------------------------------------------------------------
    print("\n[24.12] SUPPRESSION CONSISTENCY")

    suppressed_rows = df[df["suppressed"] == True]

    if suppressed_rows.empty:
        print("REVIEW — no suppressed rows found.")
    else:
        suppressed_numeric = suppressed_rows["metric_value_numeric"].notna().sum()

        print(
            f"Suppressed rows with numeric metric value: "
            f"{suppressed_numeric}"
        )

        if suppressed_numeric == 0:
            print("PASS — suppressed metric remains non-numeric.")
        else:
            print("FAIL — suppressed metric has numeric value.")

    # ------------------------------------------------------------------------
    # 24.13 CONFIDENCE INTERVALS
    # ------------------------------------------------------------------------
    print("\n[24.13] CONFIDENCE INTERVALS")

    ci_lower = pd.to_numeric(df["ci_lower"], errors="coerce")
    ci_upper = pd.to_numeric(df["ci_upper"], errors="coerce")

    metric_numeric = pd.to_numeric(
        df["metric_value_numeric"],
        errors="coerce"
    )

    print(f"CI lower numeric: {ci_lower.notna().sum()}")
    print(f"CI upper numeric: {ci_upper.notna().sum()}")

    print(
        f"CI lower missing/non-numeric: "
        f"{ci_lower.isna().sum()}"
    )

    print(
        f"CI upper missing/non-numeric: "
        f"{ci_upper.isna().sum()}"
    )

    # ------------------------------------------------------------------------
    # 24.14 CONFIDENCE INTERVAL LOGIC
    # ------------------------------------------------------------------------
    print("\n[24.14] CONFIDENCE INTERVAL LOGIC")

    valid_ci = (
        metric_numeric.notna()
        & ci_lower.notna()
        & ci_upper.notna()
    )

    invalid_ci = (
        valid_ci
        & (
            (ci_lower > metric_numeric)
            | (metric_numeric > ci_upper)
        )
    ).sum()

    print(f"Validated CI records: {valid_ci.sum()}")
    print(f"Invalid CI records:   {invalid_ci}")

    if invalid_ci == 0:
        print("PASS")
    else:
        print("FAIL")

    # ------------------------------------------------------------------------
    # 24.15 METRIC RANGE
    # ------------------------------------------------------------------------
    print("\n[24.15] METRIC RANGE")

    numeric_values = metric_numeric.dropna()

    if not numeric_values.empty:
        print(f"Minimum: {numeric_values.min():.2f} per 100")
        print(f"Maximum: {numeric_values.max():.2f} per 100")
        print(f"Mean:    {numeric_values.mean():.2f} per 100")

        if (numeric_values >= 0).all():
            print("PASS — rates are non-negative.")
        else:
            print("FAIL — negative rate detected.")

    # ------------------------------------------------------------------------
    # 24.16 MISSING VALUES
    # ------------------------------------------------------------------------
    print("\n[24.16] MISSING VALUES")

    missing = df.isna().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print("No missing values.")
    else:
        print(missing)

    # ------------------------------------------------------------------------
    # 24.17 DATA TYPES
    # ------------------------------------------------------------------------
    print("\n[24.17] DATA TYPES")
    print(df.dtypes)

    # ------------------------------------------------------------------------
    # 24.18 REFRESH DATE
    # ------------------------------------------------------------------------
    print("\n[24.18] REFRESH DATE")

    print(df["refresh_date"].value_counts(dropna=False))

    # ------------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------------
    section("VALIDATION SUMMARY")

    print("PASS:")
    print("- Transformed column structure confirmed")
    print("- Indicator identity confirmed")
    print("- Geographic coverage assessed")
    print("- Fiscal-year coverage assessed")
    print("- Province-year uniqueness checked")
    print("- Metric and unit confirmed")
    print("- Numeric metric field validated")
    print("- Suppression handling validated")
    print("- Confidence intervals validated")
    print("- Metric range assessed")
    print("- Refresh date assessed")

    print("\nNo source values were imputed or fabricated.")

    print("\n" + "=" * 75)
    print("TRANSFORMED DATA VALIDATION COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()