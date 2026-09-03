# =============================================================================
# CIHI JOINT REPLACEMENT WAIT TIMES — TRANSFORMATION
# =============================================================================

from pathlib import Path

import pandas as pd


# =============================================================================
# FILE PATHS
# =============================================================================

INPUT_FILE = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
    r"\data\processed\outcomes"
    r"\cihi_joint_replacement_wait_times_clean.csv"
)

OUTPUT_FILE = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
    r"\data\processed\outcomes"
    r"\cihi_joint_replacement_wait_times_transformed.csv"
)


# =============================================================================
# EXPECTED STRUCTURE
# =============================================================================

EXPECTED_INDICATOR = "Joint Replacement Wait Times"

EXPECTED_REPORTING_LEVELS = {
    "Province/territory",
    "Health region",
    "National",
}

EXPECTED_METRICS = {
    "Number of cases",
    "Percentage of cases treated within benchmark",
}

EXPECTED_REPORTING_YEARS = set(range(2019, 2026))

# =============================================================================
# EXPECTED INPUT COLUMNS
# =============================================================================

EXPECTED_COLUMNS = [
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


# =============================================================================
# LOAD DATA
# =============================================================================

print("=" * 78)
print("CIHI JOINT REPLACEMENT WAIT TIMES — TRANSFORMATION")
print("=" * 78)

print()
print("Input file:")
print(INPUT_FILE)

print()
print("Output file:")
print(OUTPUT_FILE)

df = pd.read_csv(
    INPUT_FILE,
    dtype="string"
)

print()
print(f"Input shape: {df.shape}")


# =============================================================================
# COLUMN VALIDATION
# =============================================================================

missing_columns = [
    col for col in EXPECTED_COLUMNS
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing expected columns: {missing_columns}"
    )

print()
print("Column validation passed.")


# =============================================================================
# INDICATOR VALIDATION
# =============================================================================

indicators = set(
    df["indicator"]
    .dropna()
    .unique()
)

if indicators != {EXPECTED_INDICATOR}:
    raise ValueError(
        f"Unexpected indicators found: {sorted(indicators)}"
    )

print("Indicator validation passed.")


# =============================================================================
# REPORTING-LEVEL VALIDATION
# =============================================================================

reporting_levels = set(
    df["reporting_level"]
    .dropna()
    .unique()
)

unexpected_levels = reporting_levels - EXPECTED_REPORTING_LEVELS

if unexpected_levels:
    raise ValueError(
        f"Unexpected reporting levels found: {sorted(unexpected_levels)}"
    )

print("Reporting-level validation passed.")


# =============================================================================
# REPORTING-YEAR VALIDATION
# =============================================================================

years = pd.to_numeric(
    df["reporting_year"],
    errors="coerce"
)

if years.isna().any():
    raise ValueError(
        "Reporting year contains non-numeric or missing values."
    )

df["reporting_year"] = years.astype("Int64")

actual_years = set(
    df["reporting_year"]
    .dropna()
    .astype(int)
    .unique()
)

if not actual_years.issubset(EXPECTED_REPORTING_YEARS):
    raise ValueError(
        f"Unexpected reporting years found: "
        f"{sorted(actual_years - EXPECTED_REPORTING_YEARS)}"
    )

print("Reporting-year validation passed.")


# =============================================================================
# REPORTING-PERIOD VALIDATION
# =============================================================================

if df["time_scale"].dropna().nunique() != 1:
    raise ValueError(
        "Unexpected variation in time scale."
    )

if df["time_scale"].dropna().iloc[0] != "Fiscal year":
    raise ValueError(
        f"Unexpected time scale: "
        f"{df['time_scale'].dropna().unique().tolist()}"
    )

print("Reporting-period validation passed.")


# =============================================================================
# METRIC VALIDATION
# =============================================================================

metrics = set(
    df["metric"]
    .dropna()
    .unique()
)

unexpected_metrics = metrics - EXPECTED_METRICS

if unexpected_metrics:
    raise ValueError(
        f"Unexpected metrics found: {sorted(unexpected_metrics)}"
    )

if metrics != EXPECTED_METRICS:
    raise ValueError(
        f"Expected metrics {EXPECTED_METRICS}, found {metrics}"
    )

print("Metric validation passed.")


# =============================================================================
# CREATE ANALYSIS-READY METRIC FIELDS
# =============================================================================

print()
print("Creating analysis-ready metric fields...")


# -----------------------------------------------------------------------------
# Indicator result
# -----------------------------------------------------------------------------

# The cleaned file retains the original metric value in metric_value_raw.
#
# Valid numeric values are converted to numbers.
# "Not available" becomes <NA>.
#
# This is intentional: "Not available" means the result is unavailable,
# not that the result is zero.

df["indicator_result"] = pd.to_numeric(
    df["metric_value_raw"],
    errors="coerce"
)


# -----------------------------------------------------------------------------
# Availability
# -----------------------------------------------------------------------------

df["indicator_result_available"] = (
    df["indicator_result"].notna()
)


# -----------------------------------------------------------------------------
# Result source
# -----------------------------------------------------------------------------

df["indicator_result_source"] = pd.NA

df.loc[
    df["indicator_result_available"],
    "indicator_result_source"
] = "CIHI metric value"


# -----------------------------------------------------------------------------
# Benchmark percentage
# -----------------------------------------------------------------------------

benchmark_mask = (
    df["metric"]
    == "Percentage of cases treated within benchmark"
)

df["benchmark_pct"] = pd.NA

df.loc[
    benchmark_mask,
    "benchmark_pct"
] = df.loc[
    benchmark_mask,
    "indicator_result"
]


# -----------------------------------------------------------------------------
# Procedure volume
# -----------------------------------------------------------------------------

volume_mask = (
    df["metric"]
    == "Number of cases"
)

df["procedure_volume"] = pd.NA

df.loc[
    volume_mask,
    "procedure_volume"
] = df.loc[
    volume_mask,
    "indicator_result"
]


# -----------------------------------------------------------------------------
# Wait-time fields
# -----------------------------------------------------------------------------

# Joint Replacement Wait Times does not provide the actual waiting-time
# duration in this dataset. It provides cases and percentage treated
# within benchmark.

df["wait_time_measure"] = "not_applicable"

df["wait_time_days"] = pd.NA

df["wait_time_hours"] = pd.NA


# -----------------------------------------------------------------------------
# Benchmark applicability
# -----------------------------------------------------------------------------

df["benchmark_applicable"] = benchmark_mask


# -----------------------------------------------------------------------------
# Analysis unit
# -----------------------------------------------------------------------------

df["analysis_unit"] = "percent"

df.loc[
    volume_mask,
    "analysis_unit"
] = "cases"


# =============================================================================
# VALIDATING TRANSFORMED VALUES
# =============================================================================

print()
print("Validating transformed values...")


# -----------------------------------------------------------------------------
# Indicator-result availability
# -----------------------------------------------------------------------------

expected_availability = (
    df["indicator_result"].notna()
)

if not df["indicator_result_available"].eq(
    expected_availability
).all():
    raise ValueError(
        "Indicator-result availability does not match "
        "transformed indicator-result values."
    )

print(
    "Indicator-result availability validation passed."
)


# -----------------------------------------------------------------------------
# Benchmark validation
# -----------------------------------------------------------------------------

benchmark_available = (
    df.loc[
        benchmark_mask,
        "indicator_result"
    ].notna()
)

benchmark_pct_available = (
    df.loc[
        benchmark_mask,
        "benchmark_pct"
    ].notna()
)

if not benchmark_available.equals(
    benchmark_pct_available
):
    raise ValueError(
        "Benchmark percentage availability does not match "
        "indicator-result availability."
    )

print(
    "Benchmark-value validation passed."
)


# -----------------------------------------------------------------------------
# Volume validation
# -----------------------------------------------------------------------------

volume_available = (
    df.loc[
        volume_mask,
        "indicator_result"
    ].notna()
)

procedure_volume_available = (
    df.loc[
        volume_mask,
        "procedure_volume"
    ].notna()
)

if not volume_available.equals(
    procedure_volume_available
):
    raise ValueError(
        "Procedure-volume availability does not match "
        "indicator-result availability."
    )

print(
    "Procedure-volume validation passed."
)


# -----------------------------------------------------------------------------
# Benchmark range
# -----------------------------------------------------------------------------

benchmark_values = pd.to_numeric(
    df.loc[
        benchmark_mask,
        "benchmark_pct"
    ],
    errors="coerce"
).dropna()

if benchmark_values.lt(0).any():
    raise ValueError(
        "Benchmark percentage contains values below 0."
    )

if benchmark_values.gt(100).any():
    raise ValueError(
        "Benchmark percentage contains values above 100."
    )

print(
    "Benchmark percentage range validation passed."
)


# -----------------------------------------------------------------------------
# Volume range
# -----------------------------------------------------------------------------

volume_values = pd.to_numeric(
    df.loc[
        volume_mask,
        "procedure_volume"
    ],
    errors="coerce"
).dropna()

if volume_values.lt(0).any():
    raise ValueError(
        "Procedure volume contains negative values."
    )

print(
    "Procedure-volume range validation passed."
)


# =============================================================================
# STRUCTURAL VALIDATION
# =============================================================================

print()
print("Structural validation:")

expected_records = 3872

if len(df) != expected_records:
    raise ValueError(
        f"Unexpected record count: {len(df)} "
        f"(expected {expected_records})"
    )

print(
    f"Records: {len(df)}"
)


# -----------------------------------------------------------------------------
# Duplicate structural records
# -----------------------------------------------------------------------------

structural_columns = [
    "place_or_organization",
    "province",
    "region",
    "reporting_level",
    "indicator",
    "time_frame",
    "level_1_breakdown",
    "level_1_breakdown_value",
    "metric",
]

duplicate_count = df.duplicated(
    subset=structural_columns
).sum()

print(
    f"Duplicate structural records: {duplicate_count}"
)

if duplicate_count != 0:
    raise ValueError(
        "Duplicate structural records detected."
    )

print("Structural validation passed.")


# =============================================================================
# COLUMN ORDER
# =============================================================================

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
    "indicator_result_source",
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
    "wait_time_measure",
    "wait_time_days",
    "wait_time_hours",
    "benchmark_pct",
    "benchmark_applicable",
    "procedure_volume",
    "analysis_unit",
]

df = df[final_columns]


# =============================================================================
# SAVE OUTPUT
# =============================================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =============================================================================
# FINAL SUMMARY
# =============================================================================

print()
print("=" * 78)
print("CIHI JOINT REPLACEMENT WAIT TIMES TRANSFORMATION COMPLETE")
print("=" * 78)

print()
print(f"Final shape: {df.shape}")

print()
print("Indicator-result availability:")
print(
    df["indicator_result_available"]
    .value_counts()
    .sort_index()
)

print()
print("Metrics:")
print(
    df["metric"]
    .value_counts()
)

print()
print("Reporting years:")
print(
    df["reporting_year"]
    .value_counts()
    .sort_index()
)

print()
print("Benchmark records:")
print(
    df["benchmark_applicable"]
    .sum()
)

print()
print("Volume records:")
print(
    df["procedure_volume"]
    .notna()
    .sum()
)

print()
print("Output file:")
print(OUTPUT_FILE)

print()
print("=" * 78)
print("TRANSFORMATION COMPLETE")
print("=" * 78)