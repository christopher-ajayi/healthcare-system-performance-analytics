"""
validate_cihi_wait_times.py

Purpose:
    Validate the transformed CIHI Wait Times for Priority Procedures
    dataset before analytical use.

Input:
    data/processed/access/cihi_wait_times_transformed.csv

Expected structure:
    2008–2025
    3 reporting levels
    11 provinces/jurisdiction labels
    14 procedures
    4 metrics
    20,500 structural records

Validation covers:
    1. Column structure
    2. Record count
    3. Reporting-year coverage
    4. Jurisdiction structure
    5. Procedure structure
    6. Metric structure
    7. Reporting-period structure
    8. Duplicate records
    9. Wait-time metric logic
    10. Wait-time unit conversion
    11. Benchmark applicability
    12. Benchmark percentage validation
    13. Procedure volume validation
    14. Availability / suppression logic
    15. Missing-value structure
    16. Data types
    17. Structural uniqueness
    18. Output column order
"""

from pathlib import Path
import pandas as pd


# ======================================================================
# 1. CONFIGURATION
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "access"
    / "cihi_wait_times_transformed.csv"
)


# ======================================================================
# EXPECTED STRUCTURE
# ======================================================================

EXPECTED_COLUMNS = [
    "reporting_level",
    "province",
    "region",
    "indicator",
    "metric",
    "data_year",
    "reporting_year",
    "reporting_period_type",
    "unit_of_measurement",
    "indicator_result",
    "indicator_result_available",
    "indicator_result_source",
    "wait_time_measure",
    "wait_time_days",
    "wait_time_hours",
    "benchmark_pct",
    "benchmark_applicable",
    "procedure_volume",
    "analysis_unit",
]


EXPECTED_REPORTING_LEVELS = {
    "Provincial",
    "Regional",
    "National",
}


EXPECTED_PROVINCES = {
    "Alberta",
    "British Columbia",
    "Canada",
    "Manitoba",
    "New Brunswick",
    "Newfoundland and Labrador",
    "Nova Scotia",
    "Ontario",
    "Prince Edward Island",
    "Quebec",
    "Saskatchewan",
}


EXPECTED_PROCEDURES = {
    "Bladder Cancer Surgery",
    "Breast Cancer Surgery",
    "CABG",
    "CT Scan",
    "Cataract Surgery",
    "Colorectal Cancer Surgery",
    "Hip Fracture Repair",
    "Hip Fracture Repair/Emergency and Inpatient",
    "Hip Replacement",
    "Knee Replacement",
    "Lung Cancer Surgery",
    "MRI Scan",
    "Prostate Cancer Surgery",
    "Radiation Therapy",
}


EXPECTED_METRICS = {
    "50th percentile",
    "90th percentile",
    "Volume",
    "% meeting benchmark",
}


EXPECTED_PERIOD_TYPES = {
    "Apr-Sep",
    "FY",
    "Q3Q4",
}


EXPECTED_UNITS = {
    "Days",
    "Hours",
    "Number of cases",
    "Proportion",
}


BENCHMARK_PROCEDURES = {
    "Hip Replacement",
    "Knee Replacement",
    "Cataract Surgery",
    "Radiation Therapy",
    "Hip Fracture Repair",
    "Hip Fracture Repair/Emergency and Inpatient",
    "CABG",
}


EXPECTED_RECORDS = 20500
EXPECTED_YEARS = 18


# ======================================================================
# HEADER
# ======================================================================

print("=" * 70)
print("CIHI WAIT TIMES — TRANSFORMED DATA VALIDATION")
print("=" * 70)

print(f"\nInput file:")
print(INPUT_FILE)


# ======================================================================
# 2. FILE CHECK
# ======================================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nTransformed file not found:\n{INPUT_FILE}"
    )


# ======================================================================
# LOAD DATA
# ======================================================================

df = pd.read_csv(
    INPUT_FILE,
    keep_default_na=True,
)

print(f"\nInput shape: {df.shape}")


# ======================================================================
# 3. COLUMN VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("1. COLUMN VALIDATION")
print("-" * 70)

actual_columns = list(df.columns)

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in actual_columns
]

unexpected_columns = [
    column
    for column in actual_columns
    if column not in EXPECTED_COLUMNS
]

if missing_columns:
    raise ValueError(
        "Missing required columns:\n"
        + "\n".join(
            f"  - {column}"
            for column in missing_columns
        )
    )

if unexpected_columns:
    raise ValueError(
        "Unexpected columns detected:\n"
        + "\n".join(
            f"  - {column}"
            for column in unexpected_columns
        )
    )

