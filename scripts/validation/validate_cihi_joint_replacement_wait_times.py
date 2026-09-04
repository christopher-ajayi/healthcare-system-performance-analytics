from pathlib import Path

import pandas as pd


# =============================================================================
# CONFIGURATION
# =============================================================================

INPUT_FILE = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
    r"\data\processed\outcomes"
    r"\cihi_joint_replacement_wait_times_transformed.csv"
)

EXPECTED_RECORDS = 3872

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

EXPECTED_PROVINCES = {
    "Alberta",
    "British Columbia",
    "Manitoba",
    "New Brunswick",
    "Newfoundland and Labrador",
    "Northwest Territories",
    "Nova Scotia",
    "Nunavut",
    "Ontario",
    "Prince Edward Island",
    "Quebec",
    "Saskatchewan",
    "Yukon",
}

EXPECTED_YEARS = set(range(2019, 2026))


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


# =============================================================================
# HELPERS
# =============================================================================

def section(title):
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def fail(message):
    raise ValueError(message)


# =============================================================================
# LOAD DATA
# =============================================================================

print("=" * 78)
print("CIHI JOINT REPLACEMENT WAIT TIMES — TRANSFORMED DATA VALIDATION")
print("=" * 78)

print("\nInput file:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    fail(f"Input file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

print(f"\nInput shape: {df.shape}")


# =============================================================================
# 1. COLUMN VALIDATION
# =============================================================================

section("1. COLUMN VALIDATION")

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

if missing_columns or unexpected_columns:
    fail(
        "Column validation failed.\n"
        f"Missing columns: {missing_columns}\n"
        f"Unexpected columns: {unexpected_columns}"
    )

print("Column validation passed.")

print("\nColumns:")

for column in actual_columns:
    print(f"  - {column}")


# =============================================================================
# 2. RECORD COUNT
# =============================================================================

section("2. RECORD COUNT")

actual_records = len(df)

print(f"Actual records:   {actual_records}")
print(f"Expected records: {EXPECTED_RECORDS}")

if actual_records != EXPECTED_RECORDS:
    fail(
        f"Record-count validation failed: "
        f"expected {EXPECTED_RECORDS}, found {actual_records}"
    )

print("Record-count validation passed.")


# =============================================================================
# 3. INDICATOR VALIDATION
# =============================================================================

section("3. INDICATOR VALIDATION")

indicators = set(df["indicator"].dropna().unique())

if indicators != {EXPECTED_INDICATOR}:
    fail(
        f"Unexpected indicators found: {sorted(indicators)}"
    )

if df["indicator"].isna().any():
    fail("Indicator validation failed: missing indicator values detected.")

print("Indicator validation passed.")
print(f"Indicator: {EXPECTED_INDICATOR}")


# =============================================================================
# 4. REPORTING-YEAR VALIDATION
# =============================================================================

section("4. REPORTING-YEAR VALIDATION")

reporting_year_numeric = pd.to_numeric(
    df["reporting_year"],
    errors="coerce"
)

if reporting_year_numeric.isna().any():
    fail("Reporting-year validation failed: missing/non-numeric years detected.")

years = set(reporting_year_numeric.astype(int))

if years != EXPECTED_YEARS:
    fail(
        "Unexpected reporting years.\n"
        f"Expected: {sorted(EXPECTED_YEARS)}\n"
        f"Actual:   {sorted(years)}"
    )

print("Reporting-year validation passed.")
print(f"  Years: {len(years)}")
print(f"  Coverage: {min(years)} → {max(years)}")

print("\nReporting-year counts:")
print(
    df["reporting_year"]
    .value_counts()
    .sort_index()
)


# =============================================================================
# 5. REPORTING-LEVEL VALIDATION
# =============================================================================

section("5. REPORTING-LEVEL VALIDATION")

if df["reporting_level"].isna().any():
    fail("Reporting-level validation failed: missing reporting levels detected.")

levels = set(df["reporting_level"].unique())

if levels != EXPECTED_REPORTING_LEVELS:
    fail(
        "Unexpected reporting levels.\n"
        f"Expected: {EXPECTED_REPORTING_LEVELS}\n"
        f"Actual:   {levels}"
    )

print("Reporting-level validation passed.")
print(f"  Reporting levels: {len(levels)}")
print(df["reporting_level"].value_counts())


# =============================================================================
# 6. JURISDICTION VALIDATION
# =============================================================================

section("6. JURISDICTION VALIDATION")

province_values = set(
    df["province"]
    .dropna()
    .astype(str)
    .unique()
)

print(f"Province/territory values: {len(province_values)}")

print("\nProvince/territory values:")

for province in sorted(province_values):
    print(f"  - {province}")

if province_values != EXPECTED_PROVINCES:
    missing_provinces = EXPECTED_PROVINCES - province_values
    unexpected_provinces = province_values - EXPECTED_PROVINCES

    fail(
        "Province/territory validation failed.\n"
        f"Missing: {sorted(missing_provinces)}\n"
        f"Unexpected: {sorted(unexpected_provinces)}"
    )

print("Jurisdiction validation passed.")
print("All 13 Canadian provinces/territories are represented.")


# =============================================================================
# 7. NATIONAL JURISDICTION STRUCTURE
# =============================================================================

section("7. NATIONAL JURISDICTION STRUCTURE")

national = df[
    df["reporting_level"] == "National"
]

if len(national) == 0:
    fail("No National records found.")

national_provinces = set(
    national["province"]
    .dropna()
    .astype(str)
    .unique()
)

if national_provinces:
    fail(
        "National records should not contain province values.\n"
        f"Found: {sorted(national_provinces)}"
    )

national_regions = set(
    national["region"]
    .dropna()
    .astype(str)
    .unique()
)

if national_regions:
    fail(
        "National records should not contain region values.\n"
        f"Found: {sorted(national_regions)}"
    )

print("National jurisdiction structure validation passed.")
print(f"National records: {len(national)}")


# =============================================================================
# 8. PROVINCE/TERRITORY STRUCTURE
# =============================================================================

section("8. PROVINCE/TERRITORY STRUCTURE")

province_level = df[
    df["reporting_level"] == "Province/territory"
]

if len(province_level) == 0:
    fail("No Province/territory records found.")

province_level_regions = set(
    province_level["region"]
    .dropna()
    .astype(str)
    .unique()
)

if province_level_regions:
    fail(
        "Province/territory records should not contain region values.\n"
        f"Found: {sorted(province_level_regions)}"
    )

print("Province/territory structural validation passed.")
print(f"Province/territory records: {len(province_level)}")


# =============================================================================
# 9. HEALTH-REGION STRUCTURE
# =============================================================================

section("9. HEALTH-REGION STRUCTURE")

health_region = df[
    df["reporting_level"] == "Health region"
].copy()

print(f"Health-region records: {len(health_region)}")

# Standard health-region records should have a region value.
standard_health_region = health_region[
    ~health_region["place_or_organization"]
    .astype(str)
    .str.contains(
        r"\(Former\)",
        case=False,
        regex=True,
        na=False,
    )
]

missing_region = (
    standard_health_region["region"].isna()
    | standard_health_region["region"]
    .astype(str)
    .str.strip()
    .eq("")
).sum()

if missing_region != 0:
    fail(
        "Health-region records contain missing region values.\n"
        f"Missing region records among standard health regions: "
        f"{missing_region}"
    )

# Ontario former LHIN records are a legitimate historical structure.
former_lhin = health_region[
    health_region["place_or_organization"]
    .astype(str)
    .str.contains(
        r"\(Former\)",
        case=False,
        regex=True,
        na=False,
    )
]

former_lhin_missing_region = (
    former_lhin["region"].isna()
    | former_lhin["region"]
    .astype(str)
    .str.strip()
    .eq("")
).sum()

print(
    f"Standard health-region records: "
    f"{len(standard_health_region)}"
)

print(
    f"Former-LHIN health-region records: "
    f"{len(former_lhin)}"
)

print(
    f"Former-LHIN records with missing region: "
    f"{former_lhin_missing_region}"
)

# Validate that the historical exception is specifically Ontario.
non_ontario_former_lhin = former_lhin[
    former_lhin["province"] != "Ontario"
]

if len(non_ontario_former_lhin) != 0:
    fail(
        "Former-LHIN records found outside Ontario."
    )

# All missing-region records must belong to the former Ontario LHIN group.
all_health_region_missing = health_region[
    health_region["region"].isna()
    | health_region["region"]
    .astype(str)
    .str.strip()
    .eq("")
]

invalid_missing_region = all_health_region_missing[
    ~all_health_region_missing["place_or_organization"]
    .astype(str)
    .str.contains(
        r"\(Former\)",
        case=False,
        regex=True,
        na=False,
    )
]

if len(invalid_missing_region) != 0:
    fail(
        "Unexpected health-region records with missing region values.\n"
        f"Invalid records: {len(invalid_missing_region)}"
    )

print("Health-region structural validation passed.")
print(
    "Historical exception validated: Ontario former LHIN records "
    "may legitimately have missing region values."
)


# =============================================================================
# 10. METRIC VALIDATION
# =============================================================================

section("10. METRIC VALIDATION")

if df["metric"].isna().any():
    fail("Metric validation failed: missing metric values detected.")

metrics = set(df["metric"].unique())

if metrics != EXPECTED_METRICS:
    fail(
        "Unexpected metrics.\n"
        f"Expected: {EXPECTED_METRICS}\n"
        f"Actual:   {metrics}"
    )

print("Metric validation passed.")
print(df["metric"].value_counts())


# =============================================================================
# 11. REPORTING PERIOD / TIME SCALE VALIDATION
# =============================================================================

section("11. REPORTING PERIOD VALIDATION")

if df["time_scale"].isna().any():
    fail("Time-scale validation failed: missing time scale values.")

time_scales = set(
    df["time_scale"]
    .dropna()
    .astype(str)
    .unique()
)

if time_scales != {"Fiscal year"}:
    fail(
        "Unexpected time scale values.\n"
        f"Expected: {{'Fiscal year'}}\n"
        f"Actual:   {time_scales}"
    )

print("Reporting-period validation passed.")
print("Time scale: Fiscal year")


# =============================================================================
# 12. UNIT-OF-MEASUREMENT VALIDATION
# =============================================================================

section("12. UNIT-OF-MEASUREMENT VALIDATION")

number_cases = df[
    df["metric"] == "Number of cases"
]

benchmark_metric = df[
    df["metric"] == "Percentage of cases treated within benchmark"
]

invalid_number_cases = number_cases[
    number_cases["unit_of_measure"].notna()
]

if len(invalid_number_cases) != 0:
    fail(
        "Number-of-cases records contain unexpected units."
    )

invalid_percentage = benchmark_metric[
    benchmark_metric["unit_of_measure"].fillna("") != "Percent"
]

if len(invalid_percentage) != 0:
    fail(
        "Percentage-of-cases records contain unexpected units."
    )

print("Unit-of-measurement validation passed.")


# =============================================================================
# 13. DUPLICATE VALIDATION
# =============================================================================

section("13. DUPLICATE VALIDATION")

structural_columns = [
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
]

duplicate_count = df.duplicated(
    subset=structural_columns
).sum()

print(f"Duplicate structural records: {duplicate_count}")

if duplicate_count != 0:
    fail("Duplicate validation failed.")

print("Duplicate validation passed.")


# =============================================================================
# 14. INDICATOR-RESULT AVAILABILITY VALIDATION
# =============================================================================

section("14. INDICATOR-RESULT AVAILABILITY VALIDATION")

numeric_result = pd.to_numeric(
    df["indicator_result"],
    errors="coerce"
)

expected_available = numeric_result.notna()

actual_available = (
    df["indicator_result_available"]
    .astype(bool)
)

mismatch = (
    expected_available != actual_available
).sum()

print(
    f"Available indicator results: "
    f"{actual_available.sum()}"
)

print(
    f"Unavailable indicator results: "
    f"{(~actual_available).sum()}"
)

print(f"Availability mismatches: {mismatch}")

if mismatch != 0:
    fail(
        "Indicator-result availability validation failed."
    )

print("Indicator-result availability validation passed.")


# =============================================================================
# 15. BENCHMARK VALIDATION
# =============================================================================

section("15. BENCHMARK VALIDATION")

benchmark_mask = (
    df["metric"]
    == "Percentage of cases treated within benchmark"
)

benchmark_results = pd.to_numeric(
    df.loc[
        benchmark_mask,
        "indicator_result"
    ],
    errors="coerce"
)

benchmark_pct = pd.to_numeric(
    df.loc[
        benchmark_mask,
        "benchmark_pct"
    ],
    errors="coerce"
)

available_benchmark = benchmark_results.notna()

missing_benchmark_pct = (
    available_benchmark
    & benchmark_pct.isna()
).sum()

if missing_benchmark_pct != 0:
    fail(
        "Available benchmark results are missing benchmark_pct values."
    )

invalid_benchmark_range = (
    (benchmark_pct.dropna() < 0)
    | (benchmark_pct.dropna() > 100)
).any()

if invalid_benchmark_range:
    fail(
        "Benchmark percentage values outside 0–100 range detected."
    )

print(
    f"Benchmark records: "
    f"{benchmark_pct.notna().sum()}"
)

print("Benchmark validation passed.")


# =============================================================================
# 16. PROCEDURE VOLUME VALIDATION
# =============================================================================

section("16. PROCEDURE VOLUME VALIDATION")

volume_mask = (
    df["metric"]
    == "Number of cases"
)

volume_results = pd.to_numeric(
    df.loc[
        volume_mask,
        "indicator_result"
    ],
    errors="coerce"
)

procedure_volume = pd.to_numeric(
    df.loc[
        volume_mask,
        "procedure_volume"
    ],
    errors="coerce"
)

volume_mismatch = (
    volume_results.notna()
    & procedure_volume.isna()
).sum()

if volume_mismatch != 0:
    fail(
        "Available Number-of-cases records are missing "
        "procedure_volume."
    )

if (
    procedure_volume.dropna() < 0
).any():
    fail(
        "Negative procedure-volume values detected."
    )

print(
    f"Procedure-volume records: "
    f"{procedure_volume.notna().sum()}"
)

print("Procedure-volume validation passed.")


# =============================================================================
# 17. METRIC-RANGE VALIDATION
# =============================================================================

section("17. METRIC-RANGE VALIDATION")

percentage_results = pd.to_numeric(
    df.loc[
        df["metric"]
        == "Percentage of cases treated within benchmark",
        "indicator_result"
    ],
    errors="coerce"
)

if (
    percentage_results.dropna() < 0
).any() or (
    percentage_results.dropna() > 100
).any():
    fail(
        "Percentage-of-cases results outside 0–100 range detected."
    )

case_results = pd.to_numeric(
    df.loc[
        df["metric"] == "Number of cases",
        "indicator_result"
    ],
    errors="coerce"
)

if (
    case_results.dropna() < 0
).any():
    fail(
        "Negative Number-of-cases results detected."
    )

print("Metric-range validation passed.")


# =============================================================================
# 18. WAIT-TIME FIELD VALIDATION
# =============================================================================

section("18. WAIT-TIME FIELD VALIDATION")

wait_days = pd.to_numeric(
    df["wait_time_days"],
    errors="coerce"
)

wait_hours = pd.to_numeric(
    df["wait_time_hours"],
    errors="coerce"
)

if (
    wait_days.dropna() < 0
).any():
    fail(
        "Negative wait_time_days values detected."
    )

if (
    wait_hours.dropna() < 0
).any():
    fail(
        "Negative wait_time_hours values detected."
    )

print("Wait-time field validation passed.")

print(
    f"  Wait-time measures: "
    f"{df['wait_time_measure'].dropna().nunique()}"
)

print(
    f"  Wait-time days available: "
    f"{wait_days.notna().sum()}"
)

print(
    f"  Wait-time hours available: "
    f"{wait_hours.notna().sum()}"
)


# =============================================================================
# 19. MISSING-VALUE VALIDATION
# =============================================================================

section("19. MISSING-VALUE VALIDATION")

missing_summary = df.isna().sum()

print(missing_summary)


required_fields = [
    "place_or_organization",
    "reporting_level",
    "indicator",
    "measure_type",
    "indicator_segment",
    "segment_value",
    "time_scale",
    "time_frame",
    "reporting_year",
    "metric",
    "main_metric",
    "metric_value_raw",
    "indicator_result_available",
]

for column in required_fields:

    if df[column].isna().any():
        fail(
            f"Required field contains missing values: {column}"
        )


available_rows = (
    df["indicator_result_available"]
    .astype(bool)
)

if df.loc[
    available_rows,
    "indicator_result"
].isna().any():

    fail(
        "Available records contain missing indicator_result values."
    )


unavailable_rows = ~available_rows

if df.loc[
    unavailable_rows,
    "indicator_result"
].notna().any():

    fail(
        "Unavailable records contain indicator_result values."
    )

print("Structural missing-value validation passed.")


# =============================================================================
# 20. DATA-TYPE VALIDATION
# =============================================================================

section("20. DATA-TYPE VALIDATION")

numeric_columns = [
    "reporting_year",
    "indicator_result",
    "benchmark_pct",
    "procedure_volume",
    "wait_time_days",
    "wait_time_hours",
]

for column in numeric_columns:

    converted = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    invalid = (
        df[column].notna()
        & converted.isna()
    ).sum()

    if invalid != 0:
        fail(
            f"Non-numeric values found in numeric field: {column}"
        )

print("Data-type validation passed.")


# =============================================================================
# 21. STRUCTURAL UNIQUENESS VALIDATION
# =============================================================================

section("21. STRUCTURAL UNIQUENESS VALIDATION")

actual_combinations = len(
    df.drop_duplicates(
        subset=structural_columns
    )
)

print(
    f"Expected combinations: {EXPECTED_RECORDS}"
)

print(
    f"Actual combinations:   {actual_combinations}"
)

if actual_combinations != EXPECTED_RECORDS:
    fail(
        "Structural uniqueness validation failed."
    )

print("Structural uniqueness validation passed.")


# =============================================================================
# 22. OUTPUT ORDER VALIDATION
# =============================================================================

section("22. OUTPUT ORDER VALIDATION")

if list(df.columns) != EXPECTED_COLUMNS:
    fail(
        "Output column order validation failed."
    )

print("Output column order validation passed.")


# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 78)
print("CIHI JOINT REPLACEMENT WAIT TIMES VALIDATION COMPLETE")
print("=" * 78)

print("\nFINAL VALIDATION SUMMARY")

print(
    f"  Records:                 {len(df)}"
)

print(
    f"  Reporting years:         {len(years)}"
)

print(
    f"  Reporting levels:       {len(levels)}"
)

print(
    f"  Jurisdictions:           {len(province_values)}"
)

print(
    f"  Metrics:                 {len(metrics)}"
)

print(
    f"  Available results:       "
    f"{df['indicator_result_available'].astype(bool).sum()}"
)

print(
    f"  Unavailable results:     "
    f"{(~df['indicator_result_available'].astype(bool)).sum()}"
)

print(
    f"  Benchmark records:       "
    f"{df['benchmark_pct'].notna().sum()}"
)

print(
    f"  Volume records:          "
    f"{df['procedure_volume'].notna().sum()}"
)

print(
    f"  Health regions:          "
    f"{df.loc[df['reporting_level'] == 'Health region', 'region'].nunique()}"
)

print("\nReporting years:")
print(
    df["reporting_year"]
    .value_counts()
    .sort_index()
)

print("\nMetrics:")
print(
    df["metric"]
    .value_counts()
)

print("\nReporting levels:")
print(
    df["reporting_level"]
    .value_counts()
)

print("\nValidated file:")
print(INPUT_FILE)

print("\n" + "=" * 78)
print("VALIDATION PASSED")
print("=" * 78)