"""
transform_cihi_wait_times.py

Purpose:
    Transform the cleaned CIHI Table 1 wait-times dataset into an
    analysis-ready access dataset.

Input:
    data/processed/access/cihi_wait_times_clean.csv

Output:
    data/processed/access/cihi_wait_times_transformed.csv

Methodological principles:
    - Preserve the complete structural dataset.
    - Preserve unavailable/suppressed observations.
    - Do not infer missing values.
    - Keep reporting-period distinctions.
    - Separate wait-time, benchmark and volume measures.
    - Do not impose an artificial benchmark-procedure restriction.
"""

from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# 1. CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "access"
    / "cihi_wait_times_clean.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "access"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "cihi_wait_times_transformed.csv"
)


# ============================================================
# 2. EXPECTED STRUCTURE
# ============================================================

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
]


EXPECTED_REPORTING_LEVELS = {
    "Provincial",
    "Regional",
    "National",
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


# ============================================================
# 3. HEADER
# ============================================================

print("=" * 70)
print("CIHI WAIT TIMES — TRANSFORMATION")
print("=" * 70)

print(f"\nInput file:")
print(INPUT_FILE)

print(f"\nOutput file:")
print(OUTPUT_FILE)


# ============================================================
# 4. FILE CHECK
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )


# ============================================================
# 5. LOAD CLEANED DATA
# ============================================================

df = pd.read_csv(
    INPUT_FILE
)

print(f"\nInput shape: {df.shape}")


# ============================================================
# 6. COLUMN VALIDATION
# ============================================================

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "Missing required columns:\n"
        + "\n".join(
            f"  - {column}"
            for column in missing_columns
        )
    )

print("\nColumn validation passed.")


# ============================================================
# 7. PRESERVE ORIGINAL STRUCTURE
# ============================================================

df = df[EXPECTED_COLUMNS].copy()


# ============================================================
# 8. TEXT STANDARDIZATION
# ============================================================

text_columns = [
    "reporting_level",
    "province",
    "region",
    "indicator",
    "metric",
    "data_year",
    "reporting_period_type",
    "unit_of_measurement",
    "indicator_result_source",
]

for column in text_columns:

    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# ============================================================
# 9. REPORTING YEAR
# ============================================================

df["reporting_year"] = pd.to_numeric(
    df["reporting_year"],
    errors="coerce"
)

if df["reporting_year"].isna().any():

    raise ValueError(
        "Invalid or missing reporting_year values detected."
    )

df["reporting_year"] = (
    df["reporting_year"]
    .astype(int)
)


# ============================================================
# 10. INDICATOR RESULT
# ============================================================

df["indicator_result"] = pd.to_numeric(
    df["indicator_result"],
    errors="coerce"
)


# ============================================================
# 11. AVAILABILITY FLAG
# ============================================================

df["indicator_result_available"] = (
    df["indicator_result"].notna()
)


# ============================================================
# 12. VERIFY AVAILABILITY AGAINST SOURCE FLAG
# ============================================================

source_available = (
    df["indicator_result_source"]
    .eq("available")
)

source_unavailable = (
    df["indicator_result_source"]
    .eq("unavailable")
)

if (
    (source_available & ~df["indicator_result_available"])
    .any()
):

    raise ValueError(
        "Rows marked as available contain missing indicator results."
    )

if (
    (source_unavailable & df["indicator_result_available"])
    .any()
):

    raise ValueError(
        "Rows marked as unavailable contain numeric indicator results."
    )


# ============================================================
# 13. REPORTING LEVEL VALIDATION
# ============================================================

unexpected_reporting_levels = (
    set(df["reporting_level"].dropna().unique())
    - EXPECTED_REPORTING_LEVELS
)

if unexpected_reporting_levels:

    raise ValueError(
        "Unexpected reporting levels detected:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(
                unexpected_reporting_levels
            )
        )
    )

print("Reporting-level validation passed.")


# ============================================================
# 14. METRIC VALIDATION
# ============================================================

unexpected_metrics = (
    set(df["metric"].dropna().unique())
    - EXPECTED_METRICS
)

if unexpected_metrics:

    raise ValueError(
        "Unexpected metrics detected:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(
                unexpected_metrics
            )
        )
    )

print("Metric validation passed.")


# ============================================================
# 15. REPORTING PERIOD VALIDATION
# ============================================================

unexpected_periods = (
    set(df["reporting_period_type"].dropna().unique())
    - EXPECTED_PERIOD_TYPES
)

