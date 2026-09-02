from pathlib import Path
import pandas as pd


INPUT_FILE = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
    r"\data\processed\outcomes\avoidable_hospitalizations_acscs_transformed.csv"
)


def main():

    print("=" * 75)
    print("CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs")
    print("TRANSFORMED DATA INSPECTION")
    print("=" * 75)

    # ------------------------------------------------------------------
    # [23.1] LOAD TRANSFORMED DATA
    # ------------------------------------------------------------------
    print("\n[23.1] LOAD TRANSFORMED DATA")
    print(f"Input: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # ------------------------------------------------------------------
    # [23.2] COLUMN STRUCTURE
    # ------------------------------------------------------------------
    print("\n[23.2] COLUMN STRUCTURE")

    for i, col in enumerate(df.columns, start=1):
        print(f"{i:2}. {col}")

    # ------------------------------------------------------------------
    # [23.3] INDICATOR
    # ------------------------------------------------------------------
    print("\n[23.3] INDICATOR")
    print(df["indicator"].value_counts(dropna=False))

    # ------------------------------------------------------------------
    # [23.4] GEOGRAPHIC COVERAGE
    # ------------------------------------------------------------------
    print("\n[23.4] GEOGRAPHIC COVERAGE")

    print(df["province_territory"].value_counts(dropna=False))

    print(
        f"\nProvinces/territories: "
        f"{df['province_territory'].nunique(dropna=True)}"
    )

    # ------------------------------------------------------------------
    # [23.5] TIME COVERAGE
    # ------------------------------------------------------------------
    print("\n[23.5] TIME COVERAGE")

    print(df["fiscal_year"].value_counts(dropna=False).sort_index())

    print(
        f"\nFiscal years: "
        f"{df['fiscal_year'].nunique(dropna=True)}"
    )

    # ------------------------------------------------------------------
    # [23.6] METRIC
    # ------------------------------------------------------------------
    print("\n[23.6] METRIC")
    print(df["metric"].value_counts(dropna=False))

    # ------------------------------------------------------------------
    # [23.7] UNIT OF MEASURE
    # ------------------------------------------------------------------
    print("\n[23.7] UNIT OF MEASURE")
    print(df["unit_of_measure"].value_counts(dropna=False))

    # ------------------------------------------------------------------
    # [23.8] METRIC VALUES
    # ------------------------------------------------------------------
    print("\n[23.8] METRIC VALUES")

    numeric = pd.to_numeric(
        df["metric_value_numeric"],
        errors="coerce"
    )

    print(f"Numeric observations:     {numeric.notna().sum():,}")
    print(f"Non-numeric/missing:       {numeric.isna().sum():,}")

    # ------------------------------------------------------------------
    # [23.9] SUPPRESSION
    # ------------------------------------------------------------------
    print("\n[23.9] SUPPRESSION")

    print(df["suppressed"].value_counts(dropna=False))

    # ------------------------------------------------------------------
    # [23.10] CONFIDENCE INTERVALS
    # ------------------------------------------------------------------
    print("\n[23.10] CONFIDENCE INTERVALS")

    ci_lower = pd.to_numeric(df["ci_lower"], errors="coerce")
    ci_upper = pd.to_numeric(df["ci_upper"], errors="coerce")

    print(
        f"ci_lower: "
        f"{ci_lower.notna().sum()} numeric / "
        f"{ci_lower.isna().sum()} missing"
    )

    print(
        f"ci_upper: "
        f"{ci_upper.notna().sum()} numeric / "
        f"{ci_upper.isna().sum()} missing"
    )

    # ------------------------------------------------------------------
    # [23.11] DUPLICATES
    # ------------------------------------------------------------------
    print("\n[23.11] DUPLICATES")

    print(f"Exact duplicate rows: {df.duplicated().sum()}")

    province_year_duplicates = df.duplicated(
        subset=["province_territory", "fiscal_year"],
        keep=False
    ).sum()

    print(
        f"Province-year duplicate observations: "
        f"{province_year_duplicates}"
    )

    # ------------------------------------------------------------------
    # [23.12] MISSING VALUES
    # ------------------------------------------------------------------
    print("\n[23.12] MISSING VALUES")

    missing = df.isna().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values.")
    else:
        print(missing)

    # ------------------------------------------------------------------
    # [23.13] METRIC RANGE
    # ------------------------------------------------------------------
    print("\n[23.13] METRIC RANGE")

    numeric_values = numeric.dropna()

    if len(numeric_values) > 0:
        print(f"Minimum: {numeric_values.min():,.2f}")
        print(f"Maximum: {numeric_values.max():,.2f}")
        print(f"Mean:    {numeric_values.mean():,.2f}")
    else:
        print("No numeric metric values available.")

    # ------------------------------------------------------------------
    # [23.14] DATA TYPES
    # ------------------------------------------------------------------
    print("\n[23.14] DATA TYPES")
    print(df.dtypes)

    # ------------------------------------------------------------------
    # [23.15] FIRST 10 RECORDS
    # ------------------------------------------------------------------
    print("\n[23.15] FIRST 10 RECORDS")
    print(df.head(10).to_string(index=False))

    print("\n" + "=" * 75)
    print("INSPECTION COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()