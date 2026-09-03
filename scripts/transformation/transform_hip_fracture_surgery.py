from pathlib import Path
import pandas as pd
import re


# ============================================================================
# CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS
# DATA TRANSFORMATION
# ============================================================================

BASE_DIR = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
)

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "outcomes"
    / "hip_fracture_surgery_within_48_hours_clean.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "outcomes"
    / "hip_fracture_surgery_within_48_hours_transformed.csv"
)


def standardize_column_name(column):
    column = str(column).strip().lower()
    column = re.sub(r"[^a-z0-9]+", "_", column)
    column = re.sub(r"_+", "_", column)
    return column.strip("_")


def standardize_text(value):
    if pd.isna(value):
        return value

    value = str(value).strip()

    # Preserve source suppression/missing markers.
    if value in {"", "nan", "NaN"}:
        return pd.NA

    return value


def extract_fiscal_years(value):
    if pd.isna(value):
        return pd.NA, pd.NA

    text = str(value).strip()

    match = re.search(r"(\d{4})\s*[–-]\s*(\d{4})", text)

    if match:
        return int(match.group(1)), int(match.group(2))

    return pd.NA, pd.NA


def main():

    print("=" * 74)
    print("CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS")
    print("DATA TRANSFORMATION")
    print("=" * 74)

    # ------------------------------------------------------------------------
    # [25.1] LOAD CLEAN DATA
    # ------------------------------------------------------------------------
    print("\n[25.1] LOAD CLEAN DATA")
    print(f"Input: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE, dtype=str)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    # ------------------------------------------------------------------------
    # [25.2] STANDARDIZE COLUMN NAMES
    # ------------------------------------------------------------------------
    print("\n[25.2] STANDARDIZE COLUMN NAMES")

    df.columns = [standardize_column_name(c) for c in df.columns]

    print("Column names standardized.")

    # ------------------------------------------------------------------------
    # [25.3] STANDARDIZE TEXT FIELDS
    # ------------------------------------------------------------------------
    print("\n[25.3] STANDARDIZE TEXT FIELDS")

    text_columns = df.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        df[column] = df[column].map(standardize_text)

    print("Text fields standardized.")

    # ------------------------------------------------------------------------
    # [25.4] STANDARDIZE TIME FRAME
    # ------------------------------------------------------------------------
    print("\n[25.4] STANDARDIZE TIME FRAME")

    if "time_frame" in df.columns:
        df["fiscal_year"] = (
            df["time_frame"]
            .astype("string")
            .str.replace("-", "–", regex=False)
            .str.strip()
        )

    elif "fiscal_year" in df.columns:
        df["fiscal_year"] = (
            df["fiscal_year"]
            .astype("string")
            .str.replace("-", "–", regex=False)
            .str.strip()
        )

    else:
        raise KeyError(
            "Neither 'time_frame' nor 'fiscal_year' exists in the clean dataset."
        )

    # ------------------------------------------------------------------------
    # [25.5] TRANSFORM METRIC VALUE
    # ------------------------------------------------------------------------
    print("\n[25.5] TRANSFORM METRIC VALUE")

    if "metric_value" not in df.columns:
        raise KeyError("Expected 'metric_value' column was not found.")

    metric_numeric = pd.to_numeric(
        df["metric_value"],
        errors="coerce"
    )

    suppressed_mask = (
        df["metric_value"]
        .astype("string")
        .str.strip()
        .str.lower()
        .eq("suppressed")
    )

    df["metric_value_numeric"] = metric_numeric

    print(
        "Numeric metric observations:",
        int(metric_numeric.notna().sum())
    )

    print(
        "Suppressed observations:",
        int(suppressed_mask.sum())
    )

    # ------------------------------------------------------------------------
    # [25.6] TRANSFORM CONFIDENCE INTERVALS
    # ------------------------------------------------------------------------
    print("\n[25.6] TRANSFORM CONFIDENCE INTERVALS")

    if "confidence_interval_lower_limit" in df.columns:
        df["ci_lower"] = pd.to_numeric(
            df["confidence_interval_lower_limit"],
            errors="coerce"
        )
    elif "ci_lower" in df.columns:
        df["ci_lower"] = pd.to_numeric(
            df["ci_lower"],
            errors="coerce"
        )
    else:
        df["ci_lower"] = pd.NA

    if "confidence_interval_upper_limit" in df.columns:
        df["ci_upper"] = pd.to_numeric(
            df["confidence_interval_upper_limit"],
            errors="coerce"
        )
    elif "ci_upper" in df.columns:
        df["ci_upper"] = pd.to_numeric(
            df["ci_upper"],
            errors="coerce"
        )
    else:
        df["ci_upper"] = pd.NA

    print("Confidence interval numeric fields created.")

    # ------------------------------------------------------------------------
    # [25.7] SUPPRESSION HANDLING
    # ------------------------------------------------------------------------
    print("\n[25.7] SUPPRESSION HANDLING")

    df["suppressed"] = (
        suppressed_mask
        .fillna(False)
        .astype(bool)
    )

    print(
        "Suppressed metric observations preserved:",
        int(df["suppressed"].sum())
    )

    # ------------------------------------------------------------------------
    # [25.8] CREATE TIME FIELDS
    # ------------------------------------------------------------------------
    print("\n[25.8] CREATE TIME FIELDS")

    fiscal_year_parts = df["fiscal_year"].apply(extract_fiscal_years)

    df["fiscal_year_start"] = fiscal_year_parts.map(
        lambda x: x[0]
    ).astype("Int64")

    df["fiscal_year_end"] = fiscal_year_parts.map(
        lambda x: x[1]
    ).astype("Int64")

    # ------------------------------------------------------------------------
    # [25.9] SELECT ANALYTICAL COLUMNS
    # ------------------------------------------------------------------------
    print("\n[25.9] SELECT ANALYTICAL COLUMNS")

    preferred_columns = [
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

    output_columns = [
        column
        for column in preferred_columns
        if column in df.columns
    ]

    df = df[output_columns]

    # ------------------------------------------------------------------------
    # [25.10] SORT DATA
    # ------------------------------------------------------------------------
    print("\n[25.10] SORT DATA")

    sort_columns = [
        column
        for column in [
            "province_territory",
            "fiscal_year_start",
            "fiscal_year",
        ]
        if column in df.columns
    ]

    if sort_columns:
        df = df.sort_values(
            sort_columns,
            kind="stable"
        ).reset_index(drop=True)

    # ------------------------------------------------------------------------
    # [25.11] SAVE TRANSFORMED DATA
    # ------------------------------------------------------------------------
    print("\n[25.11] SAVE TRANSFORMED DATA")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Output: {OUTPUT_FILE}")

    # ------------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------------
    print("\n" + "=" * 74)
    print("TRANSFORMATION SUMMARY")
    print("=" * 74)

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    if "province_territory" in df.columns:
        print(
            "Provinces/territories:",
            df["province_territory"].nunique()
        )

    if "fiscal_year" in df.columns:
        print(
            "Fiscal years:",
            df["fiscal_year"].nunique()
        )

    print(
        "Numeric metric observations:",
        int(df["metric_value_numeric"].notna().sum())
    )

    print(
        "Suppressed metric observations:",
        int(df["suppressed"].sum())
    )

    print("\nTransformation complete.")
    print("=" * 74)


if __name__ == "__main__":
    main()