if unexpected_periods:

    raise ValueError(
        "Unexpected reporting-period types detected:\n"
        + "\n".join(
            f"  - {value}"
            for value in sorted(
                unexpected_periods
            )
        )
    )

print("Reporting-period validation passed.")


# ============================================================
# 16. DATA YEAR VALIDATION
# ============================================================

if df["reporting_year"].min() < 2008:

    raise ValueError(
        "Reporting years earlier than 2008 detected."
    )

if df["reporting_year"].max() > 2025:

    raise ValueError(
        "Reporting years later than 2025 detected."
    )

print(
    "Reporting-year validation passed."
)


# ============================================================
# 17. METRIC-SPECIFIC DERIVED VARIABLES
# ============================================================

print(
    "\nCreating analysis-ready metric fields..."
)


# ------------------------------------------------------------
# Wait-time metrics
# ------------------------------------------------------------

df["wait_time_days"] = np.nan

wait_time_mask = (
    df["metric"].isin(
        {
            "50th percentile",
            "90th percentile",
        }
    )
    & df["unit_of_measurement"].eq("Days")
    & df["indicator_result_available"]
)

df.loc[
    wait_time_mask,
    "wait_time_days"
] = df.loc[
    wait_time_mask,
    "indicator_result"
]


# ------------------------------------------------------------
# Wait-time hours
# ------------------------------------------------------------

df["wait_time_hours"] = np.nan

wait_time_hours_mask = (
    df["metric"].isin(
        {
            "50th percentile",
            "90th percentile",
        }
    )
    & df["unit_of_measurement"].eq("Hours")
    & df["indicator_result_available"]
)

df.loc[
    wait_time_hours_mask,
    "wait_time_hours"
] = df.loc[
    wait_time_hours_mask,
    "indicator_result"
]


# ------------------------------------------------------------
# Benchmark percentage
# ------------------------------------------------------------

df["benchmark_pct"] = np.nan

benchmark_mask = (
    df["metric"].eq("% meeting benchmark")
    & df["indicator_result_available"]
)

df.loc[
    benchmark_mask,
    "benchmark_pct"
] = df.loc[
    benchmark_mask,
    "indicator_result"
]


# ------------------------------------------------------------
# Procedure volume
# ------------------------------------------------------------

df["procedure_volume"] = np.nan

volume_mask = (
    df["metric"].eq("Volume")
    & df["indicator_result_available"]
)

df.loc[
    volume_mask,
    "procedure_volume"
] = df.loc[
    volume_mask,
    "indicator_result"
]


# ============================================================
# 18. BENCHMARK IDENTIFICATION
# ============================================================

"""
IMPORTANT:

Do not hard-code a destructive list of benchmark procedures.

The CIHI workbook itself identifies benchmark information through
the "% meeting benchmark" metric.

Therefore:

    benchmark_applicable = True

whenever the dataset contains a benchmark metric for that
procedure/jurisdiction/reporting period.

This preserves CIHI's actual reported structure.
"""

df["benchmark_applicable"] = (
    df["metric"]
    .eq("% meeting benchmark")
)


# ============================================================
# 19. WAIT-TIME MEASURE TYPE
# ============================================================

df["wait_time_measure"] = "not_applicable"

df.loc[
    df["metric"].eq("50th percentile"),
    "wait_time_measure"
] = "median"

df.loc[
    df["metric"].eq("90th percentile"),
    "wait_time_measure"
] = "90th_percentile"


# ============================================================
# 20. UNIT NORMALIZATION
# ============================================================

df["analysis_unit"] = "not_applicable"

df.loc[
    df["metric"].isin(
        {
            "50th percentile",
            "90th percentile",
        }
    )
    & df["unit_of_measurement"].eq("Days"),
    "analysis_unit"
] = "days"

df.loc[
    df["metric"].isin(
        {
            "50th percentile",
            "90th percentile",
        }
    )
    & df["unit_of_measurement"].eq("Hours"),
    "analysis_unit"
] = "hours"

df.loc[
    df["metric"].eq("% meeting benchmark"),
    "analysis_unit"
] = "percent"

df.loc[
    df["metric"].eq("Volume"),
    "analysis_unit"
] = "cases"


# ============================================================
# 21. VALUE VALIDATION
# ============================================================

print("\nValidating transformed values...")


# ------------------------------------------------------------
# Percentile wait times
# ------------------------------------------------------------

percentile_mask = (
    df["metric"].isin(
        {
            "50th percentile",
            "90th percentile",
        }
    )
    & df["indicator_result_available"]
)

