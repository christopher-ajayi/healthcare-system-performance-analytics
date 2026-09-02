from pathlib import Path
import pandas as pd


# ============================================================
# CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS
# RAW DATA INSPECTION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "hip_fracture_surgery_within_48_hours_raw.csv"
)


def main():

    print("=" * 75)
    print("CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS")
    print("RAW DATA INSPECTION")
    print("=" * 75)

    df = pd.read_csv(INPUT_FILE)

    print(f"\nInput:")
    print(INPUT_FILE)

    print("\nShape:")
    print(f"Rows:    {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]:,}")

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("COLUMNS")
    print("-" * 75)

    for i, column in enumerate(df.columns, start=1):
        print(f"{i:2}. {column}")

    # --------------------------------------------------------
    # Indicator
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("INDICATOR")
    print("-" * 75)

    print(df["Indicator"].value_counts(dropna=False).to_string())

    # --------------------------------------------------------
    # Measure type
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("MEASURE TYPE")
    print("-" * 75)

    print(df["Measure type"].value_counts(dropna=False).to_string())

    # --------------------------------------------------------
    # Reporting level
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("REPORTING LEVEL")
    print("-" * 75)

    print(df["Reporting level"].value_counts(dropna=False).to_string())

    # --------------------------------------------------------
    # Province / territory
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("PROVINCE / TERRITORY")
    print("-" * 75)

    print(
        df["Province/territory"]
        .value_counts(dropna=False)
        .sort_index()
        .to_string()
    )

    # --------------------------------------------------------
    # Time scale / frame
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("TIME SCALE")
    print("-" * 75)

    print(df["Time scale"].value_counts(dropna=False).to_string())

    print("\nTIME FRAME")

    print(
        df["Time frame"]
        .value_counts(dropna=False)
        .sort_index()
        .to_string()
    )

    # --------------------------------------------------------
    # Metric
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("METRIC")
    print("-" * 75)

    print(df["Metric"].value_counts(dropna=False).to_string())

    print("\nMAIN METRIC")

    print(df["Main metric"].value_counts(dropna=False).to_string())

    # --------------------------------------------------------
    # Unit
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("UNIT OF MEASURE")
    print("-" * 75)

    print(df["Unit of measure"].value_counts(dropna=False).to_string())

    # --------------------------------------------------------
    # Segment
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("INDICATOR SEGMENT")
    print("-" * 75)

    print(df["Indicator segment"].value_counts(dropna=False).to_string())

    # --------------------------------------------------------
    # Missingness
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("MISSING VALUES")
    print("-" * 75)

    missing = (
        df.isna()
        .sum()
        .sort_values(ascending=False)
    )

    missing_pct = (
        df.isna()
        .mean()
        .mul(100)
        .sort_values(ascending=False)
    )

    missing_report = pd.DataFrame({
        "missing_count": missing,
        "missing_pct": missing_pct.round(2)
    })

    print(missing_report.to_string())

    # --------------------------------------------------------
    # Duplicate records
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("DUPLICATES")
    print("-" * 75)

    print(
        f"Exact duplicate rows: "
        f"{df.duplicated().sum():,}"
    )

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("DATA TYPES")
    print("-" * 75)

    print(df.dtypes.to_string())

    # --------------------------------------------------------
    # Metric value inspection
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("METRIC VALUE")
    print("-" * 75)

    print(
        df["Metric value"]
        .describe(include="all")
        .to_string()
    )

    # --------------------------------------------------------
    # Confidence intervals
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("CONFIDENCE INTERVALS")
    print("-" * 75)

    ci_columns = [
        "Confidence interval lower limit",
        "Confidence interval upper limit"
    ]

    print(df[ci_columns].describe().to_string())

    # --------------------------------------------------------
    # Sample
    # --------------------------------------------------------

    print("\n" + "-" * 75)
    print("FIRST 10 RECORDS")
    print("-" * 75)

    print(
        df.head(10).to_string(index=False)
    )

    print("\n" + "=" * 75)
    print("INSPECTION COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()