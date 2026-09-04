from pathlib import Path
import pandas as pd


# ============================================================
# CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS
# RAW DATA QUALITY ASSESSMENT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "hip_fracture_surgery_within_48_hours_raw.csv"
)


def main():

    print("=" * 75)
    print("CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS")
    print("RAW DATA QUALITY ASSESSMENT")
    print("=" * 75)

    df = pd.read_csv(INPUT_FILE, dtype=str)

    # --------------------------------------------------------
    # 1. File-level validation
    # --------------------------------------------------------

    print("\n[1] FILE VALIDATION")

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    assert len(df) == 1479, "Unexpected row count."
    assert len(df.columns) == 33, "Unexpected column count."

    print("PASS — expected dimensions confirmed.")

    # --------------------------------------------------------
    # 2. Indicator validation
    # --------------------------------------------------------

    print("\n[2] INDICATOR VALIDATION")

    indicators = df["Indicator"].value_counts(dropna=False)

    print(indicators.to_string())

    assert len(indicators) == 1
    assert indicators.index[0] == "Hip Fracture Surgery Within 48 Hours"

    print("PASS — single expected indicator.")

    # --------------------------------------------------------
    # 3. Duplicate validation
    # --------------------------------------------------------

    print("\n[3] DUPLICATE VALIDATION")

    duplicates = df.duplicated().sum()

    print(f"Exact duplicate rows: {duplicates}")

    assert duplicates == 0

    print("PASS — no exact duplicate rows.")

    # --------------------------------------------------------
    # 4. Time validation
    # --------------------------------------------------------

    print("\n[4] TIME VALIDATION")

    expected_years = {
        "2020–2021",
        "2021–2022",
        "2022–2023",
        "2023–2024",
        "2024–2025",
    }

    actual_years = set(df["Time frame"].dropna().unique())

    print("Actual periods:")
    for year in sorted(actual_years):
        print(f"  {year}")

    assert actual_years == expected_years

    print("PASS — expected five fiscal-year periods confirmed.")

    # --------------------------------------------------------
    # 5. Main metric validation
    # --------------------------------------------------------

    print("\n[5] MAIN METRIC VALIDATION")

    main_metric = df[df["Main metric"] == "Yes"]

    print(f"Main metric records: {len(main_metric):,}")

    print("\nMetric:")
    print(main_metric["Metric"].value_counts().to_string())

    print("\nUnit:")
    print(main_metric["Unit of measure"].value_counts().to_string())

    assert set(main_metric["Metric"].unique()) == {
        "Risk-adjusted rate"
    }

    assert set(main_metric["Unit of measure"].unique()) == {
        "Percent"
    }

    print("PASS — main metric is risk-adjusted rate (%).")

    # --------------------------------------------------------
    # 6. Supporting metrics
    # --------------------------------------------------------

    print("\n[6] SUPPORTING METRICS")

    supporting = df[df["Main metric"] == "No"]

    print(
        supporting["Metric"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # 7. Suppression assessment
    # --------------------------------------------------------

    print("\n[7] SUPPRESSION ASSESSMENT")

    suppressed_metric = (
        df["Metric value"]
        .str.strip()
        .str.casefold()
        .eq("suppressed")
    )

    print(
        f"Suppressed metric values: "
        f"{suppressed_metric.sum():,}"
    )

    print(
        f"Non-suppressed metric values: "
        f"{(~suppressed_metric).sum():,}"
    )

    # --------------------------------------------------------
    # 8. Confidence interval suppression
    # --------------------------------------------------------

    print("\n[8] CONFIDENCE INTERVAL ASSESSMENT")

    for column in [
        "Confidence interval lower limit",
        "Confidence interval upper limit",
    ]:

        suppressed = (
            df[column]
            .fillna("")
            .str.strip()
            .str.casefold()
            .eq("suppressed")
        )

        print(
            f"{column}: "
            f"{suppressed.sum():,} suppressed"
        )

    # --------------------------------------------------------
    # 9. Geographic coverage
    # --------------------------------------------------------

    print("\n[9] GEOGRAPHIC COVERAGE")

    print(
        df["Reporting level"]
        .value_counts()
        .to_string()
    )

    print("\nProvince / territory:")

    print(
        df["Province/territory"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    # --------------------------------------------------------
    # 10. Main provincial indicator records
    # --------------------------------------------------------

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
        ]
        .sort_values(
            ["Province/territory", "Time frame"]
        )
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # 11. Validation summary
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("VALIDATION SUMMARY")
    print("=" * 75)

    print("""
PASS:
- Expected file dimensions
- Single indicator
- No exact duplicate rows
- Expected fiscal-year coverage
- Main metric correctly identified
- Risk-adjusted rate correctly identified
- Percent unit correctly identified
- Suppression retained for later handling

REQUIRES CLEANING:
- Numeric conversion of metric values
- Numeric conversion of confidence intervals
- Treatment of suppressed values
- Separation of main metric from supporting metrics
- Selection of analytical geographic level
- Standardization of missing-value representations
""")

    print("=" * 75)


if __name__ == "__main__":
    main()