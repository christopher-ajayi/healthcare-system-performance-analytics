from pathlib import Path
import pandas as pd


# ============================================================
# CIHI — 30-DAY HOSPITAL READMISSION
# RAW DATA QUALITY ASSESSMENT
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

EXPECTED_INDICATOR = "All Patients Readmitted to Hospital"

EXPECTED_YEARS = [
    "2020–2021",
    "2021–2022",
    "2022–2023",
    "2023–2024",
    "2024–2025",
]


# ============================================================
# 2. LOAD DATA
# ============================================================

def load_data():

    df = pd.read_csv(
        INPUT_FILE,
        dtype=str
    )

    return df


# ============================================================
# 3. FILE VALIDATION
# ============================================================

def validate_file(df):

    print("=" * 75)
    print("CIHI — 30-DAY HOSPITAL READMISSION")
    print("RAW DATA QUALITY ASSESSMENT")
    print("=" * 75)

    print("\n[1] FILE VALIDATION")

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    if len(df) == 3628 and len(df.columns) == 33:
        print("PASS — expected dimensions confirmed.")
    else:
        print("REVIEW — dimensions differ from acquisition output.")


# ============================================================
# 4. INDICATOR VALIDATION
# ============================================================

def validate_indicator(df):

    print("\n[2] INDICATOR VALIDATION")

    counts = df["Indicator"].value_counts(dropna=False)

    print(counts.to_string())

    if (
        len(counts) == 1
        and counts.index[0] == EXPECTED_INDICATOR
    ):
        print("PASS — single expected indicator.")
    else:
        print("FAIL — unexpected indicator values found.")


# ============================================================
# 5. DUPLICATE VALIDATION
# ============================================================

def validate_duplicates(df):

    print("\n[3] DUPLICATE VALIDATION")

    duplicates = df.duplicated().sum()

    print(
        f"Exact duplicate rows: {duplicates:,}"
    )

    if duplicates == 0:
        print("PASS — no exact duplicate rows.")
    else:
        print("REVIEW — exact duplicate rows detected.")


# ============================================================
# 6. TIME VALIDATION
# ============================================================

def validate_time(df):

    print("\n[4] TIME VALIDATION")

    actual_years = sorted(
        df["Time frame"]
        .dropna()
        .unique()
    )

    print("Actual periods:")

    for year in actual_years:
        print(f"  {year}")

    if set(actual_years) == set(EXPECTED_YEARS):
        print("PASS — expected five fiscal-year periods confirmed.")
    else:
        print("FAIL — unexpected fiscal-year coverage.")


# ============================================================
# 7. MAIN METRIC VALIDATION
# ============================================================

def validate_main_metric(df):

    print("\n[5] MAIN METRIC VALIDATION")

    main = df[
        df["Main metric"].eq("Yes")
    ].copy()

    print(
        f"Main metric records: {len(main):,}"
    )

    print("\nMetric:")
    print(
        main["Metric"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nUnit:")
    print(
        main["Unit of measure"]
        .value_counts(dropna=False)
        .to_string()
    )

    if (
        main["Metric"].eq("Risk-adjusted rate").all()
        and main["Unit of measure"].eq("Per 100").all()
    ):
        print(
            "PASS — main metric is risk-adjusted rate "
            "(per 100)."
        )
    else:
        print(
            "FAIL — unexpected main metric or unit."
        )


# ============================================================
# 8. SUPPORTING METRICS
# ============================================================

def validate_supporting_metrics(df):

    print("\n[6] SUPPORTING METRICS")

    supporting = df[
        df["Main metric"].ne("Yes")
    ]

    print(
        supporting["Metric"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 9. SUPPRESSION ASSESSMENT
# ============================================================

def validate_suppression(df):

    print("\n[7] SUPPRESSION ASSESSMENT")

    main = df[
        df["Main metric"].eq("Yes")
    ].copy()

    suppressed = (
        main["Metric value"]
        .eq("Suppressed")
    )

    print(
        f"Suppressed metric values: "
        f"{suppressed.sum():,}"
    )

    print(
        f"Non-suppressed metric values: "
        f"{(~suppressed).sum():,}"
    )


# ============================================================
# 10. CONFIDENCE INTERVAL ASSESSMENT
# ============================================================

def validate_confidence_intervals(df):

    print("\n[8] CONFIDENCE INTERVAL ASSESSMENT")

    main = df[
        df["Main metric"].eq("Yes")
    ].copy()

    lower_suppressed = (
        main["Confidence interval lower limit"]
        .eq("Suppressed")
    )

    upper_suppressed = (
        main["Confidence interval upper limit"]
        .eq("Suppressed")
    )

    print(
        "Confidence interval lower limit: "
        f"{lower_suppressed.sum():,} suppressed"
    )

    print(
        "Confidence interval upper limit: "
        f"{upper_suppressed.sum():,} suppressed"
    )


# ============================================================
# 11. GEOGRAPHIC COVERAGE
# ============================================================

def validate_geography(df):

    print("\n[9] GEOGRAPHIC COVERAGE")

    print("\nReporting level:")

    print(
        df["Reporting level"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nProvince / territory:")

    print(
        df["Province/territory"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 12. PROVINCIAL MAIN-METRIC RECORDS
# ============================================================

def inspect_provincial_records(df):

    print("\n[10] PROVINCIAL MAIN-METRIC RECORDS")

    provincial = df[
        (df["Reporting level"] == "Province/territory")
        & (df["Main metric"] == "Yes")
    ].copy()

    print(
        f"Records: {len(provincial):,}"
    )

    print(
        provincial[
            [
                "Province/territory",
                "Time frame",
                "Metric",
                "Metric value",
                "Unit of measure",
                "Confidence interval lower limit",
                "Confidence interval upper limit",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 13. DATA TYPE VALIDATION
# ============================================================

def validate_data_types(df):

    print("\n[11] DATA TYPE VALIDATION")

    print(
        df.dtypes.to_string()
    )

    if all(dtype == "object" for dtype in df.dtypes):
        print(
            "PASS — raw fields retained as strings "
            "for validation and cleaning."
        )
    else:
        print(
            "REVIEW — unexpected data types detected."
        )


# ============================================================
# 14. COMPLETION
# ============================================================

def main():

    df = load_data()

    validate_file(df)
    validate_indicator(df)
    validate_duplicates(df)
    validate_time(df)
    validate_main_metric(df)
    validate_supporting_metrics(df)
    validate_suppression(df)
    validate_confidence_intervals(df)
    validate_geography(df)
    inspect_provincial_records(df)
    validate_data_types(df)

    print("\n" + "=" * 75)
    print("VALIDATION COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()