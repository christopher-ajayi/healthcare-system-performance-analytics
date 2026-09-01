from pathlib import Path
import pandas as pd


# ============================================================
# 1. CIHI — 30-DAY HOSPITAL READMISSION
#    DATA CLEANING
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "30_day_hospital_readmission_raw.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "30_day_hospital_readmission_clean.csv"
)


def main():

    print("=" * 75)
    print("CIHI — 30-DAY HOSPITAL READMISSION")
    print("DATA CLEANING")
    print("=" * 75)

    # ========================================================
    # 2. LOAD RAW DATA
    # ========================================================

    print("\n[2] LOAD RAW DATA")

    df = pd.read_csv(
        INPUT_FILE,
        dtype=str
    )

    print(f"Input rows: {len(df):,}")
    print(f"Input columns: {len(df.columns):,}")

    # ========================================================
    # 3. FILTER PRIMARY ANALYTICAL METRIC
    # ========================================================

    print("\n[3] FILTER PRIMARY ANALYTICAL METRIC")

    clean = df[
        (df["Main metric"] == "Yes") &
        (df["Metric"] == "Risk-adjusted rate") &
        (df["Reporting level"] == "Province/territory")
    ].copy()

    print(f"After primary metric filter: {len(clean):,} rows")

    # ========================================================
    # 4. IDENTIFY SUPPRESSED VALUES
    # ========================================================

    print("\n[4] IDENTIFY SUPPRESSED VALUES")

    clean["suppressed"] = (
        clean["Metric value"]
        .astype(str)
        .str.strip()
        .eq("Suppressed")
    )

    print(
        clean["suppressed"]
        .value_counts()
        .sort_index()
    )

    # ========================================================
    # 5. STANDARDIZE FISCAL YEAR
    # ========================================================

    print("\n[5] STANDARDIZE FISCAL YEAR")

    clean["fiscal_year"] = clean["Time frame"].astype(str).str.strip()

    print(
        clean["fiscal_year"]
        .value_counts()
        .sort_index()
    )

    # ========================================================
    # 6. CONVERT NUMERIC METRIC FIELDS
    # ========================================================

    print("\n[6] CONVERT NUMERIC METRIC FIELDS")

    clean["metric_value"] = pd.to_numeric(
        clean["Metric value"],
        errors="coerce"
    )

    clean["ci_lower"] = pd.to_numeric(
        clean["Confidence interval lower limit"],
        errors="coerce"
    )

    clean["ci_upper"] = pd.to_numeric(
        clean["Confidence interval upper limit"],
        errors="coerce"
    )

    print(
        f"metric_value numeric observations: "
        f"{clean['metric_value'].notna().sum():,}"
    )

    print(
        f"ci_lower numeric observations: "
        f"{clean['ci_lower'].notna().sum():,}"
    )

    print(
        f"ci_upper numeric observations: "
        f"{clean['ci_upper'].notna().sum():,}"
    )

    # ========================================================
    # 7. RETAIN CLEAN ANALYTICAL FIELDS
    # ========================================================

    print("\n[7] RETAIN CLEAN ANALYTICAL FIELDS")

    clean = clean[
        [
            "Province/territory",
            "fiscal_year",
            "Indicator",
            "Metric",
            "Unit of measure",
            "metric_value",
            "ci_lower",
            "ci_upper",
            "suppressed",
            "Refresh date"
        ]
    ].copy()

    print(f"Clean rows: {len(clean):,}")
    print(f"Clean columns: {len(clean.columns):,}")

    # ========================================================
    # 8. ORDER RECORDS
    # ========================================================

    print("\n[8] ORDER RECORDS")

    fiscal_order = [
        "2020–2021",
        "2021–2022",
        "2022–2023",
        "2023–2024",
        "2024–2025"
    ]

    clean["fiscal_year"] = pd.Categorical(
        clean["fiscal_year"],
        categories=fiscal_order,
        ordered=True
    )

    clean = clean.sort_values(
        ["Province/territory", "fiscal_year"]
    ).reset_index(drop=True)

    # ========================================================
    # 9. SAVE CLEAN DATA
    # ========================================================

    print("\n[9] SAVE CLEAN DATA")

    clean.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nCleaning complete.")
    print("=" * 75)


if __name__ == "__main__":
    main()