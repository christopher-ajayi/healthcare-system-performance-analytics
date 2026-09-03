from pathlib import Path
import pandas as pd


# ============================================================================
# CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs
# DATA TRANSFORMATION
# ============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "outcomes"
    / "avoidable_hospitalizations_acscs_clean.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "outcomes"
    / "avoidable_hospitalizations_acscs_transformed.csv"
)


def main():

    print("=" * 75)
    print("CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs")
    print("DATA TRANSFORMATION")
    print("=" * 75)

    # ------------------------------------------------------------------------
    # 22.1 LOAD CLEAN DATA
    # ------------------------------------------------------------------------
    print("\n[22.1] LOAD CLEAN DATA")
    print(f"Input: {INPUT_FILE}")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # ------------------------------------------------------------------------
    # 22.2 STANDARDIZE COLUMN NAMES
    # ------------------------------------------------------------------------
    print("\n[22.2] STANDARDIZE COLUMN NAMES")

    rename_map = {
        "Place or organization": "place_or_organization",
        "Province/territory": "province_territory",
        "Region": "region",
        "Reporting level": "reporting_level",
        "Indicator": "indicator",
        "Measure type": "measure_type",
        "Indicator segment": "indicator_segment",
        "Segment value": "segment_value",
        "Time scale": "time_scale",
        "Time frame": "time_frame",
        "Level 1 breakdown": "level_1_breakdown",
        "Level 1 breakdown value": "level_1_breakdown_value",
        "Level 2 breakdown": "level_2_breakdown",
        "Level 2 breakdown value": "level_2_breakdown_value",
        "Level 3 breakdown": "level_3_breakdown",
        "Level 3 breakdown value": "level_3_breakdown_value",
        "Metric": "metric",
        "Main metric": "main_metric",
        "Metric value": "metric_value",
        "Unit of measure": "unit_of_measure",
        "Confidence interval lower limit": "confidence_interval_lower_limit",
        "Confidence interval upper limit": "confidence_interval_upper_limit",
        "Statistically different": "statistically_different",
        "Urban or rural/remote": "urban_or_rural_remote",
        "Hospital peer group": "hospital_peer_group",
        "Long-Term Care Facility Size": "long_term_care_facility_size",
        "Trend note": "trend_note",
        "Refresh date": "refresh_date",
    }

    df = df.rename(columns=rename_map)

    print("Column names standardized.")

    # ------------------------------------------------------------------------
    # 22.3 STANDARDIZE TEXT FIELDS
    # ------------------------------------------------------------------------
    print("\n[22.3] STANDARDIZE TEXT FIELDS")

    text_columns = df.select_dtypes(include="object").columns

    for col in text_columns:
        df[col] = df[col].astype("string").str.strip()

    print("Text fields standardized.")

    # ------------------------------------------------------------------------
    # 22.4 STANDARDIZE TIME FRAME
    # ------------------------------------------------------------------------
    print("\n[22.4] STANDARDIZE TIME FRAME")

    df["fiscal_year"] = (
        df["time_frame"]
        .str.replace("–", "-", regex=False)
        .str.replace("—", "-", regex=False)
        .str.strip()
    )

    # Restore canonical fiscal-year display using an en dash.
    df["fiscal_year"] = df["fiscal_year"].str.replace(
        r"^(\d{4})-(\d{4})$",
        r"\1–\2",
        regex=True,
    )

    # ------------------------------------------------------------------------
    # 22.5 TRANSFORM METRIC VALUE
    # ------------------------------------------------------------------------
    print("\n[22.5] TRANSFORM METRIC VALUE")

    df["metric_value_numeric"] = pd.to_numeric(
        df["metric_value"],
        errors="coerce",
    )

    numeric_count = df["metric_value_numeric"].notna().sum()

    suppressed_count = (
        df["metric_value"]
        .astype("string")
        .str.strip()
        .str.lower()
        .eq("suppressed")
        .sum()
    )

    print(f"Numeric metric observations: {numeric_count}")
    print(f"Suppressed observations: {suppressed_count}")

    # ------------------------------------------------------------------------
    # 22.6 TRANSFORM CONFIDENCE INTERVALS
    # ------------------------------------------------------------------------
    print("\n[22.6] TRANSFORM CONFIDENCE INTERVALS")

    df["ci_lower"] = pd.to_numeric(
        df["confidence_interval_lower_limit"],
        errors="coerce",
    )

    df["ci_upper"] = pd.to_numeric(
        df["confidence_interval_upper_limit"],
        errors="coerce",
    )

    print("Confidence interval numeric fields created.")

    # ------------------------------------------------------------------------
    # 22.7 SUPPRESSION HANDLING
    # ------------------------------------------------------------------------
    print("\n[22.7] SUPPRESSION HANDLING")

    df["suppressed"] = (
        df["metric_value"]
        .astype("string")
        .str.strip()
        .str.lower()
        .eq("suppressed")
    )

    print(
        "Suppressed metric observations preserved: "
        f"{df['suppressed'].sum()}"
    )

    # ------------------------------------------------------------------------
    # 22.8 CREATE TIME FIELDS
    # ------------------------------------------------------------------------
    print("\n[22.8] CREATE TIME FIELDS")

    df["fiscal_year_start"] = pd.to_numeric(
        df["fiscal_year"].str[:4],
        errors="coerce",
    ).astype("Int64")

    df["fiscal_year_end"] = pd.to_numeric(
        df["fiscal_year"].str[-4:],
        errors="coerce",
    ).astype("Int64")

    # ------------------------------------------------------------------------
    # 22.9 SELECT ANALYTICAL COLUMNS
    # ------------------------------------------------------------------------
    print("\n[22.9] SELECT ANALYTICAL COLUMNS")

    output_columns = [
        "place_or_organization",
        "province_territory",
        "region",
        "reporting_level",
        "indicator",
        "measure_type",
        "indicator_segment",
        "segment_value",
        "fiscal_year",
        "metric",
        "main_metric",
        "metric_value",
        "metric_value_numeric",
        "unit_of_measure",
        "ci_lower",
        "ci_upper",
        "suppressed",
        "statistically_different",
        "urban_or_rural_remote",
        "hospital_peer_group",
        "long_term_care_facility_size",
        "trend_note",
        "refresh_date",
        "fiscal_year_start",
        "fiscal_year_end",
    ]

    missing_columns = [
        col for col in output_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required transformed columns missing: "
            + ", ".join(missing_columns)
        )

    df = df[output_columns]

    # ------------------------------------------------------------------------
    # 22.10 SORT DATA
    # ------------------------------------------------------------------------
    print("\n[22.10] SORT DATA")

    df = df.sort_values(
        by=["province_territory", "fiscal_year_start"],
        ascending=[True, True],
        na_position="last",
    ).reset_index(drop=True)

    # ------------------------------------------------------------------------
    # 22.11 SAVE TRANSFORMED DATA
    # ------------------------------------------------------------------------
    print("\n[22.11] SAVE TRANSFORMED DATA")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Output: {OUTPUT_FILE}")

    # ------------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("TRANSFORMATION SUMMARY")
    print("=" * 75)

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(
        "Provinces/territories: "
        f"{df['province_territory'].nunique()}"
    )
    print(
        "Fiscal years: "
        f"{df['fiscal_year'].nunique()}"
    )
    print(
        "Numeric metric observations: "
        f"{df['metric_value_numeric'].notna().sum()}"
    )
    print(
        "Suppressed metric observations: "
        f"{df['suppressed'].sum()}"
    )

    print("\nTransformation complete.")
    print("=" * 75)


if __name__ == "__main__":
    main()