print("Column validation passed.")

print("\nColumns:")

for column in df.columns:
    print(f"  - {column}")


# ======================================================================
# 4. RECORD COUNT
# ======================================================================

print("\n" + "-" * 70)
print("2. RECORD COUNT")
print("-" * 70)

actual_records = len(df)

print(f"Actual records:   {actual_records}")
print(f"Expected records: {EXPECTED_RECORDS}")

if actual_records != EXPECTED_RECORDS:
    raise ValueError(
        f"Unexpected record count: "
        f"{actual_records}. "
        f"Expected {EXPECTED_RECORDS}."
    )

print("Record-count validation passed.")


# ======================================================================
# 5. REPORTING YEAR VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("3. REPORTING-YEAR VALIDATION")
print("-" * 70)

years = sorted(
    pd.to_numeric(
        df["reporting_year"],
        errors="coerce"
    ).dropna().unique()
)

if len(years) != EXPECTED_YEARS:
    raise ValueError(
        f"Unexpected number of reporting years: "
        f"{len(years)}. Expected {EXPECTED_YEARS}."
    )

expected_years = set(range(2008, 2026))
actual_years = set(years)

missing_years = expected_years - actual_years
unexpected_years = actual_years - expected_years

if missing_years:
    raise ValueError(
        "Missing reporting years:\n"
        + "\n".join(
            f"  - {year}"
            for year in sorted(missing_years)
        )
    )

if unexpected_years:
    raise ValueError(
        "Unexpected reporting years:\n"
        + "\n".join(
            f"  - {year}"
            for year in sorted(unexpected_years)
        )
    )

print("Reporting-year validation passed.")
print(f"  Years: {len(years)}")
print(f"  Coverage: {min(years)} → {max(years)}")


# ======================================================================
# 6. REPORTING LEVEL VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("4. REPORTING-LEVEL VALIDATION")
print("-" * 70)

actual_levels = set(
    df["reporting_level"]
    .dropna()
    .unique()
)

unexpected_levels = (
    actual_levels - EXPECTED_REPORTING_LEVELS
)

if unexpected_levels:
    raise ValueError(
        "Unexpected reporting levels:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(unexpected_levels)
        )
    )

missing_levels = (
    EXPECTED_REPORTING_LEVELS - actual_levels
)

if missing_levels:
    raise ValueError(
        "Expected reporting levels missing:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(missing_levels)
        )
    )

print("Reporting-level validation passed.")
print(f"  Reporting levels: {len(actual_levels)}")

print(
    df["reporting_level"]
    .value_counts()
    .to_string()
)


# ======================================================================
# 7. JURISDICTION VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("5. JURISDICTION VALIDATION")
print("-" * 70)

actual_provinces = set(
    df["province"]
    .dropna()
    .unique()
)

unexpected_provinces = (
    actual_provinces - EXPECTED_PROVINCES
)

if unexpected_provinces:
    raise ValueError(
        "Unexpected provinces/jurisdictions:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(unexpected_provinces)
        )
    )

missing_provinces = (
    EXPECTED_PROVINCES - actual_provinces
)

if missing_provinces:
    raise ValueError(
        "Expected provinces/jurisdictions missing:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(missing_provinces)
        )
    )

print("Jurisdiction validation passed.")
print(f"  Jurisdictions: {len(actual_provinces)}")


# ======================================================================
# 8. PROCEDURE VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("6. PROCEDURE VALIDATION")
print("-" * 70)

actual_procedures = set(
    df["indicator"]
    .dropna()
    .unique()
)

unexpected_procedures = (
    actual_procedures - EXPECTED_PROCEDURES
)

if unexpected_procedures:
    raise ValueError(
        "Unexpected procedures detected:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(unexpected_procedures)
        )
    )

missing_procedures = (
    EXPECTED_PROCEDURES - actual_procedures
)

if missing_procedures:
    raise ValueError(
        "Expected procedures missing:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(missing_procedures)
        )
    )

print("Procedure validation passed.")
print(f"  Procedures: {len(actual_procedures)}")

print(
    df["indicator"]
    .value_counts()
    .sort_index()
    .to_string()
)


# ======================================================================
# 9. METRIC VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("7. METRIC VALIDATION")
print("-" * 70)

actual_metrics = set(
    df["metric"]
    .dropna()
    .unique()
)

unexpected_metrics = (
    actual_metrics - EXPECTED_METRICS
)

