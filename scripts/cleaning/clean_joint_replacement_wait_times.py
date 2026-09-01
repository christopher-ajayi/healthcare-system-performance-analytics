from pathlib import Path
import pandas as pd


# ============================================================================
# CIHI JOINT REPLACEMENT WAIT TIMES — CLEANING
# ============================================================================

PROJECT_ROOT = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
)

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "cihi_indicator_library.xlsx"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "outcomes"
    / "cihi_joint_replacement_wait_times_clean.csv"
)

SHEET_NAME = "Sheet1"
TARGET_INDICATOR = "Joint Replacement Wait Times"


# ============================================================================
# HEADER
# ============================================================================

print("=" * 78)
print("CIHI JOINT REPLACEMENT WAIT TIMES — CLEANING")
print("=" * 78)

print(f"\nInput file:\n{INPUT_FILE}")
print(f"\nSheet: {SHEET_NAME}")
print(f"\nOutput file:\n{OUTPUT_FILE}")


# ============================================================================
# LOAD
# ============================================================================

df = pd.read_excel(
    INPUT_FILE,
    sheet_name=SHEET_NAME,
    dtype=str
)

print(f"\nRaw shape: {df.shape}")


# ============================================================================
# COLUMN VALIDATION
# ============================================================================

required_columns = [
    "Place or organization",
    "Province/territory",
    "Region",
    "Corporation",
    "Reporting level",
    "Indicator",
    "Measure type",
    "Indicator segment",
    "Segment value",
    "Time scale",
    "Time frame",
    "Level 1 breakdown",
    "Level 1 breakdown value",
    "Level 2 breakdown",
    "Level 2 breakdown value",
    "Level 3 breakdown",
    "Level 3 breakdown value",
    "Metric",
    "Main metric",
    "Metric value",
    "Unit of measure",
    "Confidence interval lower limit",
    "Confidence interval upper limit",
    "Statistically different",
    "Performance comparison",
    "Performance trend",
    "Top results",
    "Data coverage",
    "Urban or rural/remote",
    "Hospital peer group",
    "Long-Term Care Facility Size",
    "Trend note",
    "Refresh date",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("\nColumn validation passed.")


# ============================================================================
# REMOVE COMPLETELY EMPTY ROWS
# ============================================================================

before = len(df)

df = df.dropna(how="all").copy()

removed = before - len(df)

print(f"\nCompletely empty rows removed: {removed:,}")


# ============================================================================
# FILTER TARGET INDICATOR
# ============================================================================

df["Indicator"] = df["Indicator"].astype("string").str.strip()

df = df[
    df["Indicator"] == TARGET_INDICATOR
].copy()

if df.empty:
    raise ValueError(
        f"No records found for indicator: {TARGET_INDICATOR}"
    )

print(
    f"\nTarget indicator records: {len(df):,}"
)


# ============================================================================
# STANDARDIZE TEXT FIELDS
# ============================================================================

text_columns = [
    "Place or organization",
    "Province/territory",
    "Region",
    "Corporation",
    "Reporting level",
    "Indicator",
    "Measure type",
    "Indicator segment",
    "Segment value",
    "Time scale",
    "Time frame",
    "Level 1 breakdown",
    "Level 1 breakdown value",
    "Level 2 breakdown",
    "Level 2 breakdown value",
    "Level 3 breakdown",
    "Level 3 breakdown value",
    "Metric",
    "Main metric",
    "Metric value",
    "Unit of measure",
    "Statistically different",
    "Performance comparison",
    "Performance trend",
    "Top results",
    "Data coverage",
    "Urban or rural/remote",
    "Hospital peer group",
    "Long-Term Care Facility Size",
    "Trend note",
]

for column in text_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# ============================================================================
# STANDARDIZE NOT-APPLICABLE VALUES
# ============================================================================

na_markers = {
    "-": pd.NA,
    "": pd.NA,
}

for column in text_columns:
    df[column] = df[column].replace(na_markers)


# ============================================================================
# VALIDATE INDICATOR STRUCTURE
# ============================================================================

if df["Indicator"].nunique() != 1:
    raise ValueError(
        "Multiple indicators detected after filtering."
    )

if df["Indicator"].iloc[0] != TARGET_INDICATOR:
    raise ValueError(
        "Unexpected indicator detected."
    )

print("Indicator validation passed.")


# ============================================================================
# REPORTING LEVEL VALIDATION
# ============================================================================

expected_reporting_levels = {
    "National",
    "Province/territory",
    "Health region",
}

actual_reporting_levels = set(
    df["Reporting level"].dropna().unique()
)

unexpected_levels = (
    actual_reporting_levels
    - expected_reporting_levels
)

if unexpected_levels:
    raise ValueError(
        f"Unexpected reporting levels: {unexpected_levels}"
    )

print("Reporting-level validation passed.")


# ============================================================================
# TIME SCALE VALIDATION
# ============================================================================

expected_time_scale = {"Fiscal year"}

actual_time_scale = set(
    df["Time scale"].dropna().unique()
)

if actual_time_scale != expected_time_scale:
    raise ValueError(
        f"Unexpected time scale: {actual_time_scale}"
    )

print("Time-scale validation passed.")


# ============================================================================
# TIME FRAME VALIDATION
# ============================================================================

df["reporting_year"] = pd.to_numeric(
    df["Time frame"].str.extract(r"(\d{4})")[0],
    errors="coerce"
).astype("Int64")

if df["reporting_year"].isna().any():
    raise ValueError(
        "Unable to derive reporting year from Time frame."
    )

print("Reporting-year validation passed.")
print(
    f"  Minimum year: {df['reporting_year'].min()}"
)
print(
    f"  Maximum year: {df['reporting_year'].max()}"
)


# ============================================================================
# METRIC VALIDATION
# ============================================================================

expected_metrics = {
    "Number of cases",
    "Percentage of cases treated within benchmark",
}

actual_metrics = set(
    df["Metric"].dropna().unique()
)

unexpected_metrics = (
    actual_metrics - expected_metrics
)

if unexpected_metrics:
    raise ValueError(
        f"Unexpected metrics: {unexpected_metrics}"
    )

if actual_metrics != expected_metrics:
    raise ValueError(
        f"Expected both metrics, found: {actual_metrics}"
    )

print("Metric validation passed.")


# ============================================================================
# METRIC / UNIT COMPATIBILITY
# ============================================================================

number_of_cases = df["Metric"] == "Number of cases"

benchmark_percentage = (
    df["Metric"]
    == "Percentage of cases treated within benchmark"
)

if df.loc[number_of_cases, "Unit of measure"].notna().any():
    raise ValueError(
        "Number-of-cases records contain an unexpected unit."
    )

percentage_units = set(
    df.loc[
        benchmark_percentage,
        "Unit of measure"
    ].dropna().unique()
)

if percentage_units != {"Percent"}:
    raise ValueError(
        f"Unexpected benchmark percentage units: "
        f"{percentage_units}"
    )

print("Metric/unit compatibility validation passed.")


# ============================================================================
# INDICATOR SEGMENT VALIDATION
# ============================================================================

if set(df["Indicator segment"].dropna().unique()) != {
    "Not applicable"
}:
    raise ValueError(
        "Unexpected indicator segment values detected."
    )

if set(df["Segment value"].dropna().unique()) != {
    "Not applicable"
}:
    raise ValueError(
        "Unexpected segment values detected."
    )

print("Indicator-segment validation passed.")


# ============================================================================
# LEVEL 2 / LEVEL 3 VALIDATION
# ============================================================================

for column in [
    "Level 2 breakdown",
    "Level 2 breakdown value",
    "Level 3 breakdown",
    "Level 3 breakdown value",
]:
    values = set(df[column].dropna().unique())

    if values != {"Not applicable"}:
        raise ValueError(
            f"Unexpected values in {column}: {values}"
        )

print("Level 2/3 breakdown validation passed.")


# ============================================================================
# METRIC VALUE CLEANING
# ============================================================================

# Preserve "Not available" as missing analytical values.
df["indicator_result_available"] = (
    df["Metric value"].notna()
    & ~df["Metric value"].isin(["Not available"])
)

df["indicator_result"] = pd.to_numeric(
    df["Metric value"].replace(
        {"Not available": pd.NA}
    ),
    errors="coerce"
)


# ============================================================================
# NUMERIC VALIDATION
# ============================================================================

if (
    df.loc[
        number_of_cases,
        "indicator_result"
    ]
    .dropna()
    .lt(0)
    .any()
):
    raise ValueError(
        "Negative case counts detected."
    )

benchmark_values = (
    df.loc[
        benchmark_percentage,
        "indicator_result"
    ]
    .dropna()
)

if (
    benchmark_values.lt(0).any()
    or benchmark_values.gt(100).any()
):
    raise ValueError(
        "Benchmark percentage values outside 0–100 detected."
    )

print("Numeric-range validation passed.")


# ============================================================================
# STRUCTURAL DUPLICATE VALIDATION
# ============================================================================

structural_columns = [
    "Place or organization",
    "Province/territory",
    "Region",
    "Corporation",
    "Reporting level",
    "Indicator",
    "Indicator segment",
    "Segment value",
    "Time scale",
    "Time frame",
    "Level 1 breakdown",
    "Level 1 breakdown value",
    "Level 2 breakdown",
    "Level 2 breakdown value",
    "Level 3 breakdown",
    "Level 3 breakdown value",
    "Metric",
]

duplicate_count = df.duplicated(
    subset=structural_columns,
    keep=False
).sum()

print(
    f"\nDuplicate structural records: "
    f"{duplicate_count:,}"
)

if duplicate_count:
    raise ValueError(
        "Duplicate structural records detected."
    )

print("Duplicate validation passed.")


# ============================================================================
# FINAL COLUMN SELECTION / RENAMING
# ============================================================================

rename_columns = {
    "Place or organization": "place_or_organization",
    "Province/territory": "province",
    "Region": "region",
    "Corporation": "corporation",
    "Reporting level": "reporting_level",
    "Indicator": "indicator",
    "Measure type": "measure_type",
    "Indicator segment": "indicator_segment",
    "Segment value": "segment_value",
    "Time scale": "time_scale",
    "Time frame": "time_frame",
    "Level 1 breakdown": "level_1_breakdown",
    "Level 1 breakdown value": "level_1_breakdown_value",
    "Level 2 breakdown": "level_2_breakdown",
    "Level 2 breakdown value": "level_2_breakdown_value",
    "Level 3 breakdown": "level_3_breakdown",
    "Level 3 breakdown value": "level_3_breakdown_value",
    "Metric": "metric",
    "Main metric": "main_metric",
    "Unit of measure": "unit_of_measure",
    "Metric value": "metric_value_raw",
    "Confidence interval lower limit": "confidence_interval_lower",
    "Confidence interval upper limit": "confidence_interval_upper",
    "Statistically different": "statistically_different",
    "Performance comparison": "performance_comparison",
    "Performance trend": "performance_trend",
    "Top results": "top_results",
    "Data coverage": "data_coverage",
    "Urban or rural/remote": "urban_or_rural_remote",
    "Hospital peer group": "hospital_peer_group",
    "Long-Term Care Facility Size": "long_term_care_facility_size",
    "Trend note": "trend_note",
    "Refresh date": "refresh_date",
}

df = df.rename(columns=rename_columns)


# ============================================================================
# FINAL COLUMN ORDER
# ============================================================================

final_columns = [
    "place_or_organization",
    "province",
    "region",
    "corporation",
    "reporting_level",
    "indicator",
    "measure_type",
    "indicator_segment",
    "segment_value",
    "time_scale",
    "time_frame",
    "reporting_year",
    "level_1_breakdown",
    "level_1_breakdown_value",
    "level_2_breakdown",
    "level_2_breakdown_value",
    "level_3_breakdown",
    "level_3_breakdown_value",
    "metric",
    "main_metric",
    "metric_value_raw",
    "indicator_result",
    "indicator_result_available",
    "unit_of_measure",
    "confidence_interval_lower",
    "confidence_interval_upper",
    "statistically_different",
    "performance_comparison",
    "performance_trend",
    "top_results",
    "data_coverage",
    "urban_or_rural_remote",
    "hospital_peer_group",
    "long_term_care_facility_size",
    "trend_note",
    "refresh_date",
]

df = df[final_columns]


# ============================================================================
# OUTPUT DIRECTORY
# ============================================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================================
# SAVE
# ============================================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 78)
print("CIHI JOINT REPLACEMENT WAIT TIMES CLEANING COMPLETE")
print("=" * 78)

print(f"\nFinal shape: {df.shape}")

print("\nReporting levels:")
print(df["reporting_level"].value_counts())

print("\nMetrics:")
print(df["metric"].value_counts())

print("\nReporting years:")
print(
    df["reporting_year"]
    .value_counts()
    .sort_index()
)

print("\nIndicator-result availability:")
print(
    df["indicator_result_available"]
    .value_counts()
)

print("\nFinal missing-value summary:")
print(df.isna().sum())

print(f"\nOutput file:\n{OUTPUT_FILE}")

print("\n" + "=" * 78)
print("CLEANING COMPLETE")
print("=" * 78)