if (
    df.loc[
        percentile_mask,
        "indicator_result"
    ] < 0
).any():

    raise ValueError(
        "Negative wait-time values detected."
    )


# ------------------------------------------------------------
# Benchmark percentages
# ------------------------------------------------------------

if (
    df.loc[
        benchmark_mask,
        "benchmark_pct"
    ] < 0
).any():

    raise ValueError(
        "Negative benchmark percentages detected."
    )

if (
    df.loc[
        benchmark_mask,
        "benchmark_pct"
    ] > 100
).any():

    raise ValueError(
        "Benchmark percentages greater than 100 detected."
    )


# ------------------------------------------------------------
# Volumes
# ------------------------------------------------------------

if (
    df.loc[
        volume_mask,
        "procedure_volume"
    ] < 0
).any():

    raise ValueError(
        "Negative procedure volumes detected."
    )


print("Metric-value validation passed.")


# ============================================================
# 22. STRUCTURAL VALIDATION
# ============================================================

expected_records = 20500

actual_records = len(df)

print("\nStructural validation:")
print(f"  Records: {actual_records}")

if actual_records != expected_records:

    raise ValueError(
        f"Unexpected record count: "
        f"{actual_records}. "
        f"Expected {expected_records}."
    )


# ============================================================
# 23. DUPLICATE VALIDATION
# ============================================================

key_columns = [
    "reporting_level",
    "province",
    "region",
    "indicator",
    "metric",
    "data_year",
]

duplicate_count = (
    df.duplicated(
        subset=key_columns
    )
    .sum()
)

print(
    f"Duplicate structural records: "
    f"{duplicate_count}"
)

if duplicate_count > 0:

    raise ValueError(
        "Duplicate structural records detected."
    )


# ============================================================
# 24. PROCEDURE SUMMARY
# ============================================================

print("\nProcedures:")

print(
    df["indicator"]
    .value_counts()
    .sort_index()
    .to_string()
)


# ============================================================
# 25. METRIC SUMMARY
# ============================================================

print("\nMetrics:")

print(
    df["metric"]
    .value_counts()
    .to_string()
)


# ============================================================
# 26. PERIOD SUMMARY
# ============================================================

print("\nReporting periods:")

print(
    df["reporting_period_type"]
    .value_counts()
    .to_string()
)


# ============================================================
# 27. BENCHMARK SUMMARY
# ============================================================

print("\nBenchmark records:")

benchmark_summary = (
    df.loc[
        df["benchmark_applicable"]
    ]
    .groupby("indicator")
    .size()
    .sort_values(
        ascending=False
    )
)

print(
    benchmark_summary.to_string()
)


# ============================================================
# 28. AVAILABLE / UNAVAILABLE SUMMARY
# ============================================================

print("\nIndicator-result availability:")

print(
    df["indicator_result_available"]
    .value_counts()
    .to_string()
)


# ============================================================
# 29. FINAL COLUMN ORDER
# ============================================================

final_columns = [
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

df = df[final_columns]


# ============================================================
# 30. SORT
# ============================================================

df = df.sort_values(
    by=[
        "reporting_year",
        "reporting_period_type",
        "reporting_level",
        "province",
        "region",
        "indicator",
        "metric",
    ],
    na_position="last",
).reset_index(
    drop=True
)


# ============================================================
# 31. FINAL NULL CHECK
# ============================================================

print("\nFinal missing-value summary:")

print(
    df.isna()
    .sum()
    .to_string()
)


# ============================================================
# 32. SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 33. FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("CIHI WAIT TIMES TRANSFORMATION COMPLETE")
print("=" * 70)

print(
    f"\nFinal shape: {df.shape}"
)

print(
    f"\nOutput file:\n{OUTPUT_FILE}"
)

print("\nAvailable indicator results:")

print(
    df["indicator_result_available"]
    .value_counts()
    .to_string()
)

print("\nWait-time records:")

print(
    df["wait_time_measure"]
    .value_counts()
    .to_string()
)

print("\nBenchmark records:")

print(
    df["benchmark_applicable"]
    .value_counts()
    .to_string()
)

print("\nVolume records:")

print(
    df["metric"]
    .eq("Volume")
    .sum()
)

print("\nFirst 10 transformed records:")

print(
    df.head(10)
    .to_string(index=False)
)

print("\n" + "=" * 70)
print("TRANSFORMATION COMPLETE")
print("=" * 70)