from pathlib import Path
import pandas as pd


# ============================================================================
# CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs
# RAW DATA INSPECTION
# ============================================================================


# ============================================================================
# [1] INITIALIZE
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "avoidable_hospitalizations_acscs_raw.csv"
)


# ============================================================================
# [2] LOAD RAW DATA
# ============================================================================

def main():

    print("=" * 75)
    print("CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs")
    print("RAW DATA INSPECTION")
    print("=" * 75)

    print("\n[2] LOAD RAW DATA")
    print(f"\nInput:")
    print(INPUT_FILE)

    df = pd.read_csv(
        INPUT_FILE,
        dtype=str
    )


    # =========================================================================
    # [3] DATASET DIMENSIONS
    # =========================================================================

    print("\n[3] DATASET DIMENSIONS")

    print("\nShape:")
    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns):,}")


    # =========================================================================
    # [4] COLUMN STRUCTURE
    # =========================================================================

    print("\n[4] COLUMN STRUCTURE")

    print("\nCOLUMNS")

    for i, column in enumerate(df.columns, start=1):
        print(f"{i:2}. {column}")


    # =========================================================================
    # [5] INDICATOR
    # =========================================================================

    print("\n[5] INDICATOR")

    print("\nIndicator")

    print(
        df["Indicator"]
        .value_counts(dropna=False)
        .to_string()
    )


    # =========================================================================
    # [6] MEASURE TYPE
    # =========================================================================

    print("\n[6] MEASURE TYPE")

    print("\nMeasure type")

    print(
        df["Measure type"]
        .value_counts(dropna=False)
        .to_string()
    )


    # =========================================================================
    # [7] REPORTING LEVEL
    # =========================================================================

    print("\n[7] REPORTING LEVEL")

    print("\nReporting level")

    print(
        df["Reporting level"]
        .value_counts(dropna=False)
        .to_string()
    )


    # =========================================================================
    # [8] GEOGRAPHIC COVERAGE
    # =========================================================================

    print("\n[8] GEOGRAPHIC COVERAGE")

    print("\nProvince / territory")

    print(
        df["Province/territory"]
        .value_counts(dropna=False)
        .to_string()
    )


    # =========================================================================
    # [9] TIME SCALE
    # =========================================================================

    print("\n[9] TIME SCALE")

    print("\nTime scale")

    print(
        df["Time scale"]
        .value_counts(dropna=False)
        .to_string()
    )


    # =========================================================================
    # [10] TIME FRAME
    # =========================================================================

    print("\n[10] TIME FRAME")

    print("\nTime frame")

    print(
        df["Time frame"]
        .value_counts(dropna=False)
        .sort_index()
        .to_string()
    )


    # =========================================================================
    # [11] METRIC
    # =========================================================================

    print("\n[11] METRIC")

    print("\nMetric")

    print(
        df["Metric"]
        .value_counts(dropna=False)
        .to_string()
    )


    # =========================================================================
    # [12] MAIN METRIC
    # =========================================================================

    print("\n[12] MAIN METRIC")

    print("\nMain metric")

    print(
        df["Main metric"]
        .value_counts(dropna=False)
        .to_string()
    )


    # =========================================================================
    # [13] UNIT OF MEASURE
    # =========================================================================

    print("\n[13] UNIT OF MEASURE")

    print("\nUnit of measure")

    print(
        df["Unit of measure"]
        .value_counts(dropna=False)
        .to_string()
    )


    # =========================================================================
    # [14] MISSING VALUES
    # =========================================================================

    print("\n[14] MISSING VALUES")

    missing = (
        df.isna()
        .sum()
        .sort_values(ascending=False)
    )

    missing_pct = (
        missing
        .div(len(df))
        .mul(100)
        .round(2)
    )

    missing_summary = pd.DataFrame({
        "missing_count": missing,
        "missing_pct": missing_pct
    })

    print(
        missing_summary
        .to_string()
    )


    # =========================================================================
    # [15] DUPLICATES
    # =========================================================================

    print("\n[15] DUPLICATES")

    exact_duplicates = df.duplicated().sum()

    print(f"Exact duplicate rows: {exact_duplicates:,}")


    # =========================================================================
    # [16] DATA TYPES
    # =========================================================================

    print("\n[16] DATA TYPES")

    print(
        df.dtypes
        .to_string()
    )


    # =========================================================================
    # [17] METRIC VALUE
    # =========================================================================

    print("\n[17] METRIC VALUE")

    print("\nMetric value")

    print(
        df["Metric value"]
        .value_counts(dropna=False)
        .head(20)
        .to_string()
    )

    print(
        f"\nUnique metric values: "
        f"{df['Metric value'].nunique(dropna=False):,}"
    )


    # =========================================================================
    # [18] CONFIDENCE INTERVALS
    # =========================================================================

    print("\n[18] CONFIDENCE INTERVALS")

    print("\nConfidence interval lower limit")

    print(
        df["Confidence interval lower limit"]
        .value_counts(dropna=False)
        .head(15)
        .to_string()
    )

    print("\nConfidence interval upper limit")

    print(
        df["Confidence interval upper limit"]
        .value_counts(dropna=False)
        .head(15)
        .to_string()
    )


    # =========================================================================
    # [19] FIRST 10 RECORDS
    # =========================================================================

    print("\n[19] FIRST 10 RECORDS")

    print(
        df.head(10)
        .to_string(index=False)
    )


    # =========================================================================
    # [20] INSPECTION COMPLETE
    # =========================================================================

    print("\n" + "=" * 75)
    print("INSPECTION COMPLETE")
    print("=" * 75)


# ============================================================================
# [21] RUN
# ============================================================================

if __name__ == "__main__":
    main()