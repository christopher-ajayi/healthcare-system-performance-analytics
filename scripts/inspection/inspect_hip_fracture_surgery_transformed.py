from pathlib import Path
import pandas as pd


# ============================================================================
# CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS
# TRANSFORMED DATA INSPECTION
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


def main():

    print("=" * 74)
    print("CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS")
    print("TRANSFORMED DATA INSPECTION")
    print("=" * 74)

    # ------------------------------------------------------------------------
    # [26.1] LOAD TRANSFORMED DATA
    # ------------------------------------------------------------------------
    print("\n[26.1] LOAD TRANSFORMED DATA")
    print(f"Input: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    # ------------------------------------------------------------------------
    # [26.2] COLUMN STRUCTURE
    # ------------------------------------------------------------------------
    print("\n[26.2] COLUMN STRUCTURE")

    for i, column in enumerate(df.columns, start=1):
        print(f"{i:2}. {column}")

    # ------------------------------------------------------------------------
    # [26.3] INDICATOR
    # ------------------------------------------------------------------------
    print("\n[26.3] INDICATOR")

    if "indicator" in df.columns:
        print(df["indicator"].value_counts(dropna=False))
    else:
        print("indicator column not present.")

    # ------------------------------------------------------------------------
    # [26.4] GEOGRAPHIC COVERAGE
    # ------------------------------------------------------------------------
    print("\n[26.4] GEOGRAPHIC COVERAGE")

    if "province_territory" in df.columns:
        print(
            df["province_territory"]
            .value_counts(dropna=False)
            .sort_index()
        )

        print(
            "\nProvinces/territories:",
            df["province_territory"].nunique(dropna=True)
        )
    else:
        print("province_territory column not present.")

    # ------------------------------------------------------------------------
    # [26.5] TIME COVERAGE
    # ------------------------------------------------------------------------
    print("\n[26.5] TIME COVERAGE")

    if "fiscal_year" in df.columns:
        print(
            df["fiscal_year"]
            .value_counts(dropna=False)
            .sort_index()
        )

        print(
            "\nFiscal years:",
            df["fiscal_year"].nunique(dropna=True)
        )
    else:
        print("fiscal_year column not present.")

    # ------------------------------------------------------------------------
    # [26.6] METRIC
    # ------------------------------------------------------------------------
    print("\n[26.6] METRIC")

    if "metric" in df.columns:
        print(df["metric"].value_counts(dropna=False))
    else:
        print("metric column not present.")

    # ------------------------------------------------------------------------
    # [26.7] UNIT OF MEASURE
    # ------------------------------------------------------------------------
    print("\n[26.7] UNIT OF MEASURE")

    if "unit_of_measure" in df.columns:
        print(df["unit_of_measure"].value_counts(dropna=False))
    else:
        print("unit_of_measure column not present.")

    # ------------------------------------------------------------------------
    # [26.8] METRIC VALUES
    # ------------------------------------------------------------------------
    print("\n[26.8] METRIC VALUES")

    if "metric_value_numeric" in df.columns:

        numeric_count = df["metric_value_numeric"].notna().sum()
        missing_count = df["metric_value_numeric"].isna().sum()

        print(
            f"Numeric observations:     {numeric_count:,}"
        )
        print(
            f"Non-numeric/missing:       {missing_count:,}"
        )

    # ------------------------------------------------------------------------
    # [26.9] SUPPRESSION
    # ------------------------------------------------------------------------
    print("\n[26.9] SUPPRESSION")

    if "suppressed" in df.columns:
        print(
            df["suppressed"]
            .value_counts(dropna=False)
        )

    # ------------------------------------------------------------------------
    # [26.10] CONFIDENCE INTERVALS
    # ------------------------------------------------------------------------
    print("\n[26.10] CONFIDENCE INTERVALS")

    if "ci_lower" in df.columns:
        lower_numeric = pd.to_numeric(
            df["ci_lower"],
            errors="coerce"
        ).notna().sum()

        lower_missing = pd.to_numeric(
            df["ci_lower"],
            errors="coerce"
        ).isna().sum()

        print(
            f"ci_lower: {lower_numeric:,} numeric / "
            f"{lower_missing:,} missing"
        )

    if "ci_upper" in df.columns:
        upper_numeric = pd.to_numeric(
            df["ci_upper"],
            errors="coerce"
        ).notna().sum()

        upper_missing = pd.to_numeric(
            df["ci_upper"],
            errors="coerce"
        ).isna().sum()

        print(
            f"ci_upper: {upper_numeric:,} numeric / "
            f"{upper_missing:,} missing"
        )

    # ------------------------------------------------------------------------
    # [26.11] DUPLICATES
    # ------------------------------------------------------------------------
    print("\n[26.11] DUPLICATES")

    exact_duplicates = df.duplicated().sum()

    print(
        "Exact duplicate rows:",
        exact_duplicates
    )

    if (
        "province_territory" in df.columns
        and "fiscal_year" in df.columns
    ):

        province_year_duplicates = df.duplicated(
            subset=[
                "province_territory",
                "fiscal_year"
            ]
        ).sum()

        print(
            "Province-year duplicate observations:",
            province_year_duplicates
        )

    # ------------------------------------------------------------------------
    # [26.12] MISSING VALUES
    # ------------------------------------------------------------------------
    print("\n[26.12] MISSING VALUES")

    missing = df.isna().sum()

    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values.")
    else:
        print(missing)

    # ------------------------------------------------------------------------
    # [26.13] METRIC RANGE
    # ------------------------------------------------------------------------
    print("\n[26.13] METRIC RANGE")

    if "metric_value_numeric" in df.columns:

        numeric_values = pd.to_numeric(
            df["metric_value_numeric"],
            errors="coerce"
        ).dropna()

        if len(numeric_values) > 0:
            print(
                f"Minimum: {numeric_values.min():.2f}"
            )
            print(
                f"Maximum: {numeric_values.max():.2f}"
            )
            print(
                f"Mean:    {numeric_values.mean():.2f}"
            )
        else:
            print("No numeric metric observations.")

    # ------------------------------------------------------------------------
    # [26.14] DATA TYPES
    # ------------------------------------------------------------------------
    print("\n[26.14] DATA TYPES")

    print(df.dtypes)

    # ------------------------------------------------------------------------
    # [26.15] FIRST 10 RECORDS
    # ------------------------------------------------------------------------
    print("\n[26.15] FIRST 10 RECORDS")

    print(
        df.head(10).to_string(index=False)
    )

    print("\n" + "=" * 74)
    print("INSPECTION COMPLETE")
    print("=" * 74)


if __name__ == "__main__":
    main()