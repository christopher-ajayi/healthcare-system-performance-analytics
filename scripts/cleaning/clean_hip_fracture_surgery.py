from pathlib import Path
import pandas as pd


# ============================================================
# CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS
# DATA CLEANING
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "hip_fracture_surgery_within_48_hours_raw.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "hip_fracture_surgery_within_48_hours_clean.csv"
)


def main():

    print("=" * 75)
    print("CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS")
    print("DATA CLEANING")
    print("=" * 75)

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    df = pd.read_csv(INPUT_FILE, dtype=str)

    print(f"\nInput rows: {len(df):,}")

    # --------------------------------------------------------
    # 2. Keep primary indicator metric
    # --------------------------------------------------------

    df = df[
        (df["Indicator"] == "Hip Fracture Surgery Within 48 Hours")
        & (df["Measure type"] == "Indicator")
        & (df["Metric"] == "Risk-adjusted rate")
        & (df["Main metric"] == "Yes")
    ].copy()

    print(
        f"After primary metric filter: "
        f"{len(df):,} rows"
    )

    # --------------------------------------------------------
    # 3. Identify provincial records
    # --------------------------------------------------------

    provincial = df[
        df["Reporting level"] == "Province/territory"
    ].copy()

    print(
        f"Provincial main-metric records: "
        f"{len(provincial):,}"
    )

    # --------------------------------------------------------
    # 4. Inspect breakdown structure
    # --------------------------------------------------------

    print("\nProvincial breakdown structure:")

    breakdown_columns = [
        "Level 1 breakdown",
        "Level 1 breakdown value",
        "Level 2 breakdown",
        "Level 2 breakdown value",
        "Level 3 breakdown",
        "Level 3 breakdown value",
    ]

    for column in breakdown_columns:
        print(f"\n{column}:")
        print(
            provincial[column]
            .value_counts(dropna=False)
            .head(20)
            .to_string()
        )

    # --------------------------------------------------------
    # 5. Identify overall provincial records
    # --------------------------------------------------------
    #
    # The overall provincial result has all breakdown fields
    # marked "Not applicable".
    #
    # Do NOT aggregate income-quintile values.
    # --------------------------------------------------------

    overall_mask = (
        (provincial["Level 1 breakdown"] == "Not applicable")
        & (provincial["Level 1 breakdown value"] == "Not applicable")
        & (provincial["Level 2 breakdown"] == "Not applicable")
        & (provincial["Level 2 breakdown value"] == "Not applicable")
        & (provincial["Level 3 breakdown"] == "Not applicable")
        & (provincial["Level 3 breakdown value"] == "Not applicable")
    )

    provincial_overall = provincial[overall_mask].copy()

    print(
        "\nOverall provincial records: "
        f"{len(provincial_overall):,}"
    )

    # --------------------------------------------------------
    # 6. Preserve income-quintile records separately
    # --------------------------------------------------------

    provincial_income = provincial[~overall_mask].copy()

    print(
        "Provincial breakdown records retained separately: "
        f"{len(provincial_income):,}"
    )

    # --------------------------------------------------------
    # 7. Convert numeric fields
    # --------------------------------------------------------

    numeric_columns = [
        "Metric value",
        "Confidence interval lower limit",
        "Confidence interval upper limit",
    ]

    for column in numeric_columns:

        df[column + " numeric"] = pd.to_numeric(
            df[column].replace(
                {
                    "Suppressed": pd.NA,
                    "suppressed": pd.NA,
                    "": pd.NA,
                    "-": pd.NA,
                }
            ),
            errors="coerce",
        )

    # --------------------------------------------------------
    # 8. Add explicit suppression flag
    # --------------------------------------------------------

    df["suppressed"] = (
        df["Metric value"]
        .fillna("")
        .str.strip()
        .str.casefold()
        .eq("suppressed")
    )

    # --------------------------------------------------------
    # 9. Create clean analytical provincial dataset
    # --------------------------------------------------------

    clean = provincial_overall.copy()

    clean["metric_value"] = pd.to_numeric(
        clean["Metric value"].replace(
            {
                "Suppressed": pd.NA,
                "suppressed": pd.NA,
                "": pd.NA,
                "-": pd.NA,
            }
        ),
        errors="coerce",
    )

    clean["ci_lower"] = pd.to_numeric(
        clean["Confidence interval lower limit"].replace(
            {
                "Suppressed": pd.NA,
                "suppressed": pd.NA,
                "": pd.NA,
                "-": pd.NA,
            }
        ),
        errors="coerce",
    )

    clean["ci_upper"] = pd.to_numeric(
        clean["Confidence interval upper limit"].replace(
            {
                "Suppressed": pd.NA,
                "suppressed": pd.NA,
                "": pd.NA,
                "-": pd.NA,
            }
        ),
        errors="coerce",
    )

    clean["suppressed"] = (
        clean["Metric value"]
        .fillna("")
        .str.strip()
        .str.casefold()
        .eq("suppressed")
    )

    # --------------------------------------------------------
    # 10. Standardize year
    # --------------------------------------------------------

    clean["fiscal_year"] = clean["Time frame"]

    # --------------------------------------------------------
    # 11. Standardize indicator name
    # --------------------------------------------------------

    clean["indicator"] = (
        "Hip Fracture Surgery Within 48 Hours"
    )

    clean["metric"] = "Risk-adjusted rate"

    clean["unit"] = "Percent"

    # --------------------------------------------------------
    # 12. Select analytical fields
    # --------------------------------------------------------

    clean = clean[
        [
            "indicator",
            "Province/territory",
            "fiscal_year",
            "metric",
            "unit",
            "metric_value",
            "ci_lower",
            "ci_upper",
            "suppressed",
            "Refresh date",
        ]
    ].copy()

    # --------------------------------------------------------
    # 13. Sort
    # --------------------------------------------------------

    clean = clean.sort_values(
        [
            "Province/territory",
            "fiscal_year",
        ]
    )

    # --------------------------------------------------------
    # 14. Remove exact duplicates
    # --------------------------------------------------------

    clean = clean.drop_duplicates()

    # --------------------------------------------------------
    # 15. Save
    # --------------------------------------------------------

    clean.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # 16. Report
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("CLEANING SUMMARY")
    print("=" * 75)

    print(f"Clean rows: {len(clean):,}")
    print(f"Clean columns: {len(clean.columns):,}")

    print("\nProvinces/territories:")
    print(
        clean["Province/territory"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nFiscal years:")
    print(
        clean["fiscal_year"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nSuppressed records:")
    print(clean["suppressed"].value_counts().to_string())

    print("\nMetric value:")
    print(clean["metric_value"].describe().to_string())

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nCleaning complete.")
    print("=" * 75)


if __name__ == "__main__":
    main()