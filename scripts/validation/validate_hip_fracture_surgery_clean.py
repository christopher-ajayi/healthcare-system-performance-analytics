from pathlib import Path
import pandas as pd


# ============================================================
# CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS
# CLEAN DATA VALIDATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "hip_fracture_surgery_within_48_hours_clean.csv"
)


def main():

    print("=" * 75)
    print("CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS")
    print("CLEAN DATA VALIDATION")
    print("=" * 75)

    df = pd.read_csv(INPUT_FILE)

    # --------------------------------------------------------
    # 1. Dimensions
    # --------------------------------------------------------

    print("\n[1] DIMENSIONS")

    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    assert len(df) == 60
    assert len(df.columns) == 10

    print("PASS")

    # --------------------------------------------------------
    # 2. Indicator
    # --------------------------------------------------------

    print("\n[2] INDICATOR")

    print(df["indicator"].value_counts().to_string())

    assert df["indicator"].nunique() == 1
    assert (
        df["indicator"].iloc[0]
        == "Hip Fracture Surgery Within 48 Hours"
    )

    print("PASS")

    # --------------------------------------------------------
    # 3. Geography
    # --------------------------------------------------------

    print("\n[3] GEOGRAPHIC COVERAGE")

    provinces = sorted(
        df["Province/territory"].unique()
    )

    print(f"Provinces/territories: {len(provinces)}")

    for province in provinces:
        print(f"  {province}")

    assert len(provinces) == 12

    # --------------------------------------------------------
    # 4. Five-year coverage
    # --------------------------------------------------------

    print("\n[4] TIME COVERAGE")

    years = sorted(df["fiscal_year"].unique())

    for year in years:
        count = (df["fiscal_year"] == year).sum()
        print(f"  {year}: {count}")

        assert count == 12

    assert len(years) == 5

    print("PASS")

    # --------------------------------------------------------
    # 5. One observation per province/year
    # --------------------------------------------------------

    print("\n[5] UNIQUENESS")

    duplicate_keys = df.duplicated(
        subset=[
            "Province/territory",
            "fiscal_year",
        ]
    ).sum()

    print(
        "Duplicate province-year observations: "
        f"{duplicate_keys}"
    )

    assert duplicate_keys == 0

    print("PASS")

    # --------------------------------------------------------
    # 6. Metric
    # --------------------------------------------------------

    print("\n[6] METRIC")

    print(df["metric"].value_counts().to_string())
    print(df["unit"].value_counts().to_string())

    assert df["metric"].eq(
        "Risk-adjusted rate"
    ).all()

    assert df["unit"].eq(
        "Percent"
    ).all()

    print("PASS")

    # --------------------------------------------------------
    # 7. Numeric validation
    # --------------------------------------------------------

    print("\n[7] NUMERIC FIELDS")

    numeric_columns = [
        "metric_value",
        "ci_lower",
        "ci_upper",
    ]

    for column in numeric_columns:

        numeric_count = df[column].notna().sum()

        print(
            f"{column}: "
            f"{numeric_count} numeric observations"
        )

        assert pd.api.types.is_numeric_dtype(
            df[column]
        )

    print("PASS")

    # --------------------------------------------------------
    # 8. Suppression
    # --------------------------------------------------------

    print("\n[8] SUPPRESSION")

    print(
        df["suppressed"]
        .value_counts()
        .to_string()
    )

    suppressed = df["suppressed"]

    assert suppressed.sum() == 15
    assert (~suppressed).sum() == 45

    # Suppressed records should have no numeric metric.
    assert df.loc[
        suppressed,
        "metric_value"
    ].isna().all()

    # Non-suppressed records should have numeric metric.
    assert df.loc[
        ~suppressed,
        "metric_value"
    ].notna().all()

    print("PASS")

    # --------------------------------------------------------
    # 9. Confidence intervals
    # --------------------------------------------------------

    print("\n[9] CONFIDENCE INTERVALS")

    for column in ["ci_lower", "ci_upper"]:

        suppressed_missing = df.loc[
            suppressed,
            column
        ].isna().all()

        print(
            f"{column}: "
            f"suppressed records missing = "
            f"{suppressed_missing}"
        )

        assert suppressed_missing

    # --------------------------------------------------------
    # 10. Logical CI checks
    # --------------------------------------------------------

    print("\n[10] CONFIDENCE INTERVAL LOGIC")

    valid_ci = df[
        df["metric_value"].notna()
        & df["ci_lower"].notna()
        & df["ci_upper"].notna()
    ]

    assert (
        valid_ci["ci_lower"]
        <= valid_ci["metric_value"]
    ).all()

    assert (
        valid_ci["metric_value"]
        <= valid_ci["ci_upper"]
    ).all()

    assert (
        valid_ci["ci_lower"]
        <= valid_ci["ci_upper"]
    ).all()

    print(
        f"Validated CI records: {len(valid_ci):,}"
    )

    print("PASS")

    # --------------------------------------------------------
    # 11. Value range
    # --------------------------------------------------------

    print("\n[11] RATE RANGE")

    observed = df["metric_value"].dropna()

    print(f"Minimum: {observed.min():.1f}%")
    print(f"Maximum: {observed.max():.1f}%")

    assert observed.between(0, 100).all()

    print("PASS")

    # --------------------------------------------------------
    # 12. Final validation
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("VALIDATION SUMMARY")
    print("=" * 75)

    print("""
PASS:
- 60 province-year observations
- 12 provinces/territories
- 5 fiscal years
- One observation per province/year
- Risk-adjusted rate correctly retained
- Percent unit confirmed
- Numeric metric fields confirmed
- CI fields validated
- Suppression correctly preserved
- Rates within valid 0–100% range

CLEAN DATASET IS READY FOR ANALYSIS.
""")

    print("=" * 75)


if __name__ == "__main__":
    main()