from pathlib import Path
import pandas as pd


# ============================================================
# CIHI — 30-DAY HOSPITAL READMISSION
# RAW DATA INSPECTION
# ============================================================


# ============================================================
# 1. CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "30_day_hospital_readmission_raw.csv"
)


# ============================================================
# 2. LOAD DATA
# ============================================================

def load_data():

    print("=" * 75)
    print("CIHI — 30-DAY HOSPITAL READMISSION")
    print("RAW DATA INSPECTION")
    print("=" * 75)

    print("\nInput:")
    print(INPUT_FILE)

    df = pd.read_csv(
        INPUT_FILE,
        dtype=str
    )

    print("\nShape:")
    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    return df


# ============================================================
# 3. COLUMN INSPECTION
# ============================================================

def inspect_columns(df):

    print("\n" + "-" * 75)
    print("COLUMNS")
    print("-" * 75)

    for i, column in enumerate(df.columns, start=1):
        print(f"{i:2}. {column}")


# ============================================================
# 4. INDICATOR INSPECTION
# ============================================================

def inspect_indicator(df):

    print("\n" + "-" * 75)
    print("INDICATOR")
    print("-" * 75)

    print(
        df["Indicator"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 5. MEASURE TYPE INSPECTION
# ============================================================

def inspect_measure_type(df):

    print("\n" + "-" * 75)
    print("MEASURE TYPE")
    print("-" * 75)

    print(
        df["Measure type"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 6. REPORTING LEVEL INSPECTION
# ============================================================

def inspect_reporting_level(df):

    print("\n" + "-" * 75)
    print("REPORTING LEVEL")
    print("-" * 75)

    print(
        df["Reporting level"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 7. GEOGRAPHIC COVERAGE
# ============================================================

def inspect_geography(df):

    print("\n" + "-" * 75)
    print("PROVINCE / TERRITORY")
    print("-" * 75)

    print(
        df["Province/territory"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 8. TIME SCALE
# ============================================================

def inspect_time_scale(df):

    print("\n" + "-" * 75)
    print("TIME SCALE")
    print("-" * 75)

    print(
        df["Time scale"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 9. TIME FRAME
# ============================================================

def inspect_time_frame(df):

    print("\n" + "-" * 75)
    print("TIME FRAME")
    print("-" * 75)

    print(
        df["Time frame"]
        .value_counts(dropna=False)
        .sort_index()
        .to_string()
    )


# ============================================================
# 10. METRIC
# ============================================================

def inspect_metric(df):

    print("\n" + "-" * 75)
    print("METRIC")
    print("-" * 75)

    print(
        df["Metric"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 11. MAIN METRIC
# ============================================================

def inspect_main_metric(df):

    print("\n" + "-" * 75)
    print("MAIN METRIC")
    print("-" * 75)

    print(
        df["Main metric"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 12. UNIT OF MEASURE
# ============================================================

def inspect_unit(df):

    print("\n" + "-" * 75)
    print("UNIT OF MEASURE")
    print("-" * 75)

    print(
        df["Unit of measure"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 13. MISSING VALUES
# ============================================================

def inspect_missing_values(df):

    print("\n" + "-" * 75)
    print("MISSING VALUES")
    print("-" * 75)

    missing = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_pct": (
            df.isna().mean() * 100
        ).round(2)
    })

    missing = (
        missing
        .sort_values(
            "missing_count",
            ascending=False
        )
    )

    print(missing.to_string())


# ============================================================
# 14. DUPLICATES
# ============================================================

def inspect_duplicates(df):

    print("\n" + "-" * 75)
    print("DUPLICATES")
    print("-" * 75)

    duplicates = df.duplicated().sum()

    print(
        f"Exact duplicate rows: {duplicates:,}"
    )


# ============================================================
# 15. DATA TYPES
# ============================================================

def inspect_data_types(df):

    print("\n" + "-" * 75)
    print("DATA TYPES")
    print("-" * 75)

    print(
        df.dtypes.to_string()
    )


# ============================================================
# 16. METRIC VALUE
# ============================================================

def inspect_metric_value(df):

    print("\n" + "-" * 75)
    print("METRIC VALUE")
    print("-" * 75)

    print(
        df["Metric value"]
        .value_counts(dropna=False)
        .head(20)
        .to_string()
    )

    print(
        f"\nUnique metric values: "
        f"{df['Metric value'].nunique(dropna=True):,}"
    )


# ============================================================
# 17. CONFIDENCE INTERVALS
# ============================================================

def inspect_confidence_intervals(df):

    print("\n" + "-" * 75)
    print("CONFIDENCE INTERVALS")
    print("-" * 75)

    for column in [
        "Confidence interval lower limit",
        "Confidence interval upper limit"
    ]:

        print(f"\n{column}")

        print(
            df[column]
            .value_counts(dropna=False)
            .head(15)
            .to_string()
        )


# ============================================================
# 18. FIRST RECORDS
# ============================================================

def inspect_first_records(df):

    print("\n" + "-" * 75)
    print("FIRST 10 RECORDS")
    print("-" * 75)

    print(
        df.head(10).to_string(index=False)
    )


# ============================================================
# 19. COMPLETION
# ============================================================

def main():

    df = load_data()

    inspect_columns(df)
    inspect_indicator(df)
    inspect_measure_type(df)
    inspect_reporting_level(df)
    inspect_geography(df)
    inspect_time_scale(df)
    inspect_time_frame(df)
    inspect_metric(df)
    inspect_main_metric(df)
    inspect_unit(df)
    inspect_missing_values(df)
    inspect_duplicates(df)
    inspect_data_types(df)
    inspect_metric_value(df)
    inspect_confidence_intervals(df)
    inspect_first_records(df)

    print("\n" + "=" * 75)
    print("INSPECTION COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()