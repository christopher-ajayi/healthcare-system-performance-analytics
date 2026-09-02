from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "outcomes"
    / "30_day_hospital_readmission_transformed.csv"
)


def main():

    print("=" * 75)
    print("CIHI — 30-DAY HOSPITAL READMISSION")
    print("TRANSFORMED DATA INSPECTION")
    print("=" * 75)

    print("\n[23.1] LOAD TRANSFORMED DATA")
    print(f"Input: {INPUT_FILE}")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"File not found:\n{INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # ------------------------------------------------------------------
    # COLUMN STRUCTURE
    # ------------------------------------------------------------------

    print("\n[23.2] COLUMN STRUCTURE")

    for i, column in enumerate(df.columns, start=1):
        print(f"{i:2}. {column}")

    # ------------------------------------------------------------------
    # INDICATOR
    # ------------------------------------------------------------------

    print("\n[23.3] INDICATOR")
    print(df["indicator"].value_counts(dropna=False))

    # ------------------------------------------------------------------
    # GEOGRAPHIC COVERAGE
    # ------------------------------------------------------------------

    print("\n[23.4] GEOGRAPHIC COVERAGE")

    print(
        df["province_territory"]
        .value_counts(dropna=False)
        .sort_index()
    )

    print(
        f"\nProvinces/territories: "
        f"{df['province_territory'].nunique()}"
    )

    # ------------------------------------------------------------------
    # TIME COVERAGE
    # ------------------------------------------------------------------

    print("\n[23.5] TIME COVERAGE")

    print(
        df["fiscal_year"]
        .value_counts(dropna=False)
        .sort_index()
    )

    print(
        f"\nFiscal years: "
        f"{df['fiscal_year'].nunique()}"
    )

    # ------------------------------------------------------------------
    # METRIC
    # ------------------------------------------------------------------

    print("\n[23.6] METRIC")
    print(df["metric"].value_counts(dropna=False))

    # ------------------------------------------------------------------
    # UNIT
    # ------------------------------------------------------------------

    print("\n[23.7] UNIT OF MEASURE")
    print(df["unit_of_measure"].value_counts(dropna=False))

    # ------------------------------------------------------------------
    # METRIC VALUES
    # ------------------------------------------------------------------

    print("\n[23.8] METRIC VALUES")

    numeric_count = df["metric_value_numeric"].notna().sum()
    non_numeric_count = df["metric_value_numeric"].isna().sum()

    print(f"Numeric observations:     {numeric_count}")
    print(f"Non-numeric observations: {non_numeric_count}")

    if non_numeric_count > 0:
        print("\nNon-numeric source values:")
        print(
            df.loc[
                df["metric_value_numeric"].isna(),
                "metric_value"
            ].value_counts(dropna=False)
        )

    # ------------------------------------------------------------------
    # SUPPRESSION
    # ------------------------------------------------------------------

    print("\n[23.9] SUPPRESSION")

    print(
        df["suppressed"]
        .value_counts(dropna=False)
    )

    # ------------------------------------------------------------------
    # CONFIDENCE INTERVALS
    # ------------------------------------------------------------------

    print("\n[23.10] CONFIDENCE INTERVALS")

    for column in ["ci_lower", "ci_upper"]:

        numeric = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        print(
            f"{column}: "
            f"{numeric.notna().sum()} numeric / "
            f"{numeric.isna().sum()} non-numeric or missing"
        )

    # ------------------------------------------------------------------
    # DUPLICATES
    # ------------------------------------------------------------------

    print("\n[23.11] DUPLICATES")

    exact_duplicates = df.duplicated().sum()

    print(
        f"Exact duplicate rows: "
        f"{exact_duplicates}"
    )

    key_duplicates = df.duplicated(
        subset=["province_territory", "fiscal_year"]
    ).sum()

    print(
        f"Province-year duplicate observations: "
        f"{key_duplicates}"
    )

    # ------------------------------------------------------------------
    # NULLS
    # ------------------------------------------------------------------

    print("\n[23.12] MISSING VALUES")

    missing = df.isna().sum()

    print(
        missing[missing > 0]
        .sort_values(ascending=False)
    )

    # ------------------------------------------------------------------
    # RANGE
    # ------------------------------------------------------------------

    print("\n[23.13] METRIC RANGE")

    numeric_values = df["metric_value_numeric"].dropna()

    if not numeric_values.empty:

        print(f"Minimum: {numeric_values.min()}")
        print(f"Maximum: {numeric_values.max()}")
        print(f"Mean:    {numeric_values.mean():.2f}")

    # ------------------------------------------------------------------
    # DATA TYPES
    # ------------------------------------------------------------------

    print("\n[23.14] DATA TYPES")
    print(df.dtypes)

    # ------------------------------------------------------------------
    # SAMPLE
    # ------------------------------------------------------------------

    print("\n[23.15] FIRST 10 RECORDS")
    print(
        df.head(10)
        .to_string(index=False)
    )

    print("\n" + "=" * 75)
    print("INSPECTION COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()