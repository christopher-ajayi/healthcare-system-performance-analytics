"""
clean_cihi_wait_times.py

Purpose:
    Clean CIHI Wait Times for Priority Procedures in Canada,
    2008 to 2025 — Table 1.

Input:
    data/raw/access/
        cihi_wait_times_priority_procedures_2008_2025.xlsx

Output:
    data/processed/access/
        cihi_wait_times_clean.csv

Authoritative source:
    CIHI — Wait Times for Priority Procedures in Canada,
    2008 to 2025 — Data Tables.

Table:
    Table 1

Core dimensions:
    - Reporting level
    - Province
    - Region
    - Indicator
    - Metric
    - Data year
    - Unit of measurement
    - Indicator result

Important methodological rules:
    1. The original CIHI Data year is preserved.
    2. Data year is NOT blindly converted to fiscal year.
    3. Standard reporting covers April to September.
    4. COVID-era FY and Q3Q4 reporting periods are retained.
    5. "n/a" is treated as unavailable, not zero.
    6. No artificial complete province × year × procedure
       structure is imposed.
    7. Regional records are retained.
    8. National and provincial records are retained.
"""

from pathlib import Path
import re
import pandas as pd


# ============================================================
# 1. CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "access"
    / "cihi_wait_times_priority_procedures_2008_2025.xlsx"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "access"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "cihi_wait_times_clean.csv"
)

SHEET_NAME = "Table 1"


# ============================================================
# 2. SOURCE COLUMN NAMES
# ============================================================

SOURCE_COLUMNS = [
    "Reporting level",
    "Province",
    "Region",
    "Indicator",
    "Metric",
    "Data year",
    "Unit of measurement",
    "Indicator result",
]


# ============================================================
# 3. EXPECTED DIMENSIONS
# ============================================================

EXPECTED_REPORTING_LEVELS = {
    "National",
    "Provincial",
    "Regional",
}

EXPECTED_METRICS = {
    "50th percentile",
    "90th percentile",
    "% meeting benchmark",
    "Volume",
}

EXPECTED_UNITS = {
    "Days",
    "Hours",
    "Proportion",
    "Number of cases",
}


EXPECTED_PROCEDURES = {
    "Bladder Cancer Surgery",
    "Breast Cancer Surgery",
    "CABG",
    "Cataract Surgery",
    "Colorectal Cancer Surgery",
    "CT Scan",
    "Hip Fracture Repair",
    "Hip Fracture Repair/Emergency and Inpatient",
    "Hip Replacement",
    "Knee Replacement",
    "Lung Cancer Surgery",
    "MRI Scan",
    "Prostate Cancer Surgery",
    "Radiation Therapy",
}


EXPECTED_PROVINCES = {
    "Alberta",
    "British Columbia",
    "Manitoba",
    "New Brunswick",
    "Newfoundland and Labrador",
    "Nova Scotia",
    "Ontario",
    "Prince Edward Island",
    "Quebec",
    "Saskatchewan",
    "Canada",
}


# ============================================================
# 4. REPORT HEADER
# ============================================================

print("=" * 75)
print("CIHI WAIT TIMES — CLEANING")
print("=" * 75)

print(f"\nInput file:")
print(INPUT_FILE)

print(f"\nSheet:")
print(SHEET_NAME)

print(f"\nOutput file:")
print(OUTPUT_FILE)


# ============================================================
# 5. FILE CHECK
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )


# ============================================================
# 6. LOAD TABLE 1
# ============================================================

df = pd.read_excel(
    INPUT_FILE,
    sheet_name=SHEET_NAME,
    header=1,
)

print(f"\nRaw shape: {df.shape}")


# ============================================================
# 7. NORMALIZE COLUMN NAMES
# ============================================================

