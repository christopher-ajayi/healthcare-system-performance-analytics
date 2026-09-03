"""
CIHI — 30-DAY HOSPITAL READMISSION
DATA TRANSFORMATION

Stage 22 — Data Preparation / Transformation
"""

from pathlib import Path
import pandas as pd


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "30_day_hospital_readmission_clean.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "outcomes"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "30_day_hospital_readmission_transformed.csv"
)


# ============================================================================
# MAIN
# ============================================================================

def main():

    print("=" * 75)
    print("CIHI — 30-DAY HOSPITAL READMISSION")
    print("DATA TRANSFORMATION")
    print("=" * 75)

    # ------------------------------------------------------------------------
    # [22.1] LOAD CLEAN DATA
    # ------------------------------------------------------------------------

    print("\n[22.1] LOAD CLEAN DATA")
    print(f"Input: {INPUT_FILE}")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Clean input file not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # ------------------------------------------------------------------------
    # [22.2] STANDARDIZE COLUMN NAMES
    # ------------------------------------------------------------------------

    print("\n[22.2] STANDARDIZE COLUMN NAMES")

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace("/", "_", regex=False)
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    print("Column names standardized.")

    # ------------------------------------------------------------------------
    # [22.3] STANDARDIZE TEXT FIELDS
    # ------------------------------------------------------------------------

    print("\n[22.3] STANDARDIZE TEXT FIELDS")

    text_columns = [
        "place_or_organization",
        "province_territory",
        "region",
        "reporting_level",
        "indicator",
        "measure_type",
        "indicator_segment",
        "segment_value",
        "time_scale",
        "time_frame",
        "level_1_breakdown",
        "level_1_breakdown_value",
        "level_2_breakdown",
        "level_2_breakdown_value",
        "level_3_breakdown",
        "level_3_breakdown_value",
        "metric",
        "main_metric",
        "unit_of_measure",
        "statistically_different",
        "performance_comparison",
        "performance_trend",
        "top_results",
        "data_coverage",
        "urban_or_rural_remote",
        "hospital_peer_group",
        "long_term_care_facility_size",
        "trend_note",
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    print("Text fields standardized.")

    # ------------------------------------------------------------------------
    # [22.4] STANDARDIZE TIME FRAME
    # ------------------------------------------------------------------------

    print("\n[22.4] STANDARDIZE TIME FRAME")

    if "time_frame" in df.columns:

        df["time_frame"] = (
            df["time_frame"]
            .str.replace("–", "-", regex=False)
            .str.strip()
        )

        print(
            f"Fiscal years: "
            f"{df['time_frame'].dropna().nunique()}"
        )

    # ------------------------------------------------------------------------
    # [22.5] NUMERIC METRIC
    # ------------------------------------------------------------------------

    print("\n[22.5] TRANSFORM METRIC VALUE")

    if "metric_value" not in df.columns:
        raise ValueError(
            "Expected 'metric_value' column not found."
        )

    # Preserve suppression while converting numeric values.
    df["metric_value_numeric"] = pd.to_numeric(
        df["metric_value"],
        errors="coerce"
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

    print(f"Numeric metric observations: {numeric_count:,}")
    print(f"Suppressed observations: {suppressed_count:,}")

    # ------------------------------------------------------------------------
    # [22.6] CONFIDENCE INTERVALS
    # ------------------------------------------------------------------------

    print("\n[22.6] TRANSFORM CONFIDENCE INTERVALS")

    for col in [
        "confidence_interval_lower_limit",
        "confidence_interval_upper_limit",
    ]:

        if col in df.columns:

            df[f"{col}_numeric"] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    print("Confidence interval numeric fields created.")

    # ------------------------------------------------------------------------
    # [22.7] STANDARDIZE SUPPRESSION
    # ------------------------------------------------------------------------

    print("\n[22.7] SUPPRESSION HANDLING")

    suppression_mask = (
        df["metric_value"]
        .astype("string")
        .str.strip()
        .str.lower()
        .eq("suppressed")
    )

    print(
        f"Suppressed metric observations preserved: "
        f"{suppression_mask.sum():,}"
    )

    # ------------------------------------------------------------------------
    # [22.8] CREATE ANALYTICAL TIME FIELDS
    # ------------------------------------------------------------------------

    print("\n[22.8] CREATE TIME FIELDS")

    if "time_frame" in df.columns:

        df["fiscal_year_start"] = pd.to_numeric(
            df["time_frame"]
            .str.extract(r"^(\d{4})")[0],
            errors="coerce"
        )

        df["fiscal_year_end"] = pd.to_numeric(
            df["time_frame"]
            .str.extract(r"(\d{4})$")[0],
            errors="coerce"
        )

    # ------------------------------------------------------------------------
    # [22.9] SORT
    # ------------------------------------------------------------------------

    print("\n[22.9] SORT DATA")

    sort_columns = [
        col
        for col in [
            "province_territory",
            "time_frame",
            "place_or_organization",
        ]
        if col in df.columns
    ]

    if sort_columns:
        df = df.sort_values(sort_columns).reset_index(drop=True)

    # ------------------------------------------------------------------------
    # [22.10] OUTPUT
    # ------------------------------------------------------------------------

    print("\n[22.10] SAVE TRANSFORMED DATA")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
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

    if "province_territory" in df.columns:
        print(
            f"Provinces/territories: "
            f"{df['province_territory'].nunique()}"
        )

    if "time_frame" in df.columns:
        print(
            f"Fiscal years: "
            f"{df['time_frame'].nunique()}"
        )

    print(
        f"Numeric metric observations: "
        f"{df['metric_value_numeric'].notna().sum():,}"
    )

    print(
        f"Suppressed metric observations: "
        f"{suppression_mask.sum():,}"
    )

    print("\nTransformation complete.")
    print("=" * 75)


if __name__ == "__main__":
    main()