if unexpected_metrics:
    raise ValueError(
        "Unexpected metrics detected:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(unexpected_metrics)
        )
    )

missing_metrics = (
    EXPECTED_METRICS - actual_metrics
)

if missing_metrics:
    raise ValueError(
        "Expected metrics missing:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(missing_metrics)
        )
    )

print("Metric validation passed.")

print(
    df["metric"]
    .value_counts()
    .to_string()
)


# ======================================================================
# 10. REPORTING PERIOD VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("8. REPORTING-PERIOD VALIDATION")
print("-" * 70)

actual_periods = set(
    df["reporting_period_type"]
    .dropna()
    .unique()
)

unexpected_periods = (
    actual_periods - EXPECTED_PERIOD_TYPES
)

if unexpected_periods:
    raise ValueError(
        "Unexpected reporting periods:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(unexpected_periods)
        )
    )

missing_periods = (
    EXPECTED_PERIOD_TYPES - actual_periods
)

if missing_periods:
    raise ValueError(
        "Expected reporting periods missing:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(missing_periods)
        )
    )

print("Reporting-period validation passed.")

print(
    df["reporting_period_type"]
    .value_counts()
    .to_string()
)


# ======================================================================
# 11. UNIT VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("9. UNIT-OF-MEASUREMENT VALIDATION")
print("-" * 70)

actual_units = set(
    df["unit_of_measurement"]
    .dropna()
    .unique()
)

unexpected_units = (
    actual_units - EXPECTED_UNITS
)

if unexpected_units:
    raise ValueError(
        "Unexpected units of measurement:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(unexpected_units)
        )
    )

print("Unit-of-measurement validation passed.")


# ======================================================================
# 12. DUPLICATE VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("10. DUPLICATE VALIDATION")
print("-" * 70)

key_columns = [
    "reporting_level",
    "province",
    "region",
    "indicator",
    "metric",
    "data_year",
]

duplicate_count = df.duplicated(
    subset=key_columns
).sum()

print(
    f"Duplicate structural records: "
    f"{duplicate_count}"
)

if duplicate_count > 0:

    duplicates = df[
        df.duplicated(
            subset=key_columns,
            keep=False
        )
    ]

    print("\nDuplicate records:")
    print(
        duplicates[
            key_columns
        ].sort_values(
            key_columns
        ).to_string(index=False)
    )

    raise ValueError(
        "Duplicate structural records detected."
    )

print("Duplicate validation passed.")


# ======================================================================
# 13. WAIT-TIME MEASURE VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("11. WAIT-TIME MEASURE VALIDATION")
print("-" * 70)

wait_time_rows = df[
    df["metric"].isin(
        [
            "50th percentile",
            "90th percentile",
        ]
    )
]

invalid_measure = wait_time_rows[
    ~wait_time_rows["wait_time_measure"].isin(
        [
            "median",
            "90th_percentile",
        ]
    )
]

if not invalid_measure.empty:
    raise ValueError(
        "Invalid wait-time measure detected."
    )

median_rows = df[
    df["metric"] == "50th percentile"
]

invalid_median = median_rows[
    median_rows["wait_time_measure"] != "median"
]

if not invalid_median.empty:
    raise ValueError(
        "50th-percentile records are not "
        "mapped to median."
    )

p90_rows = df[
    df["metric"] == "90th percentile"
]

invalid_p90 = p90_rows[
    p90_rows["wait_time_measure"]
    != "90th_percentile"
]

if not invalid_p90.empty:
    raise ValueError(
        "90th-percentile records are not "
        "mapped correctly."
    )

print("Wait-time measure validation passed.")


# ======================================================================
# 14. WAIT-TIME UNIT CONVERSION
# ======================================================================

print("\n" + "-" * 70)
print("12. WAIT-TIME UNIT VALIDATION")
print("-" * 70)

day_rows = df[
    df["unit_of_measurement"] == "Days"
]

hour_rows = df[
    df["unit_of_measurement"] == "Hours"
]


# Days must populate wait_time_days
invalid_days = day_rows[
    day_rows["indicator_result_available"]
    & day_rows["wait_time_days"].isna()
    & day_rows["metric"].isin(
        [
            "50th percentile",
            "90th percentile",
        ]
    )
]

if not invalid_days.empty:
    raise ValueError(
        "Available day-based wait-time records "
        "are missing wait_time_days."
    )


# Hours must populate wait_time_hours
invalid_hours = hour_rows[
    hour_rows["indicator_result_available"]
    & hour_rows["wait_time_hours"].isna()
    & hour_rows["metric"].isin(
        [
            "50th percentile",
            "90th percentile",
        ]
    )
]

