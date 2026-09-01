from pathlib import Path
import pandas as pd


# ============================================================================
# [20] CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs
# DATA CLEANING
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "avoidable_hospitalizations_acscs_raw.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "avoidable_hospitalizations_acscs_clean.csv"
)

INDICATOR = "Ambulatory Care Sensitive Conditions Hospitalizations"


def main():

    print("=" * 75)
    print("CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs")
    print("DATA CLEANING")
    print("=" * 75)

    # ------------------------------------------------------------------------
    # [20.1] LOAD RAW DATA
    # ------------------------------------------------------------------------

    print("\n[20.1] LOAD RAW DATA")
    print(f"Input: {INPUT_FILE}")

    df = pd.read_csv(
        INPUT_FILE,
        dtype=str
    )

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    # ------------------------------------------------------------------------
    # [20.2] INDICATOR FILTER
    # ------------------------------------------------------------------------

    print("\n[20.2] INDICATOR FILTER")

    df = df[
        df["Indicator"].eq(INDICATOR)
    ].copy()

    print(f"Rows after indicator filter: {len(df):,}")

    # ------------------------------------------------------------------------
    # [20.3] PRIMARY METRIC FILTER
    #
    # Retain the main age-standardized rate.
    # Other metrics such as Percent, Crude rate, Numerator,
    # Denominator, Rate Ratio and Potential Rate Reduction
    # are supporting/alternative measures and are not retained
    # in this primary Outcome dataset.
    # ------------------------------------------------------------------------

    print("\n[20.3] PRIMARY METRIC FILTER")

    df = df[
        (df["Main metric"].eq("Yes")) &
        (df["Metric"].eq("Age-standardized rate"))
    ].copy()

    print(f"Primary metric rows: {len(df):,}")

    # ------------------------------------------------------------------------
    # [20.4] UNIT VALIDATION
    # ------------------------------------------------------------------------

    print("\n[20.4] UNIT FILTER")

    invalid_units = df[
        ~df["Unit of measure"].eq("Per 100,000")
    ]

    if not invalid_units.empty:
        raise ValueError(
            "Unexpected unit found in primary metric records:\n"
            f"{invalid_units['Unit of measure'].value_counts(dropna=False)}"
        )

    print("Unit confirmed: Per 100,000")

    # ------------------------------------------------------------------------
    # [20.5] PROVINCIAL MAIN-METRIC RECORDS
    #
    # Keep province/territory observations separately from health-region
    # and national observations.
    # ------------------------------------------------------------------------

    print("\n[20.5] PROVINCIAL MAIN-METRIC RECORDS")

    provincial = df[
        df["Reporting level"].eq("Province/territory")
    ].copy()

    print(
        f"Provincial main-metric records: "
        f"{len(provincial):,}"
    )

    # ------------------------------------------------------------------------
    # [20.6] RETAIN REQUIRED PROVINCIAL STRUCTURE
    #
    # The provincial series is retained where the indicator is not further
    # broken down. Breakdown records remain available in the raw dataset
    # but are not mixed into the primary provincial Outcome dataset.
    # ------------------------------------------------------------------------

    overall_provincial = provincial[
        provincial["Level 1 breakdown"].eq("Not applicable") &
        provincial["Level 1 breakdown value"].eq("Not applicable") &
        provincial["Level 2 breakdown"].eq("Not applicable") &
        provincial["Level 2 breakdown value"].eq("Not applicable") &
        provincial["Level 3 breakdown"].eq("Not applicable") &
        provincial["Level 3 breakdown value"].eq("Not applicable")
    ].copy()

    breakdown_provincial = provincial[
        ~(
            provincial["Level 1 breakdown"].eq("Not applicable") &
            provincial["Level 1 breakdown value"].eq("Not applicable") &
            provincial["Level 2 breakdown"].eq("Not applicable") &
            provincial["Level 2 breakdown value"].eq("Not applicable") &
            provincial["Level 3 breakdown"].eq("Not applicable") &
            provincial["Level 3 breakdown value"].eq("Not applicable")
        )
    ].copy()

    print(
        f"Overall provincial records: "
        f"{len(overall_provincial):,}"
    )

    print(
        f"Provincial breakdown records retained separately: "
        f"{len(breakdown_provincial):,}"
    )

    # ------------------------------------------------------------------------
    # [20.7] REMOVE UNNECESSARY RAW-ONLY FIELDS
    #
    # Keep the analytical fields required for subsequent validation and
    # analysis. Do not calculate rates, ratios, rankings or trends here.
    # ------------------------------------------------------------------------

    keep_columns = [
        "Place or organization",
        "Province/territory",
        "Region",
        "Reporting level",
        "Indicator",
        "Measure type",
        "Indicator segment",
        "Segment value",
        "Time scale",
        "Time frame",
        "Level 1 breakdown",
        "Level 1 breakdown value",
        "Level 2 breakdown",
        "Level 2 breakdown value",
        "Level 3 breakdown",
        "Level 3 breakdown value",
        "Metric",
        "Main metric",
        "Metric value",
        "Unit of measure",
        "Confidence interval lower limit",
        "Confidence interval upper limit",
        "Statistically different",
        "Urban or rural/remote",
        "Hospital peer group",
        "Long-Term Care Facility Size",
        "Trend note",
        "Refresh date",
    ]

    missing_columns = [
        col for col in keep_columns
        if col not in overall_provincial.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required columns missing:\n"
            + "\n".join(missing_columns)
        )

    clean = overall_provincial[
        keep_columns
    ].copy()

    # ------------------------------------------------------------------------
    # [20.8] SUPPRESSION PRESERVATION
    #
    # Suppressed values and suppressed confidence intervals remain exactly
    # as supplied by CIHI. No imputation is performed.
    # ------------------------------------------------------------------------

    print("\n[20.8] SUPPRESSION CHECK")

    print(
        clean["Metric value"]
        .value_counts(dropna=False)
        .head(10)
    )

    # ------------------------------------------------------------------------
    # [20.9] SORT
    # ------------------------------------------------------------------------

    print("\n[20.9] SORT DATA")

    clean = clean.sort_values(
        by=[
            "Province/territory",
            "Time frame"
        ],
        kind="stable"
    ).reset_index(drop=True)

    # ------------------------------------------------------------------------
    # [20.10] SAVE CLEAN DATA
    # ------------------------------------------------------------------------

    print("\n[20.10] SAVE CLEAN DATA")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    clean.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # ------------------------------------------------------------------------
    # [20.11] CLEANING SUMMARY
    # ------------------------------------------------------------------------

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
    )

    print("\nFiscal years:")
    print(
        clean["Time frame"]
        .value_counts()
        .sort_index()
    )

    print("\nMetric:")
    print(clean["Metric"].value_counts(dropna=False))

    print("\nUnit:")
    print(clean["Unit of measure"].value_counts(dropna=False))

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nCleaning complete.")
    print("=" * 75)


if __name__ == "__main__":
    main()