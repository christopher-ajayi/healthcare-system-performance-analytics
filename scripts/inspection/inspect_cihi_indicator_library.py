"""
========================================================================
CIHI INDICATOR LIBRARY — RAW DATA INSPECTION
========================================================================

Purpose:
    Inspect the raw CIHI Indicator Library workbook before cleaning.

This script:
    1. Locates and opens the raw workbook
    2. Lists all worksheets
    3. Inspects sheet dimensions
    4. Displays first and last rows
    5. Detects likely header structures
    6. Inspects columns and data types
    7. Detects indicator names/categories
    8. Detects jurisdictions and reporting levels
    9. Detects reporting years/periods
   10. Detects units and result fields
   11. Detects missing/suppressed values
   12. Detects potential outcome/performance indicators
   13. Performs a raw-data integrity check

IMPORTANT:
    This script DOES NOT modify the raw workbook.
    No cleaning or transformation is performed.
========================================================================
"""

from pathlib import Path
import re
import sys

import pandas as pd


# ============================================================================
# 1. PROJECT PATHS
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


# ============================================================================
# 2. DISPLAY SETTINGS
# ============================================================================

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 220)
pd.set_option("display.max_colwidth", 100)
pd.set_option("display.max_rows", 100)


# ============================================================================
# 3. HELPER FUNCTIONS
# ============================================================================

def print_separator(char="=", length=80):
    print(char * length)


def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def detect_matching_columns(columns, keywords):
    """
    Return columns whose names contain any of the supplied keywords.
    """
    matches = []

    for column in columns:
        column_text = str(column).lower()

        if any(keyword.lower() in column_text for keyword in keywords):
            matches.append(column)

    return matches


def detect_years(df):
    """
    Detect years appearing anywhere in the dataframe.
    """
    years = set()

    for column in df.columns:
        series = df[column].dropna().astype(str)

        for value in series:
            matches = re.findall(r"\b(19\d{2}|20\d{2})\b", value)

            for year in matches:
                years.add(int(year))

    return sorted(years)


def print_value_summary(df, column, top_n=20):
    """
    Print unique-value summary for a column.
    """
    if column not in df.columns:
        return

    print(f"\nColumn: {column}")
    print(f"  Non-null: {df[column].notna().sum():,}")
    print(f"  Unique:   {df[column].nunique(dropna=True):,}")

    values = (
        df[column]
        .value_counts(dropna=False)
        .head(top_n)
    )

    print(values.to_string())


# ============================================================================
# 4. START
# ============================================================================

print_separator()

print("CIHI INDICATOR LIBRARY — RAW DATA INSPECTION")

print_separator()

