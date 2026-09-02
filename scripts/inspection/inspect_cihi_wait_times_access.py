from pathlib import Path
import pandas as pd


# =============================================================================
# CONFIGURATION
# =============================================================================

INPUT_FILE = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
    r"\data\processed\access\cihi_wait_times_transformed.csv"
)


# =============================================================================
# HELPERS
# =============================================================================

def section(title):
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


# =============================================================================
# LOAD
# =============================================================================

print("=" * 78)
print("CIHI WAIT TIMES — PROCESSED ACCESS INSPECTION")
print("=" * 78)

print("\nInput file:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

print(f"\nShape: {df.shape}")


# =============================================================================
# 1. COLUMNS
# =============================================================================

section("1. COLUMNS")

for column in df.columns:
    print(f"  - {column}")


# =============================================================================
# 2. INDICATORS
# =============================================================================

section("2. INDICATORS")

if "indicator" in df.columns:
    print(df["indicator"].value_counts(dropna=False))
else:
    print("indicator column not found.")


# =============================================================================
# 3. METRICS
# =============================================================================

section("3. METRICS")

if "metric" in df.columns:
    print(df["metric"].value_counts(dropna=False))
else:
    print("metric column not found.")


# =============================================================================
# 4. MEASURE TYPES
# =============================================================================

section("4. MEASURE TYPES")

if "measure_type" in df.columns:
    print(df["measure_type"].value_counts(dropna=False))
else:
    print("measure_type column not found.")


# =============================================================================
# 5. INDICATOR SEGMENTS
# =============================================================================

section("5. INDICATOR SEGMENTS")

if "indicator_segment" in df.columns:
    print(df["indicator_segment"].value_counts(dropna=False))

if "segment_value" in df.columns:
    print("\nSegment values:")
    print(df["segment_value"].value_counts(dropna=False).head(100))


# =============================================================================
# 6. REPORTING LEVELS
# =============================================================================

section("6. REPORTING LEVELS")

if "reporting_level" in df.columns:
    print(df["reporting_level"].value_counts(dropna=False))


# =============================================================================
# 7. GEOGRAPHIC COVERAGE
# =============================================================================

section("7. GEOGRAPHIC COVERAGE")

for column in [
    "province",
    "region",
    "place_or_organization",
]:
    if column in df.columns:
        print(f"\n{column}:")
        print(f"  Unique values: {df[column].nunique(dropna=True)}")
        print(df[column].dropna().unique()[:100])


# =============================================================================
# 8. TIME COVERAGE
# =============================================================================

section("8. TIME COVERAGE")

if "reporting_year" in df.columns:
    years = pd.to_numeric(
        df["reporting_year"],
        errors="coerce"
    )

    print("Reporting years:")
    print(sorted(years.dropna().unique()))

    print("\nRecords by year:")
    print(years.value_counts().sort_index())

if "time_scale" in df.columns:
    print("\nTime scale:")
    print(df["time_scale"].value_counts(dropna=False))

if "time_frame" in df.columns:
    print("\nTime frame:")
    print(df["time_frame"].value_counts(dropna=False).head(50))


# =============================================================================
# 9. RESULT AVAILABILITY
# =============================================================================

section("9. RESULT AVAILABILITY")

for column in [
    "indicator_result",
    "indicator_result_available",
    "metric_value_raw",
]:
    if column in df.columns:
        print(f"\n{column}:")
        print(f"  Non-null: {df[column].notna().sum()}")
        print(f"  Missing:  {df[column].isna().sum()}")


# =============================================================================
# 10. BENCHMARK INFORMATION
# =============================================================================

section("10. BENCHMARK INFORMATION")

for column in [
    "benchmark_pct",
    "benchmark_applicable",
]:
    if column in df.columns:
        print(f"\n{column}:")
        print(df[column].value_counts(dropna=False).head(50))


# =============================================================================
# 11. UNITS
# =============================================================================

section("11. UNITS OF MEASUREMENT")

if "unit_of_measure" in df.columns:
    print(df["unit_of_measure"].value_counts(dropna=False))


# =============================================================================
# 12. NUMERIC RESULT SUMMARY
# =============================================================================

section("12. NUMERIC RESULT SUMMARY")

if "indicator_result" in df.columns:

    numeric_result = pd.to_numeric(
        df["indicator_result"],
        errors="coerce"
    )

    print(numeric_result.describe())


# =============================================================================
# 13. UNIQUE INDICATOR / METRIC COMBINATIONS
# =============================================================================

section("13. INDICATOR / METRIC COMBINATIONS")

combination_columns = [
    c for c in [
        "indicator",
        "metric",
        "measure_type",
        "indicator_segment",
    ]
    if c in df.columns
]

if combination_columns:
    combinations = (
        df[combination_columns]
        .drop_duplicates()
        .sort_values(combination_columns)
    )

    print(combinations.to_string(index=False))


# =============================================================================
# 14. INDICATOR / METRIC AVAILABILITY
# =============================================================================

section("14. RESULT AVAILABILITY BY METRIC")

if all(
    c in df.columns
    for c in ["metric", "indicator_result"]
):

    temp = df.copy()

    temp["result_numeric"] = pd.to_numeric(
        temp["indicator_result"],
        errors="coerce"
    )

    summary = (
        temp.groupby("metric", dropna=False)
        .agg(
            records=("metric", "size"),
            available_results=("result_numeric", "count"),
        )
    )

    summary["unavailable_results"] = (
        summary["records"]
        - summary["available_results"]
    )

    print(summary)


# =============================================================================
# 15. ACCESS DATASET SUMMARY FOR OUTCOMES DECISION
# =============================================================================

section("15. ACCESS DATASET — OUTCOMES DECISION SUMMARY")

print(
    """
The purpose of this section is to identify what the Access dataset
already measures so that Outcomes indicators are not duplicated.

Review:

  1. Indicators
  2. Metrics
  3. Measure types
  4. Benchmark measures
  5. Geographic levels
  6. Time coverage
  7. Available numeric results

The next Outcomes indicator should add a distinct dimension of
health-system performance rather than simply duplicate an existing
Access wait-time measure.
"""
)


# =============================================================================
# COMPLETE
# =============================================================================

print("\n" + "=" * 78)
print("ACCESS WAIT-TIME INSPECTION COMPLETE")
print("=" * 78P