df.columns = (
    pd.Index(df.columns)
    .astype(str)
    .str.replace("\n", " ", regex=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

print("\nDetected columns:")

for column in df.columns:
    print(f"  - {column}")


# ============================================================
# 8. COLUMN NAME NORMALIZATION
# ============================================================

column_mapping = {}

for column in df.columns:

    normalized = (
        str(column)
        .replace("\n", " ")
        .strip()
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    )

    if normalized == "Reporting level":
        column_mapping[column] = "Reporting level"

    elif normalized == "Province":
        column_mapping[column] = "Province"

    elif normalized == "Region":
        column_mapping[column] = "Region"

    elif normalized == "Indicator":
        column_mapping[column] = "Indicator"

    elif normalized == "Metric":
        column_mapping[column] = "Metric"

    elif normalized == "Data year":
        column_mapping[column] = "Data year"

    elif normalized == "Unit of measurement":
        column_mapping[column] = "Unit of measurement"

    elif normalized == "Indicator result":
        column_mapping[column] = "Indicator result"


df = df.rename(columns=column_mapping)


# ============================================================
# 9. REQUIRED COLUMN VALIDATION
# ============================================================

missing_columns = [
    column
    for column in SOURCE_COLUMNS
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "\nRequired Table 1 columns are missing:\n"
        + "\n".join(
            f"  - {column}"
            for column in missing_columns
        )
    )


print("\nRequired columns detected successfully.")


# ============================================================
# 10. SELECT AUTHORITATIVE DATA COLUMNS
# ============================================================

df = df[
    SOURCE_COLUMNS
].copy()


# ============================================================
# 11. REMOVE COMPLETELY EMPTY ROWS
# ============================================================

before_empty_removal = len(df)

df = df.dropna(
    how="all"
).copy()

removed_empty_rows = (
    before_empty_removal
    - len(df)
)

print(
    "\nCompletely empty rows removed:"
    f" {removed_empty_rows}"
)


# ============================================================
# 12. CLEAN TEXT FIELDS
# ============================================================

text_columns = [
    "Reporting level",
    "Province",
    "Region",
    "Indicator",
    "Metric",
    "Data year",
    "Unit of measurement",
]

for column in text_columns:

    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# ============================================================
# 13. REMOVE CIHI END-OF-WORKSHEET / NOTE ROWS
# ============================================================

# Valid data rows must have:
#   Reporting level
#   Indicator
#   Metric
#   Data year
#   Unit

data_mask = (
    df["Reporting level"].notna()
    & df["Indicator"].notna()
    & df["Metric"].notna()
    & df["Data year"].notna()
    & df["Unit of measurement"].notna()
)

non_data_rows = df.loc[
    ~data_mask
].copy()

print(
    "\nNon-data / note rows identified:"
    f" {len(non_data_rows)}"
)

df = df.loc[
    data_mask
].copy()


# ============================================================
# 14. NORMALIZE "n/a"
# ============================================================

NA_VALUES = {
    "n/a",
    "N/A",
    "na",
    "NA",
    "",
    "nan",
    "None",
}

for column in text_columns:

    df[column] = df[column].replace(
        list(NA_VALUES),
        pd.NA
    )


# ============================================================
# 15. INDICATOR RESULT CLEANING
# ============================================================

df["Indicator result_raw"] = (
    df["Indicator result"]
    .astype("string")
    .str.strip()
)

df["indicator_result_available"] = (
    df["Indicator result_raw"].notna()
    & ~df["Indicator result_raw"].isin(
        list(NA_VALUES)
    )
)


# ============================================================
# 16. CONVERT INDICATOR RESULT TO NUMERIC
# ============================================================

df["indicator_result"] = pd.to_numeric(
    df["Indicator result_raw"],
    errors="coerce"
)


# ============================================================
# 17. AVAILABILITY VALIDATION
# ============================================================

availability_conflict = (
    df["indicator_result_available"]
    != df["indicator_result"].notna()
)

if availability_conflict.any():

    conflict_rows = df.loc[
        availability_conflict,
        [
            "Reporting level",
            "Province",
            "Region",
            "Indicator",
            "Metric",
            "Data year",
            "Indicator result_raw",
            "indicator_result",
        ],
    ]

    print(
        "\nAvailability conflicts detected:"
    )

    print(
        conflict_rows.to_string(
            index=False
        )
    )

    raise ValueError(
        "Indicator-result availability conflict detected."
    )


# ============================================================
# 18. REPORTING LEVEL VALIDATION
# ============================================================

actual_reporting_levels = set(
    df["Reporting level"]
    .dropna()
    .unique()
)

unexpected_reporting_levels = (
    actual_reporting_levels
    - EXPECTED_REPORTING_LEVELS
)

if unexpected_reporting_levels:

    print(
        "\nUnexpected reporting levels:"
    )

    for value in sorted(
        unexpected_reporting_levels
    ):
        print(f"  - {value}")

    raise ValueError(
        "Unexpected reporting level detected."
    )

print(
    "\nReporting-level validation passed."
)


# ============================================================
# 19. METRIC VALIDATION
# ============================================================

actual_metrics = set(
    df["Metric"]
    .dropna()
    .unique()
)

unexpected_metrics = (
    actual_metrics
    - EXPECTED_METRICS
)

if unexpected_metrics:

    print(
        "\nUnexpected metrics:"
    )

    for value in sorted(
        unexpected_metrics
    ):
        print(f"  - {value}")

    raise ValueError(
        "Unexpected metric detected."
    )

print(
    "Metric validation passed."
)


# ============================================================
# 20. UNIT VALIDATION
# ============================================================

actual_units = set(
    df["Unit of measurement"]
    .dropna()
    .unique()
)

unexpected_units = (
    actual_units
    - EXPECTED_UNITS
)

if unexpected_units:

    print(
        "\nUnexpected units:"
    )

    for value in sorted(
        unexpected_units
    ):
        print(f"  - {value}")

    raise ValueError(
        "Unexpected unit of measurement detected."
    )

print(
    "Unit-of-measurement validation passed."
)


# ============================================================
# 21. PROCEDURE VALIDATION
# ============================================================

actual_indicators = set(
    df["Indicator"]
    .dropna()
    .unique()
)

unexpected_indicators = (
    actual_indicators
    - EXPECTED_PROCEDURES
)

if unexpected_indicators:

    print(
        "\nAdditional/unexpected indicators detected:"
    )

    for value in sorted(
        unexpected_indicators
    ):
        print(f"  - {value}")

    raise ValueError(
        "Unexpected procedure/indicator detected."
    )

print(
    "\nProcedure validation passed."
)

print(
    f"  Procedures detected: "
    f"{len(actual_indicators)}"
)


# ============================================================
# 22. DATA YEAR CLEANING
# ============================================================

df["data_year"] = (
    df["Data year"]
    .astype("string")
    .str.strip()
)


# ============================================================
# 23. REPORTING PERIOD TYPE
# ============================================================

def classify_reporting_period(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip()

    if value.endswith("FY"):
        return "FY"

    if value.endswith("Q3Q4"):
        return "Q3Q4"

    if re.fullmatch(
        r"\d{4}",
        value
    ):
        return "Apr-Sep"

    return "Other"


df["reporting_period_type"] = (
    df["data_year"]
    .apply(classify_reporting_period)
)


# ============================================================
# 24. REPORTING YEAR
# ============================================================

df["reporting_year"] = pd.to_numeric(
    df["data_year"]
    .astype("string")
    .str.extract(
        r"(\d{4})"
    )[0],
    errors="coerce"
).astype("Int64")


# ============================================================
# 25. DATA YEAR VALIDATION
# ============================================================

invalid_reporting_years = df.loc[
    ~df["reporting_year"].between(
        2008,
        2025
    ),
    [
        "data_year",
        "reporting_year",
    ],
]

if not invalid_reporting_years.empty:

    print(
        "\nInvalid reporting years detected:"
    )

    print(
        invalid_reporting_years
        .drop_duplicates()
        .to_string(index=False)
    )

    raise ValueError(
        "Reporting year outside expected "
        "2008–2025 range."
    )

print(
    "\nReporting-year validation passed."
)

print(
    f"  Minimum year: "
    f"{df['reporting_year'].min()}"
)

print(
    f"  Maximum year: "
    f"{df['reporting_year'].max()}"
)


# ============================================================
# 26. PROVINCE CLEANING
# ============================================================

df["province"] = (
    df["Province"]
    .astype("string")
    .str.strip()
)

df["region"] = (
    df["Region"]
    .astype("string")
    .str.strip()
)


# ============================================================
# 27. NATIONAL RECORD VALIDATION
# ============================================================

national_mask = (
    df["Reporting level"]
    == "National"
)

national_provinces = set(
    df.loc[
        national_mask,
        "province"
    ].dropna().unique()
)

if national_provinces and (
    national_provinces != {"Canada"}
):

    print(
        "\nUnexpected national-level province values:"
    )

    print(
        sorted(national_provinces)
    )

    raise ValueError(
        "National records must use Canada "
        "as the province."
    )


# ============================================================
# 28. PROVINCIAL RECORD VALIDATION
# ============================================================

provincial_mask = (
    df["Reporting level"]
    == "Provincial"
)

provincial_values = set(
    df.loc[
        provincial_mask,
        "province"
    ].dropna().unique()
)

unexpected_provinces = (
    provincial_values
    - (
        EXPECTED_PROVINCES
        - {"Canada"}
    )
)

if unexpected_provinces:

    print(
        "\nUnexpected provincial jurisdictions:"
    )

    for value in sorted(
        unexpected_provinces
    ):
        print(f"  - {value}")

    raise ValueError(
        "Unexpected provincial jurisdiction detected."
    )

print(
    "\nJurisdiction validation passed."
)


# ============================================================
# 29. REGION STRUCTURE VALIDATION
# ============================================================

# CIHI uses n/a for provincial/national rows
# where a regional value does not apply.

provincial_national_without_region = df.loc[
    df["Reporting level"].isin(
        [
            "National",
            "Provincial",
        ]
    )
    & df["region"].notna()
]

if not provincial_national_without_region.empty:

    print(
        "\nWarning:"
    )

    print(
        "Some national/provincial records contain "
        "a Region value."
    )

    print(
        provincial_national_without_region[
            [
                "Reporting level",
                "province",
                "region",
            ]
        ]
        .drop_duplicates()
        .head(20)
        .to_string(index=False)
    )

    print(
        "\nThese values are retained rather than "
        "silently deleted."
    )


# ============================================================
# 30. INDICATOR / METRIC COMPATIBILITY
# ============================================================

# Volume should use number of cases.
volume_unit_conflicts = df.loc[
    (
        df["Metric"] == "Volume"
    )
    & (
        df["Unit of measurement"]
        != "Number of cases"
    )
]

if not volume_unit_conflicts.empty:

    raise ValueError(
        "Volume records contain unexpected units."
    )


# Wait-time percentile metrics should be measured
# in Days or Hours.

percentile_mask = df["Metric"].isin(
    [
        "50th percentile",
        "90th percentile",
    ]
)

percentile_unit_conflicts = df.loc[
    percentile_mask
    & ~df["Unit of measurement"].isin(
        [
            "Days",
            "Hours",
        ]
    )
]

if not percentile_unit_conflicts.empty:

    raise ValueError(
        "Percentile wait-time records contain "
        "unexpected units."
    )


# Benchmark percentages should use proportions.

benchmark_mask = (
    df["Metric"]
    == "% meeting benchmark"
)

benchmark_unit_conflicts = df.loc[
    benchmark_mask
    & (
        df["Unit of measurement"]
        != "Proportion"
    )
]

if not benchmark_unit_conflicts.empty:

    raise ValueError(
        "Benchmark records contain unexpected units."
    )

print(
    "Metric/unit compatibility validation passed."
)


# ============================================================
# 31. NUMERIC RANGE VALIDATION
# ============================================================

available_results = df.loc[
    df["indicator_result"].notna(),
    "indicator_result"
]

if (available_results < 0).any():

    negative_rows = df.loc[
        df["indicator_result"] < 0
    ]

    print(
        "\nNegative indicator results detected:"
    )

    print(
        negative_rows[
            [
                "province",
                "region",
                "Indicator",
                "Metric",
                "data_year",
                "indicator_result",
            ]
        ]
        .to_string(index=False)
    )

    raise ValueError(
        "Negative wait-time indicator result detected."
    )


# Proportion should generally be 0–100 in the source
# representation, based on the observed CIHI table.

benchmark_values = df.loc[
    benchmark_mask,
    "indicator_result"
].dropna()

if not benchmark_values.empty:

    if (
        (benchmark_values < 0)
        | (benchmark_values > 100)
    ).any():

        raise ValueError(
            "Benchmark proportion outside 0–100 range."
        )


print(
    "Numeric-range validation passed."
)


# ============================================================
# 32. DUPLICATE VALIDATION
# ============================================================

key_columns = [
    "Reporting level",
    "province",
    "region",
    "Indicator",
    "Metric",
    "data_year",
    "Unit of measurement",
]

duplicate_mask = df.duplicated(
    subset=key_columns,
    keep=False,
)

duplicate_count = duplicate_mask.sum()

print(
    "\nDuplicate structural records:"
    f" {duplicate_count}"
)

if duplicate_count > 0:

    duplicates = df.loc[
        duplicate_mask
    ].sort_values(
        by=key_columns
    )

    print(
        "\nDuplicate records:"
    )

    print(
        duplicates.to_string(
            index=False
        )
    )

    raise ValueError(
        "Duplicate structural records detected."
    )

print(
    "Duplicate validation passed."
)


# ============================================================
# 33. MISSING RESULT SUMMARY
# ============================================================

missing_results = df[
    "indicator_result"
].isna().sum()

available_results_count = (
    df["indicator_result"]
    .notna()
    .sum()
)

print(
    "\nIndicator-result availability:"
)

print(
    f"  Available: "
    f"{available_results_count}"
)

print(
    f"  Unavailable: "
    f"{missing_results}"
)


# ============================================================
# 34. MISSING RESULTS BY METRIC
# ============================================================

print(
    "\nUnavailable results by metric:"
)

missing_by_metric = (
    df.loc[
        df["indicator_result"].isna()
    ]
    .groupby(
        "Metric"
    )
    .size()
    .sort_values(
        ascending=False
    )
)

if missing_by_metric.empty:

    print(
        "  None"
    )

else:

    print(
        missing_by_metric.to_string()
    )


# ============================================================
# 35. DATASET STRUCTURE SUMMARY
# ============================================================

print(
    "\nDataset structure:"
)

print(
    f"  Records: "
    f"{len(df)}"
)

print(
    f"  Reporting levels: "
    f"{df['Reporting level'].nunique()}"
)

print(
    f"  Provinces: "
    f"{df['province'].nunique(dropna=True)}"
)

print(
    f"  Regions: "
    f"{df['region'].nunique(dropna=True)}"
)

print(
    f"  Procedures: "
    f"{df['Indicator'].nunique()}"
)

print(
    f"  Metrics: "
    f"{df['Metric'].nunique()}"
)

print(
    f"  Reporting years: "
    f"{df['reporting_year'].nunique()}"
)


# ============================================================
# 36. REPORTING PERIOD SUMMARY
# ============================================================

print(
    "\nReporting-period types:"
)

print(
    df["reporting_period_type"]
    .value_counts(
        dropna=False
    )
    .to_string()
)


# ============================================================
# 37. PROCEDURE SUMMARY
# ============================================================

print(
    "\nProcedures:"
)

for procedure in sorted(
    df["Indicator"]
    .dropna()
    .unique()
):

    print(
        f"  - {procedure}"
    )


# ============================================================
# 38. METRIC SUMMARY
# ============================================================

print(
    "\nMetrics:"
)

for metric in sorted(
    df["Metric"]
    .dropna()
    .unique()
):

    count = (
        df["Metric"]
        == metric
    ).sum()

    print(
        f"  - {metric}: {count}"
    )


# ============================================================
# 39. STANDARDIZED OUTPUT COLUMN NAMES
# ============================================================

df = df.rename(
    columns={
        "Reporting level":
            "reporting_level",

        "Indicator":
            "indicator",

        "Metric":
            "metric",

        "Unit of measurement":
            "unit_of_measurement",

        "Indicator result":
            "indicator_result_raw",
    }
)


# ============================================================
# 40. REMOVE RAW DUPLICATE RESULT COLUMN
# ============================================================

# indicator_result_raw currently contains the original
# string representation. Preserve it under a clearer name.

df = df.rename(
    columns={
        "indicator_result_raw":
            "indicator_result_source"
    }
)


# ============================================================
# 41. FINAL COLUMN ORDER
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
]

df = df[
    final_columns
].copy()


# ============================================================
# 42. FINAL SORT
# ============================================================

reporting_level_order = {
    "National": 1,
    "Provincial": 2,
    "Regional": 3,
}

df["_reporting_level_order"] = (
    df["reporting_level"]
    .map(reporting_level_order)
)

df = df.sort_values(
    by=[
        "reporting_year",
        "_reporting_level_order",
        "province",
        "region",
        "indicator",
        "metric",
    ],
    na_position="last",
).drop(
    columns="_reporting_level_order"
).reset_index(
    drop=True
)


# ============================================================
# 43. FINAL DATA TYPE VALIDATION
# ============================================================

if not pd.api.types.is_numeric_dtype(
    df["indicator_result"]
):

    raise TypeError(
        "indicator_result is not numeric."
    )

if not pd.api.types.is_numeric_dtype(
    df["reporting_year"]
):

    raise TypeError(
        "reporting_year is not numeric."
    )


# ============================================================
# 44. FINAL MISSING-VALUE CHECK
# ============================================================

print(
    "\nFinal missing-value summary:"
)

print(
    df.isna()
    .sum()
    .to_string()
)


# ============================================================
# 45. FINAL STRUCTURAL CHECK
# ============================================================

if len(df) == 0:

    raise ValueError(
        "Cleaning produced zero records."
    )

if df["indicator"].isna().any():

    raise ValueError(
        "Missing indicator values remain."
    )

if df["metric"].isna().any():

    raise ValueError(
        "Missing metric values remain."
    )

if df["reporting_year"].isna().any():

    raise ValueError(
        "Missing reporting years remain."
    )


# ============================================================
# 46. OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 47. SAVE CLEAN DATA
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 48. FINAL REPORT
# ============================================================

print(
    "\n"
    + "=" * 75
)

print(
    "CIHI WAIT TIMES CLEANING COMPLETE"
)

print(
    "=" * 75
)

print(
    f"\nFinal shape: "
    f"{df.shape}"
)

print(
    "\nFinal columns:"
)

for column in df.columns:

    print(
        f"  - {column}"
    )

print(
    "\nReporting years:"
)

print(
    f"  {df['reporting_year'].min()}"
    f" → "
    f"{df['reporting_year'].max()}"
)

print(
    "\nReporting levels:"
)

print(
    df["reporting_level"]
    .value_counts()
    .to_string()
)

print(
    "\nProcedures:"
)

print(
    df["indicator"]
    .nunique()
)

print(
    "\nMetrics:"
)

print(
    df["metric"]
    .value_counts()
    .to_string()
)

print(
    "\nAvailable indicator results:"
)

print(
    df["indicator_result_available"]
    .value_counts()
    .to_string()
)

print(
    "\nOutput file:"
)

print(
    OUTPUT_FILE
)

print(
    "\n"
    + "=" * 75
)

print(
    "CLEANING COMPLETE"
)

print(
    "=" * 75
)