"""
inspect_cihi_wait_times.py

Purpose:
    Inspect the CIHI Wait Times for Priority Procedures workbook
    before cleaning and transformation.

Input:
    data/raw/access/cihi_wait_times_priority_procedures_2008_2025.xlsx

Output:
    Console inspection only.

Important:
    This script does NOT modify the raw workbook.
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
    / "raw"
    / "access"
    / "cihi_wait_times_priority_procedures_2008_2025.xlsx"
)


# ======================================================================
# 2. FILE CHECK
# ======================================================================

print("=" * 80)
print("CIHI WAIT TIMES — WORKBOOK INSPECTION")
print("=" * 80)

print("\n2. FILE CHECK")
print("-" * 80)

print(f"Input file:\n{INPUT_FILE}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )

file_size_bytes = INPUT_FILE.stat().st_size
file_size_mb = file_size_bytes / (1024 * 1024)

print(f"\nFile size: {file_size_mb:.2f} MB")
print("File exists: YES")


# ======================================================================
# 3. WORKBOOK SHEETS
# ======================================================================

print("\n3. WORKBOOK SHEETS")
print("-" * 80)

excel_file = pd.ExcelFile(INPUT_FILE)

print(f"\nNumber of worksheets: {len(excel_file.sheet_names)}")

for number, sheet_name in enumerate(
    excel_file.sheet_names,
    start=1
):
    print(f"  {number}. {sheet_name}")


# ======================================================================
# 4. SHEET-BY-SHEET INSPECTION
# ======================================================================

print("\n4. SHEET-BY-SHEET INSPECTION")
print("-" * 80)

for sheet_name in excel_file.sheet_names:

    print("\n" + "=" * 80)
    print(f"SHEET: {sheet_name}")
    print("=" * 80)

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    print(f"\nShape: {raw.shape}")

    print("\nFirst 15 rows:")

    print(
        raw.head(15).to_string(
            index=True,
            header=False
        )
    )

    print("\nLast 10 rows:")

    print(
        raw.tail(10).to_string(
            index=True,
            header=False
        )
    )


# ======================================================================
# 5. POTENTIAL DATA SHEET DETECTION
# ======================================================================

print("\n5. POTENTIAL DATA SHEET DETECTION")
print("-" * 80)

data_sheet_candidates = []

data_keywords = [
    "wait",
    "procedure",
    "province",
    "territory",
    "median",
    "90th",
    "percentile",
    "benchmark",
    "volume",
]


for sheet_name in excel_file.sheet_names:

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    sheet_text = " ".join(
        raw.astype(str)
        .fillna("")
        .values
        .flatten()
    ).lower()

    matches = [
        keyword
        for keyword in data_keywords
        if keyword in sheet_text
    ]

    if len(matches) >= 3:

        data_sheet_candidates.append(
            sheet_name
        )

        print(
            f"\nCandidate sheet: {sheet_name}"
        )

        print(
            f"  Matching concepts: "
            f"{', '.join(matches)}"
        )


if not data_sheet_candidates:

    print(
        "\nNo obvious data sheets detected."
    )


# ======================================================================
# 6. HEADER STRUCTURE DETECTION
# ======================================================================

print("\n6. HEADER STRUCTURE DETECTION")
print("-" * 80)

header_keywords = [
    "wait",
    "procedure",
    "province",
    "territory",
    "year",
    "fiscal",
    "median",
    "90th",
    "percentile",
    "benchmark",
    "volume",
]


for sheet_name in excel_file.sheet_names:

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    candidates = []

    for row_number in range(
        min(40, len(raw))
    ):

        row_values = (
            raw.iloc[row_number]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

        if not row_values:
            continue

        row_text = " | ".join(
            row_values
        ).lower()

        matches = [
            keyword
            for keyword in header_keywords
            if keyword in row_text
        ]

        if len(matches) >= 2:

            candidates.append(
                (
                    row_number,
                    matches,
                    row_values
                )
            )

    if candidates:

        print("\n" + "-" * 80)
        print(f"SHEET: {sheet_name}")
        print("-" * 80)

        for (
            row_number,
            matches,
            row_values
        ) in candidates:

            print(
                f"\nPossible header row: "
                f"{row_number}"
            )

            print(
                f"Detected concepts: "
                f"{', '.join(matches)}"
            )

            print("Values:")

            for index, value in enumerate(
                row_values
            ):

                print(
                    f"  {index}: {value}"
                )


# ======================================================================
# 7. COLUMN / DATA-TYPE INSPECTION
# ======================================================================

print("\n7. COLUMN / DATA-TYPE INSPECTION")
print("-" * 80)

for sheet_name in excel_file.sheet_names:

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    print("\n" + "-" * 80)
    print(f"SHEET: {sheet_name}")
    print("-" * 80)

    print("\nColumn statistics:")

    for column in raw.columns:

        non_null = raw[column].notna().sum()
        unique = raw[column].nunique(
            dropna=True
        )

        print(
            f"  Column {column}: "
            f"non-null={non_null}, "
            f"unique={unique}"
        )


# ======================================================================
# 8. POTENTIAL JURISDICTION DETECTION
# ======================================================================

print("\n8. POTENTIAL JURISDICTION DETECTION")
print("-" * 80)

canadian_jurisdictions = {
    "Canada",
    "Newfoundland and Labrador",
    "Prince Edward Island",
    "Nova Scotia",
    "New Brunswick",
    "Quebec",
    "Ontario",
    "Manitoba",
    "Saskatchewan",
    "Alberta",
    "British Columbia",
    "Yukon",
    "Northwest Territories",
    "Nunavut",
}


for sheet_name in excel_file.sheet_names:

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    found = set()

    for column in raw.columns:

        values = (
            raw[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        found.update(
            set(values).intersection(
                canadian_jurisdictions
            )
        )

    if found:

        print("\n" + "-" * 80)
        print(f"SHEET: {sheet_name}")
        print("-" * 80)

        print(
            f"\nJurisdictions detected: "
            f"{len(found)}"
        )

        for jurisdiction in sorted(found):

            print(
                f"  - {jurisdiction}"
            )


# ======================================================================
# 9. POTENTIAL PROCEDURE / CLINICAL CATEGORY DETECTION
# ======================================================================

print(
    "\n9. POTENTIAL PROCEDURE / CLINICAL CATEGORY DETECTION"
)
print("-" * 80)

procedure_keywords = [
    "hip",
    "knee",
    "cataract",
    "fracture",
    "radiation",
    "cancer",
    "ct",
    "mri",
    "cabg",
    "coronary",
]


for sheet_name in excel_file.sheet_names:

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    detected = set()

    for column in raw.columns:

        values = (
            raw[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        for value in values:

            value_lower = value.lower()

            if any(
                keyword in value_lower
                for keyword in procedure_keywords
            ):

                detected.add(value)

    if detected:

        print("\n" + "-" * 80)
        print(f"SHEET: {sheet_name}")
        print("-" * 80)

        print(
            f"\nPotential procedure/category "
            f"values detected: {len(detected)}"
        )

        for value in sorted(detected):

            print(
                f"  - {value}"
            )


# ======================================================================
# 10. WAIT-TIME MEASURE DETECTION
# ======================================================================

print("\n10. WAIT-TIME MEASURE DETECTION")
print("-" * 80)

measure_keywords = [
    "median",
    "90th percentile",
    "90th",
    "percentile",
    "wait time",
    "wait",
    "days",
    "volume",
    "benchmark",
    "within benchmark",
    "target",
]


for sheet_name in excel_file.sheet_names:

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    detected = set()

    for column in raw.columns:

        values = (
            raw[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        for value in values:

            value_lower = value.lower()

            for keyword in measure_keywords:

                if keyword in value_lower:

                    detected.add(value)

                    break

    if detected:

        print("\n" + "-" * 80)
        print(f"SHEET: {sheet_name}")
        print("-" * 80)

        print(
            f"\nPotential wait-time/measure "
            f"values: {len(detected)}"
        )

        for value in sorted(detected):

            print(
                f"  - {value}"
            )


# ======================================================================
# 11. FISCAL / REPORTING PERIOD DETECTION
# ======================================================================

print("\n11. FISCAL / REPORTING PERIOD DETECTION")
print("-" * 80)

year_keywords = [
    "2008",
    "2009",
    "2010",
    "2011",
    "2012",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
    "2025",
]


for sheet_name in excel_file.sheet_names:

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    detected_years = set()

    for column in raw.columns:

        values = (
            raw[column]
            .dropna()
            .astype(str)
        )

        for value in values:

            for year in year_keywords:

                if year in value:

                    detected_years.add(
                        year
                    )

    if detected_years:

        print("\n" + "-" * 80)
        print(f"SHEET: {sheet_name}")
        print("-" * 80)

        print(
            "\nYears detected:"
        )

        print(
            "  "
            + ", ".join(
                sorted(
                    detected_years,
                    key=int
                )
            )
        )


# ======================================================================
# 12. SUPPRESSION / MISSING-VALUE DETECTION
# ======================================================================

print("\n12. SUPPRESSION / MISSING-VALUE DETECTION")
print("-" * 80)

suppression_keywords = [
    "n/r",
    "n/a",
    "suppressed",
    "not available",
    "not reportable",
    "unstable",
    "under-reporting",
]


for sheet_name in excel_file.sheet_names:

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    detected = []

    for row_number in range(
        len(raw)
    ):

        row_text = " ".join(
            raw.iloc[row_number]
            .dropna()
            .astype(str)
            .tolist()
        )

        row_lower = row_text.lower()

        if any(
            keyword in row_lower
            for keyword in suppression_keywords
        ):

            detected.append(
                (
                    row_number,
                    row_text
                )
            )

    if detected:

        print("\n" + "-" * 80)
        print(f"SHEET: {sheet_name}")
        print("-" * 80)

        print(
            f"\nRows containing suppression/"
            f"availability terminology: "
            f"{len(detected)}"
        )

        for row_number, row_text in detected[:50]:

            print(
                f"\nRow {row_number}:"
            )

            print(
                f"  {row_text}"
            )


# ======================================================================
# 13. BENCHMARK / TARGET DETECTION
# ======================================================================

print("\n13. BENCHMARK / TARGET DETECTION")
print("-" * 80)

benchmark_keywords = [
    "benchmark",
    "target",
    "within",
    "recommended",
    "wait-time target",
]


for sheet_name in excel_file.sheet_names:

    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=None
    )

    detected = []

    for row_number in range(
        len(raw)
    ):

        row_text = " ".join(
            raw.iloc[row_number]
            .dropna()
            .astype(str)
            .tolist()
        )

        row_lower = row_text.lower()

        if any(
            keyword in row_lower
            for keyword in benchmark_keywords
        ):

            detected.append(
                (
                    row_number,
                    row_text
                )
            )

    if detected:

        print("\n" + "-" * 80)
        print(f"SHEET: {sheet_name}")
        print("-" * 80)

        print(
            f"\nBenchmark-related rows: "
            f"{len(detected)}"
        )

        for row_number, row_text in detected[:50]:

            print(
                f"\nRow {row_number}:"
            )

            print(
                f"  {row_text}"
            )


# ======================================================================
# 14. DUPLICATE / STRUCTURAL TEST
# ======================================================================

print("\n14. DUPLICATE / STRUCTURAL TEST")
print("-" * 80)

print(
    "\nThis section will be completed after "
    "the actual data table and header structure "
    "have been identified."
)

print(
    "\nNo assumptions are being made about the "
    "unique-key structure at this stage."
)


# ======================================================================
# 15. RAW DATA INTEGRITY CHECK
# ======================================================================

print("\n15. RAW DATA INTEGRITY CHECK")
print("-" * 80)

print(
    "\nWorkbook opened successfully."
)

print(
    "Raw workbook has not been modified."
)

print(
    "No cleaning or transformation was performed."
)


# ======================================================================
# 16. FINAL INSPECTION REPORT
# ======================================================================

print("\n16. FINAL INSPECTION REPORT")
print("-" * 80)

print(
    "\nThe workbook inspection is complete."
)

print(
    "\nThe next stage is to identify:"
)

print(
    "  1. The authoritative wait-time data sheet(s)"
)

print(
    "  2. The exact header row(s)"
)

print(
    "  3. The procedure/category dimension"
)

print(
    "  4. The jurisdiction dimension"
)

print(
    "  5. The reporting-period dimension"
)

print(
    "  6. Median wait-time measure"
)

print(
    "  7. 90th-percentile wait-time measure"
)

print(
    "  8. Procedure volume"
)

print(
    "  9. Benchmark/target information"
)

print(
    " 10. Suppression and missing-value rules"
)

print(
    "\nNo processed file has been created."
)


# ======================================================================
# 17. INSPECTION COMPLETE
# ======================================================================

print("\n" + "=" * 80)
print("CIHI WAIT TIMES INSPECTION COMPLETE")
print("=" * 80)

print(
    "\nRaw file preserved:"
)

print(
    INPUT_FILE
)

print(
    "\nProceed to cleaning only after reviewing "
    "this inspection output."
)

print("\n" + "=" * 80)