print("\nInput file:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    print("\nERROR: Input workbook was not found.")
    print("\nExpected location:")
    print(INPUT_FILE)
    sys.exit(1)

print("\nWorkbook found successfully.")


# ============================================================================
# 5. WORKBOOK STRUCTURE
# ============================================================================

print("\n5. WORKBOOK STRUCTURE")
print("-" * 80)

try:
    excel_file = pd.ExcelFile(INPUT_FILE)
except Exception as exc:
    print("\nERROR: Unable to open workbook.")
    print(exc)
    sys.exit(1)

sheet_names = excel_file.sheet_names

print(f"\nNumber of worksheets: {len(sheet_names)}")

print("\nWorksheets:")

for i, sheet in enumerate(sheet_names, start=1):
    print(f"  {i}. {sheet}")


# ============================================================================
# 6. SHEET DIMENSIONS
# ============================================================================

print("\n6. SHEET DIMENSIONS")
print("-" * 80)

sheet_data = {}

for sheet in sheet_names:

    try:
        df = pd.read_excel(
            INPUT_FILE,
            sheet_name=sheet,
            header=None
        )

        sheet_data[sheet] = df

        print(f"\nSHEET: {sheet}")
        print(f"  Rows:    {df.shape[0]:,}")
        print(f"  Columns: {df.shape[1]:,}")

    except Exception as exc:

        print(f"\nSHEET: {sheet}")
        print(f"  ERROR reading sheet: {exc}")


# ============================================================================
# 7. RAW SHEET PREVIEW
# ============================================================================

print("\n7. RAW SHEET PREVIEW")
print("-" * 80)

for sheet, df in sheet_data.items():

    print("\n" + "=" * 80)
    print(f"SHEET: {sheet}")
    print("=" * 80)

    print("\nFirst 10 rows:")

    print(
        df.head(10).to_string(
            index=True,
            header=False
        )
    )

    print("\nLast 10 rows:")

    print(
        df.tail(10).to_string(
            index=True,
            header=False
        )
    )


# ============================================================================
# 8. HEADER STRUCTURE DETECTION
# ============================================================================

print("\n8. HEADER STRUCTURE DETECTION")
print("-" * 80)

header_keywords = [
    "indicator",
    "indicator name",
    "indicator title",
    "measure",
    "result",
    "value",
    "province",
    "territory",
    "jurisdiction",
    "reporting level",
    "year",
    "period",
    "unit",
    "organization",
    "region",
    "breakdown",
]

for sheet, df in sheet_data.items():

    print("\n" + "-" * 80)
    print(f"SHEET: {sheet}")
    print("-" * 80)

    candidate_rows = []

    scan_limit = min(30, len(df))

    for row_number in range(scan_limit):

        row_values = df.iloc[row_number].fillna("").astype(str)

        combined = " | ".join(row_values.tolist()).lower()

        matches = [
            keyword
            for keyword in header_keywords
            if keyword in combined
        ]

        if len(matches) >= 2:

            candidate_rows.append(
                (
                    row_number,
                    matches,
                    row_values.tolist()
                )
            )

    if not candidate_rows:

        print("No obvious header row detected.")

    else:

        for row_number, matches, values in candidate_rows:

            print(f"\nPossible header row: {row_number}")
            print(
                "Detected concepts: "
                + ", ".join(sorted(set(matches)))
            )

            non_empty = [
                f"{i}: {value}"
                for i, value in enumerate(values)
                if str(value).strip()
            ]

            for value in non_empty[:20]:
                print(f"  {value}")


# ============================================================================
# 9. POTENTIAL DATA SHEET DETECTION
# ============================================================================

print("\n9. POTENTIAL DATA SHEET DETECTION")
print("-" * 80)

data_keywords = [
    "indicator",
    "result",
    "value",
    "province",
    "territory",
    "year",
    "period",
]

for sheet, df in sheet_data.items():

    text = df.astype(str).fillna("").to_string().lower()

    matches = [
        keyword
        for keyword in data_keywords
        if keyword in text
    ]

    if len(matches) >= 3:

        print(f"\nCandidate data sheet: {sheet}")
        print(
            "  Matching concepts: "
            + ", ".join(matches)
        )


# ============================================================================
# 10. COLUMN / DATA-TYPE INSPECTION
# ============================================================================

print("\n10. COLUMN / DATA-TYPE INSPECTION")
print("-" * 80)

for sheet, raw_df in sheet_data.items():

    print("\n" + "-" * 80)
    print(f"SHEET: {sheet}")
    print("-" * 80)

    # Try several likely header rows.
    header_candidates = []

    for row_number in range(min(20, len(raw_df))):

        row = raw_df.iloc[row_number].fillna("").astype(str)

        matches = sum(
            1
            for keyword in header_keywords
            if any(
                keyword.lower() in value.lower()
                for value in row
            )
        )

        if matches >= 3:
            header_candidates.append(
                (row_number, matches)
            )

    if not header_candidates:

        print("No suitable header candidate identified.")
        continue

    header_row = max(
        header_candidates,
        key=lambda x: x[1]
    )[0]

    try:

        df = pd.read_excel(
            INPUT_FILE,
            sheet_name=sheet,
            header=header_row
        )

    except Exception:

        continue

    print(f"\nSelected inspection header row: {header_row}")

    print("\nDetected columns:")

    for i, column in enumerate(df.columns):

        print(
            f"  {i}: {column}"
            f" | dtype={df[column].dtype}"
            f" | non-null={df[column].notna().sum():,}"
            f" | unique={df[column].nunique(dropna=True):,}"
        )


# ============================================================================
# 11. INDICATOR DETECTION
# ============================================================================

print("\n11. INDICATOR DETECTION")
print("-" * 80)

indicator_keywords = [
    "indicator",
    "indicator name",
    "indicator title",
    "measure",
]

for sheet, raw_df in sheet_data.items():

    header_candidates = []

    for row_number in range(min(20, len(raw_df))):

        row = raw_df.iloc[row_number].fillna("").astype(str)

        matches = sum(
            1
            for keyword in indicator_keywords
            if any(
                keyword.lower() in value.lower()
                for value in row
            )
        )

        if matches:
            header_candidates.append(
                (row_number, matches)
            )

    if not header_candidates:
        continue

    header_row = max(
        header_candidates,
        key=lambda x: x[1]
    )[0]

    try:

        df = pd.read_excel(
            INPUT_FILE,
            sheet_name=sheet,
            header=header_row
        )

    except Exception:

        continue

    indicator_columns = detect_matching_columns(
        df.columns,
        [
            "indicator",
            "measure"
        ]
    )

    if not indicator_columns:
        continue

    print("\n" + "-" * 80)
    print(f"SHEET: {sheet}")
    print("-" * 80)

    for column in indicator_columns:

        print_value_summary(
            df,
            column,
            top_n=50
        )


# ============================================================================
# 12. JURISDICTION / REPORTING-LEVEL DETECTION
# ============================================================================

print("\n12. JURISDICTION / REPORTING-LEVEL DETECTION")
print("-" * 80)

jurisdiction_keywords = [
    "province",
    "territory",
    "jurisdiction",
    "place",
    "region",
    "organization",
]

reporting_keywords = [
    "reporting level",
    "level",
]

for sheet, raw_df in sheet_data.items():

    header_candidates = []

    for row_number in range(min(20, len(raw_df))):

        row = raw_df.iloc[row_number].fillna("").astype(str)

        matches = sum(
            1
            for keyword in jurisdiction_keywords + reporting_keywords
            if any(
                keyword.lower() in value.lower()
                for value in row
            )
        )

        if matches >= 2:
            header_candidates.append(
                (row_number, matches)
            )

    if not header_candidates:
        continue

    header_row = max(
        header_candidates,
        key=lambda x: x[1]
    )[0]

    try:

        df = pd.read_excel(
            INPUT_FILE,
            sheet_name=sheet,
            header=header_row
        )

    except Exception:

        continue

    jurisdiction_columns = detect_matching_columns(
        df.columns,
        jurisdiction_keywords
    )

    reporting_columns = detect_matching_columns(
        df.columns,
        reporting_keywords
    )

    if jurisdiction_columns or reporting_columns:

        print("\n" + "-" * 80)
        print(f"SHEET: {sheet}")
        print("-" * 80)

    for column in jurisdiction_columns:

        print_value_summary(
            df,
            column,
            top_n=30
        )

    for column in reporting_columns:

        print_value_summary(
            df,
            column,
            top_n=20
        )


# ============================================================================
# 13. REPORTING YEAR / PERIOD DETECTION
# ============================================================================

print("\n13. REPORTING YEAR / PERIOD DETECTION")
print("-" * 80)

for sheet, raw_df in sheet_data.items():

    header_candidates = []

    for row_number in range(min(20, len(raw_df))):

        row = raw_df.iloc[row_number].fillna("").astype(str)

        combined = " | ".join(row.tolist()).lower()

        if "year" in combined or "period" in combined:

            header_candidates.append(row_number)

    if not header_candidates:
        continue

    header_row = header_candidates[0]

    try:

        df = pd.read_excel(
            INPUT_FILE,
            sheet_name=sheet,
            header=header_row
        )

    except Exception:

        continue

    year_columns = detect_matching_columns(
        df.columns,
        [
            "year",
            "period",
            "date",
            "fiscal"
        ]
    )

    if not year_columns:
        continue

    print("\n" + "-" * 80)
    print(f"SHEET: {sheet}")
    print("-" * 80)

    for column in year_columns:

        print_value_summary(
            df,
            column,
            top_n=40
        )

    detected_years = detect_years(df)

    if detected_years:

        print("\nYears detected:")

        print(
            "  "
            + ", ".join(
                str(year)
                for year in detected_years
            )
        )


# ============================================================================
# 14. UNIT / RESULT FIELD DETECTION
# ============================================================================

print("\n14. UNIT / RESULT FIELD DETECTION")
print("-" * 80)

unit_keywords = [
    "unit",
    "measure",
]

result_keywords = [
    "result",
    "value",
    "rate",
    "percentage",
    "percent",
    "numerator",
    "denominator",
]

for sheet, raw_df in sheet_data.items():

    header_candidates = []

    for row_number in range(min(20, len(raw_df))):

        row = raw_df.iloc[row_number].fillna("").astype(str)

        combined = " | ".join(row.tolist()).lower()

        matches = sum(
            keyword in combined
            for keyword in unit_keywords + result_keywords
        )

        if matches >= 2:

            header_candidates.append(
                (row_number, matches)
            )

    if not header_candidates:
        continue

    header_row = max(
        header_candidates,
        key=lambda x: x[1]
    )[0]

    try:

        df = pd.read_excel(
            INPUT_FILE,
            sheet_name=sheet,
            header=header_row
        )

    except Exception:

        continue

    columns = detect_matching_columns(
        df.columns,
        unit_keywords + result_keywords
    )

    if not columns:
        continue

    print("\n" + "-" * 80)
    print(f"SHEET: {sheet}")
    print("-" * 80)

    for column in columns:

        print_value_summary(
            df,
            column,
            top_n=30
        )


# ============================================================================
# 15. POTENTIAL OUTCOME / PERFORMANCE INDICATOR DETECTION
# ============================================================================

print("\n15. POTENTIAL OUTCOME / PERFORMANCE INDICATOR DETECTION")
print("-" * 80)

performance_terms = [
    "mortality",
    "readmission",
    "readmitted",
    "hospitalization",
    "hospitalisation",
    "complication",
    "adverse",
    "safety",
    "avoidable",
    "appropriate",
    "effectiveness",
    "outcome",
    "length of stay",
    "resource use",
    "occupancy",
    "emergency department",
    "surgical",
    "stroke",
    "myocardial infarction",
    "infection",
    "pressure injury",
    "fall",
    "harm",
]

for sheet, raw_df in sheet_data.items():

    header_candidates = []

    for row_number in range(min(20, len(raw_df))):

        row = raw_df.iloc[row_number].fillna("").astype(str)

        if any(
            "indicator" in value.lower()
            or "measure" in value.lower()
            for value in row
        ):

            header_candidates.append(row_number)

    if not header_candidates:
        continue

    header_row = header_candidates[0]

    try:

        df = pd.read_excel(
            INPUT_FILE,
            sheet_name=sheet,
            header=header_row
        )

    except Exception:

        continue

    indicator_columns = detect_matching_columns(
        df.columns,
        [
            "indicator",
            "measure",
            "title",
            "name"
        ]
    )

    if not indicator_columns:
        continue

    for column in indicator_columns:

        values = (
            df[column]
            .dropna()
            .astype(str)
            .drop_duplicates()
        )

        matches = []

        for value in values:

            value_lower = value.lower()

            if any(
                term in value_lower
                for term in performance_terms
            ):

                matches.append(value)

        if matches:

            print("\n" + "-" * 80)
            print(f"SHEET: {sheet}")
            print(f"Column: {column}")
            print("-" * 80)

            print(
                f"Potential performance/outcome indicators: "
                f"{len(matches)}"
            )

            for value in matches[:100]:

                print(f"  - {value}")


# ============================================================================
# 16. MISSING / SUPPRESSION DETECTION
# ============================================================================

print("\n16. MISSING / SUPPRESSION DETECTION")
print("-" * 80)

suppression_terms = [
    "n/a",
    "na",
    "not available",
    "suppressed",
    "suppression",
    "not applicable",
    "missing",
    "confidential",
    "*",
]

for sheet, raw_df in sheet_data.items():

    print("\n" + "-" * 80)
    print(f"SHEET: {sheet}")
    print("-" * 80)

    found = False

    for column in raw_df.columns:

        series = raw_df[column].dropna().astype(str)

        matches = series[
            series.str.lower().apply(
                lambda value: any(
                    term in value
                    for term in suppression_terms
                )
            )
        ]

        if len(matches) > 0:

            found = True

            print(
                f"\nColumn: {column}"
                f" | Matching cells: {len(matches):,}"
            )

            print(
                matches.head(20).to_string(
                    index=False
                )
            )

    if not found:

        print("No obvious suppression/missing terminology detected.")


# ============================================================================
# 17. DUPLICATE / STRUCTURAL TEST
# ============================================================================

print("\n17. DUPLICATE / STRUCTURAL TEST")
print("-" * 80)

print(
    """
No assumptions are being made about the final unique-key structure.

The unique key will be determined after the authoritative data sheet,
columns and dimensions have been identified.

No records are modified or removed during inspection.
"""
)


# ============================================================================
# 18. RAW DATA INTEGRITY CHECK
# ============================================================================

print("\n18. RAW DATA INTEGRITY CHECK")
print("-" * 80)

print("Workbook opened successfully.")
print("All worksheets were read for inspection.")
print("Raw workbook has not been modified.")
print("No cleaning or transformation was performed.")


# ============================================================================
# 19. FINAL INSPECTION REPORT
# ============================================================================

print("\n19. FINAL INSPECTION REPORT")
print("-" * 80)

print(
    """
The CIHI Indicator Library workbook inspection is complete.

The next stage is to identify:

  1. The authoritative data sheet
  2. The exact header row
  3. The indicator dimension
  4. The indicator category/domain
  5. The jurisdiction dimension
  6. The reporting-level dimension
  7. The reporting-period dimension
  8. The result/value field
  9. The unit of measurement
 10. Breakdown dimensions
 11. Suppression and missing-value rules
 12. Indicators appropriate for the Outcomes / Performance section

No processed file has been created.

Proceed to cleaning only after reviewing this inspection output.
"""
)

print_separator()

print("CIHI INDICATOR LIBRARY INSPECTION COMPLETE")

print_separator()

print("\nRaw file preserved:")
print(INPUT_FILE)

print("\nNo cleaning or transformation was performed.")

print_separator()