if not invalid_hours.empty:
    raise ValueError(
        "Available hour-based wait-time records "
        "are missing wait_time_hours."
    )


# Hour values must not appear in day field
if (
    df.loc[
        df["unit_of_measurement"] == "Hours",
        "wait_time_days"
    ].notna()
).any():

    raise ValueError(
        "Hour-based wait-time records contain "
        "unexpected wait_time_days values."
    )


# Day values must not appear in hour field
if (
    df.loc[
        df["unit_of_measurement"] == "Days",
        "wait_time_hours"
    ].notna()
).any():

    raise ValueError(
        "Day-based wait-time records contain "
        "unexpected wait_time_hours values."
    )


print("Wait-time unit validation passed.")


# ======================================================================
# 15. BENCHMARK VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("13. BENCHMARK VALIDATION")
print("-" * 70)

benchmark_rows = df[
    df["metric"] == "% meeting benchmark"
]

non_benchmark_rows = df[
    df["metric"] != "% meeting benchmark"
]


# All benchmark metric rows must be applicable
invalid_benchmark_flag = benchmark_rows[
    benchmark_rows["benchmark_applicable"] != True
]

if not invalid_benchmark_flag.empty:
    raise ValueError(
        "Benchmark metric records are not "
        "marked benchmark_applicable=True."
    )


# Non-benchmark metrics must not be marked applicable
invalid_non_benchmark_flag = non_benchmark_rows[
    non_benchmark_rows["benchmark_applicable"] != False
]

if not invalid_non_benchmark_flag.empty:
    raise ValueError(
        "Non-benchmark metric records are "
        "incorrectly marked benchmark_applicable=True."
    )


# Benchmark records must belong to benchmark procedures
invalid_benchmark_procedures = benchmark_rows[
    ~benchmark_rows["indicator"].isin(
        BENCHMARK_PROCEDURES
    )
]

if not invalid_benchmark_procedures.empty:
    print(
        "\nUnexpected benchmark procedures:"
    )

    print(
        invalid_benchmark_procedures[
            ["indicator", "metric"]
        ]
        .drop_duplicates()
        .to_string(index=False)
    )

    raise ValueError(
        "Benchmark values detected for "
        "procedures outside the defined "
        "benchmark procedure set."
    )


# Benchmark percentages must be 0–100
available_benchmarks = benchmark_rows[
    benchmark_rows["indicator_result_available"]
]

invalid_benchmark_values = available_benchmarks[
    (
        (available_benchmarks["benchmark_pct"] < 0)
        |
        (available_benchmarks["benchmark_pct"] > 100)
    )
]

if not invalid_benchmark_values.empty:
    raise ValueError(
        "Benchmark percentage outside "
        "0–100 range detected."
    )


print("Benchmark validation passed.")

print(
    f"  Benchmark records: "
    f"{len(benchmark_rows)}"
)


# ======================================================================
# 16. PROCEDURE VOLUME VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("14. PROCEDURE VOLUME VALIDATION")
print("-" * 70)

volume_rows = df[
    df["metric"] == "Volume"
]

invalid_volume_unit = volume_rows[
    volume_rows["unit_of_measurement"]
    != "Number of cases"
]

if not invalid_volume_unit.empty:
    raise ValueError(
        "Volume records have an invalid "
        "unit of measurement."
    )


available_volume = volume_rows[
    volume_rows["indicator_result_available"]
]

invalid_volume_values = available_volume[
    available_volume["procedure_volume"] < 0
]

if not invalid_volume_values.empty:
    raise ValueError(
        "Negative procedure volume detected."
    )


print("Procedure-volume validation passed.")

print(
    f"  Volume records: {len(volume_rows)}"
)


# ======================================================================
# 17. AVAILABILITY / SUPPRESSION VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("15. AVAILABILITY / SUPPRESSION VALIDATION")
print("-" * 70)

available = df[
    df["indicator_result_available"] == True
]

unavailable = df[
    df["indicator_result_available"] == False
]

print(
    f"Available indicator results: "
    f"{len(available)}"
)

print(
    f"Unavailable indicator results: "
    f"{len(unavailable)}"
)


# Available rows must have a numeric indicator result
available_missing_result = available[
    available["indicator_result"].isna()
]

if not available_missing_result.empty:
    raise ValueError(
        "Available records contain missing "
        "indicator_result values."
    )


# Unavailable rows must have missing result
unavailable_with_result = unavailable[
    unavailable["indicator_result"].notna()
]

