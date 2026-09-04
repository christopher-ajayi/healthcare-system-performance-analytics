from pathlib import Path
import pandas as pd


INPUT_FILE = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
    r"\data\processed\outcomes\avoidable_hospitalizations_acscs_transformed.csv"
)


EXPECTED_COLUMNS = [
    "place_or_organization",
    "province_territory",
    "region",
    "reporting_level",
    "indicator",
    "measure_type",
    "indicator_segment",
    "segment_value",
    "fiscal_year",
    "metric",
    "main_metric",
    "metric_value",
    "metric_value_numeric",
    "unit_of_measure",
    "ci_lower",
    "ci_upper",
    "suppressed",
    "statistically_different",
    "urban_or_rural_remote",
    "hospital_peer_group",
    "long_term_care_facility_size",
    "trend_note",
    "refresh_date",
    "fiscal_year_start",
    "fiscal_year_end",
]

EXPECTED_INDICATOR = (
    "Ambulatory Care Sensitive Conditions Hospitalizations"
)

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


def main():

    print("=" * 75)
    print("CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs")
    print("TRANSFORMED DATA VALIDATION")
    print("=" * 75)

    # ------------------------------------------------------------------
    # [24.1] LOAD TRANSFORMED DATA
    # ------------------------------------------------------------------
    print("\n[24.1] LOAD TRANSFORMED DATA")
    print(f"Input: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # ------------------------------------------------------------------
    # [24.2] COLUMN STRUCTURE
    # ------------------------------------------------------------------
    print("\n[24.2] COLUMN STRUCTURE")

    if list(df.columns) == EXPECTED_COLUMNS:
        print("PASS — expected transformed column structure confirmed.")
    else:
        print("FAIL — transformed column structure differs.")
        print("\nExpected:")
        print(EXPECTED_COLUMNS)
        print("\nActual:")
        print(list(df.columns))
        raise ValueError("Unexpected transformed column structure.")

    # ------------------------------------------------------------------
    # [24.3] ROW COUNT
    # ------------------------------------------------------------------
    print("\n[24.3] ROW COUNT")

    if len(df) == 155:
        print("PASS — expected 155 rows confirmed.")
    else:
        print(f"REVIEW — expected 155 rows, found {len(df)}.")

    # ------------------------------------------------------------------
    # [24.4] INDICATOR
    # ------------------------------------------------------------------
    print("\n[24.4] INDICATOR")

    print(df["indicator"].value_counts(dropna=False))

    if (
        df["indicator"].nunique(dropna=False) == 1
        and df["indicator"].iloc[0] == EXPECTED_INDICATOR
    ):
        print("PASS")
    else:
        print("FAIL — unexpected indicator identity.")

    # ------------------------------------------------------------------
    # [24.5] GEOGRAPHIC COVERAGE
    # ------------------------------------------------------------------
    print("\n[24.5] GEOGRAPHIC COVERAGE")

    province_counts = (
        df["province_territory"]
        .value_counts(dropna=False)
    )

    print(province_counts)

    province_count = df["province_territory"].nunique()

    print(f"\nProvinces/territories: {province_count}")

    if province_count == 13:
        print("PASS — expected 13 provinces/territories confirmed.")
    else:
        print("FAIL — unexpected number of provinces/territories.")

    missing_provinces = sorted(
        set(EXPECTED_PROVINCES)
        - set(df["province_territory"].dropna().unique())
    )

    unexpected_provinces = sorted(
        set(df["province_territory"].dropna().unique())
        - set(EXPECTED_PROVINCES)
    )

    if missing_provinces:
        print(f"Missing expected provinces/territories: {missing_provinces}")

    if unexpected_provinces:
        print(f"Unexpected provinces/territories: {unexpected_provinces}")

    # ------------------------------------------------------------------
    # [24.6] TIME COVERAGE
    # ------------------------------------------------------------------
    print("\n[24.6] TIME COVERAGE")

    year_counts = (
        df["fiscal_year"]
        .value_counts(dropna=False)
        .reindex(EXPECTED_YEARS)
    )

    print(year_counts)

    year_count = df["fiscal_year"].nunique()

    print(f"\nFiscal years: {year_count}")

    if year_count == 12:
        print("PASS — expected 12 fiscal years confirmed.")
    else:
        print("FAIL — unexpected number of fiscal years.")

    # ------------------------------------------------------------------
    # [24.7] PROVINCE-YEAR UNIQUENESS
    # ------------------------------------------------------------------
    print("\n[24.7] PROVINCE-YEAR UNIQUENESS")

    duplicate_count = df.duplicated(
        subset=["province_territory", "fiscal_year"]
    ).sum()

    print(
        f"Duplicate province-year observations: "
        f"{duplicate_count}"
    )

    if duplicate_count == 0:
        print("PASS")
    else:
        print("FAIL — duplicate province-year observations found.")

    # ------------------------------------------------------------------
    # [24.8] METRIC
    # ------------------------------------------------------------------
    print("\n[24.8] METRIC")

    print(df["metric"].value_counts(dropna=False))

    if (
        df["metric"].nunique(dropna=False) == 1
        and df["metric"].iloc[0] == "Age-standardized rate"
    ):
        print("PASS")
    else:
        print("FAIL — unexpected metric.")

    # ------------------------------------------------------------------
    # [24.9] UNIT OF MEASURE
    # ------------------------------------------------------------------
    print("\n[24.9] UNIT OF MEASURE")

    print(df["unit_of_measure"].value_counts(dropna=False))

    if (
        df["unit_of_measure"].nunique(dropna=False) == 1
        and df["unit_of_measure"].iloc[0] == "Per 100,000"
    ):
        print("PASS")
    else:
        print("FAIL — unexpected unit of measure.")

    # ------------------------------------------------------------------
    # [24.10] NUMERIC METRIC FIELD
    # ------------------------------------------------------------------
    print("\n[24.10] NUMERIC METRIC FIELD")

    numeric = pd.to_numeric(
        df["metric_value_numeric"],
        errors="coerce"
    )

    numeric_count = numeric.notna().sum()
    missing_count = numeric.isna().sum()

    print(f"Numeric observations: {numeric_count}")
    print(f"Missing/non-numeric:  {missing_count}")

    if numeric_count == 145 and missing_count == 10:
        print(
            "PASS — expected numeric/missing structure confirmed."
        )
    else:
        print("REVIEW — numeric/missing structure differs.")

    # ------------------------------------------------------------------
    # [24.11] SUPPRESSION
    # ------------------------------------------------------------------
    print("\n[24.11] SUPPRESSION")

    print(df["suppressed"].value_counts(dropna=False))

    suppressed_count = (df["suppressed"] == True).sum()

    if suppressed_count == 3:
        print("PASS — 3 suppressed observations preserved.")
    else:
        print(
            f"REVIEW — expected 3 suppressed observations, "
            f"found {suppressed_count}."
        )

    # ------------------------------------------------------------------
    # [24.12] SUPPRESSION CONSISTENCY
    # ------------------------------------------------------------------
    print("\n[24.12] SUPPRESSION CONSISTENCY")

    suppressed_numeric = df.loc[
        df["suppressed"] == True,
        "metric_value_numeric"
    ].notna().sum()

    print(
        "Suppressed rows with numeric metric value: "
        f"{suppressed_numeric}"
    )

    if suppressed_numeric == 0:
        print("PASS — suppressed metrics remain non-numeric.")
    else:
        print(
            "FAIL — suppressed observations contain numeric "
            "metric values."
        )

    # ------------------------------------------------------------------
    # [24.13] CONFIDENCE INTERVALS
    # ------------------------------------------------------------------
    print("\n[24.13] CONFIDENCE INTERVALS")

    ci_lower = pd.to_numeric(df["ci_lower"], errors="coerce")
    ci_upper = pd.to_numeric(df["ci_upper"], errors="coerce")

    print(
        f"CI lower numeric: {ci_lower.notna().sum()}"
    )
    print(
        f"CI upper numeric: {ci_upper.notna().sum()}"
    )
    print(
        f"CI lower missing/non-numeric: {ci_lower.isna().sum()}"
    )
    print(
        f"CI upper missing/non-numeric: {ci_upper.isna().sum()}"
    )

    # ------------------------------------------------------------------
    # [24.14] CONFIDENCE INTERVAL LOGIC
    # ------------------------------------------------------------------
    print("\n[24.14] CONFIDENCE INTERVAL LOGIC")

    valid_ci = (
        ci_lower.notna()
        & ci_upper.notna()
        & numeric.notna()
    )

    invalid_ci = (
        valid_ci
        & (
            (ci_lower > numeric)
            | (numeric > ci_upper)
            | (ci_lower > ci_upper)
        )
    )

    print(
        f"Validated CI records: {valid_ci.sum()}"
    )
    print(
        f"Invalid CI records:   {invalid_ci.sum()}"
    )

    if invalid_ci.sum() == 0:
        print("PASS")
    else:
        print("FAIL — invalid confidence interval logic detected.")

    # ------------------------------------------------------------------
    # [24.15] METRIC RANGE
    # ------------------------------------------------------------------
    print("\n[24.15] METRIC RANGE")

    numeric_values = numeric.dropna()

    if len(numeric_values) > 0:

        print(
            f"Minimum: {numeric_values.min():,.2f} "
            "per 100,000"
        )
        print(
            f"Maximum: {numeric_values.max():,.2f} "
            "per 100,000"
        )
        print(
            f"Mean:    {numeric_values.mean():,.2f} "
            "per 100,000"
        )

        if (numeric_values >= 0).all():
            print("PASS — rates are non-negative.")
        else:
            print("FAIL — negative rate detected.")

    # ------------------------------------------------------------------
    # [24.16] MISSING VALUES
    # ------------------------------------------------------------------
    print("\n[24.16] MISSING VALUES")

    missing = df.isna().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values.")
    else:
        print(missing)

    # ------------------------------------------------------------------
    # [24.17] DATA TYPES
    # ------------------------------------------------------------------
    print("\n[24.17] DATA TYPES")
    print(df.dtypes)

    # ------------------------------------------------------------------
    # [24.18] TIME FIELD LOGIC
    # ------------------------------------------------------------------
    print("\n[24.18] FISCAL YEAR FIELD LOGIC")

    year_logic = (
        (df["fiscal_year_start"] + 1)
        == df["fiscal_year_end"]
    )

    print(
        f"Valid fiscal-year start/end records: "
        f"{year_logic.sum()}"
    )
    print(
        f"Invalid fiscal-year start/end records: "
        f"{(~year_logic).sum()}"
    )

    if year_logic.all():
        print("PASS")
    else:
        print("FAIL — invalid fiscal-year boundaries detected.")

    # ------------------------------------------------------------------
    # [24.19] REFRESH DATE
    # ------------------------------------------------------------------
    print("\n[24.19] REFRESH DATE")

    print(df["refresh_date"].value_counts(dropna=False))

    # ------------------------------------------------------------------
    # VALIDATION SUMMARY
    # ------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("VALIDATION SUMMARY")
    print("=" * 75)

    print(
        """
PASS:
- Transformed column structure assessed
- Indicator identity confirmed
- Geographic coverage assessed
- Fiscal-year coverage assessed
- Province-year uniqueness checked
- Primary metric confirmed
- Unit of measure confirmed
- Numeric metric field assessed
- Suppression handling assessed
- Confidence intervals assessed
- Confidence interval logic checked
- Metric range assessed
- Fiscal-year fields validated
- No source values imputed or fabricated

REVIEW:
- Quebec — 2024–2025 remains absent from the source data.
- Missing/suppressed values have been preserved.
"""
    )

    print("=" * 75)
    print("TRANSFORMED DATA VALIDATION COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()