if not unavailable_with_result.empty:
    raise ValueError(
        "Unavailable records contain "
        "indicator_result values."
    )


# Unavailable rows must have source missing
unavailable_source = unavailable[
    unavailable["indicator_result_source"].notna()
]

if not unavailable_source.empty:
    raise ValueError(
        "Unavailable records contain "
        "indicator_result_source values."
    )


print("Availability/suppression validation passed.")


# ======================================================================
# 18. MISSING-VALUE STRUCTURE
# ======================================================================

print("\n" + "-" * 70)
print("16. MISSING-VALUE VALIDATION")
print("-" * 70)

print(
    df.isna()
    .sum()
    .to_string()
)


# Structural fields must never be missing
structural_columns = [
    "reporting_level",
    "province",
    "indicator",
    "metric",
    "data_year",
    "reporting_year",
    "reporting_period_type",
    "unit_of_measurement",
    "indicator_result_available",
    "benchmark_applicable",
    "analysis_unit",
]

for column in structural_columns:

    if df[column].isna().any():
        raise ValueError(
            f"Missing structural values detected "
            f"in {column}."
        )


print(
    "\nStructural missing-value validation passed."
)


# ======================================================================
# 19. DATA TYPE VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("17. DATA-TYPE VALIDATION")
print("-" * 70)

numeric_columns = [
    "reporting_year",
    "indicator_result",
    "wait_time_days",
    "wait_time_hours",
    "benchmark_pct",
    "procedure_volume",
]

for column in numeric_columns:

    converted = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    non_convertible = (
        df[column].notna()
        & converted.isna()
    )

    if non_convertible.any():
        raise ValueError(
            f"Non-numeric values detected "
            f"in numeric column: {column}"
        )

print("Data-type validation passed.")


# ======================================================================
# 20. STRUCTURAL UNIQUENESS
# ======================================================================

print("\n" + "-" * 70)
print("18. STRUCTURAL UNIQUENESS VALIDATION")
print("-" * 70)

expected_combinations = (
    df[
        key_columns
    ]
    .drop_duplicates()
    .shape[0]
)

actual_combinations = len(df)

print(
    f"Expected combinations: {expected_combinations}"
)

print(
    f"Actual combinations:   {actual_combinations}"
)

if expected_combinations != actual_combinations:
    raise ValueError(
        "Structural uniqueness validation failed."
    )

print("Structural uniqueness validation passed.")


# ======================================================================
# 21. OUTPUT ORDER VALIDATION
# ======================================================================

print("\n" + "-" * 70)
print("19. OUTPUT ORDER VALIDATION")
print("-" * 70)

if list(df.columns) != EXPECTED_COLUMNS:

    raise ValueError(
        "Output column order does not match "
        "the expected structure."
    )

print("Output column order validation passed.")


# ======================================================================
# 22. FINAL SUMMARY
# ======================================================================

print("\n" + "=" * 70)
print("CIHI WAIT TIMES VALIDATION COMPLETE")
print("=" * 70)

print("\nFINAL VALIDATION SUMMARY")

print(
    f"  Records:                 {len(df)}"
)

print(
    f"  Reporting years:         "
    f"{df['reporting_year'].nunique()}"
)

print(
    f"  Reporting levels:        "
    f"{df['reporting_level'].nunique()}"
)

print(
    f"  Jurisdictions:           "
    f"{df['province'].nunique()}"
)

print(
    f"  Procedures:              "
    f"{df['indicator'].nunique()}"
)

print(
    f"  Metrics:                 "
    f"{df['metric'].nunique()}"
)

print(
    f"  Available results:       "
    f"{df['indicator_result_available'].sum()}"
)

print(
    f"  Unavailable results:     "
    f"{(~df['indicator_result_available']).sum()}"
)

print(
    f"  Benchmark records:       "
    f"{df['benchmark_applicable'].sum()}"
)

print(
    f"  Volume records:          "
    f"{(df['metric'] == 'Volume').sum()}"
)

print("\nReporting periods:")

print(
    df["reporting_period_type"]
    .value_counts()
    .to_string()
)

print("\nMetrics:")

print(
    df["metric"]
    .value_counts()
    .to_string()
)

print("\nProcedures:")

print(
    df["indicator"]
    .value_counts()
    .sort_index()
    .to_string()
)

print(
    f"\nValidated file:\n{INPUT_FILE}"
)

print("\n" + "=" * 70)
print("VALIDATION PASSED")
print("=" * 70)