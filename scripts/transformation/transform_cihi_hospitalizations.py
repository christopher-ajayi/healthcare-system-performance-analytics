from pathlib import Path
import pandas as pd


# ============================================================
# CIHI HOSPITALIZATION DATA TRANSFORMATION
# ============================================================

INPUT_FILE = Path(
    "data/processed/demand/cihi_hospitalizations_clean.csv"
)

OUTPUT_FILE = Path(
    "data/processed/demand/cihi_hospitalizations_transformed.csv"
)


def main():

    print("=" * 70)
    print("CIHI HOSPITALIZATION DATA TRANSFORMATION")
    print("=" * 70)

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------
    df = pd.read_csv(INPUT_FILE)

    print("\nInput:")
    print(INPUT_FILE)

    # --------------------------------------------------------
    # STANDARDIZE COLUMN NAMES
    # --------------------------------------------------------
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # --------------------------------------------------------
    # FISCAL YEAR
    # --------------------------------------------------------
    if "year" in df.columns:
        df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce"
    ).astype("Int64")

    elif "fiscal_year" in df.columns:
        df["year"] = pd.to_numeric(
        df["fiscal_year"],
        errors="coerce"
    ).astype("Int64")

    elif "discharge_fiscal_year" in df.columns:
        df["year"] = pd.to_numeric(
        df["discharge_fiscal_year"],
        errors="coerce"
    ).astype("Int64")

    else:
        raise ValueError(
        f"No year column found. Available columns: {df.columns.tolist()}"
    )

    # --------------------------------------------------------
    # NUMERIC COLUMNS
    # --------------------------------------------------------
    numeric_columns = [
        "number_of_discharges",
        "total_length_of_stay_days",
        "average_length_of_stay_days",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # SORT DATA
    # --------------------------------------------------------
    sort_columns = [
        column
        for column in [
            "jurisdiction",
            "age_group",
            "sex",
            "year"
        ]
        if column in df.columns
    ]

    df = df.sort_values(sort_columns).reset_index(drop=True)

    # --------------------------------------------------------
    # YEAR-OVER-YEAR DISCHARGE CHANGE
    # --------------------------------------------------------
    if "number_of_discharges" in df.columns:

        group_columns = [
            column
            for column in [
                "jurisdiction",
                "age_group",
                "sex"
            ]
            if column in df.columns
        ]

        df["discharges_yoy_change"] = (
            df.groupby(group_columns)["number_of_discharges"]
            .diff()
        )

        previous_discharges = (
            df.groupby(group_columns)["number_of_discharges"]
            .shift(1)
        )

        df["discharges_yoy_growth_pct"] = (
            (
                df["number_of_discharges"]
                - previous_discharges
            )
            / previous_discharges
        ) * 100

    # --------------------------------------------------------
    # YEAR-OVER-YEAR TOTAL LENGTH OF STAY CHANGE
    # --------------------------------------------------------
    if "total_length_of_stay_days" in df.columns:

        previous_los = (
            df.groupby(group_columns)["total_length_of_stay_days"]
            .shift(1)
        )

        df["total_los_yoy_change"] = (
            df["total_length_of_stay_days"]
            - previous_los
        )

        df["total_los_yoy_growth_pct"] = (
            (
                df["total_length_of_stay_days"]
                - previous_los
            )
            / previous_los
        ) * 100

    # --------------------------------------------------------
    # ROUND DERIVED METRICS
    # --------------------------------------------------------
    percentage_columns = [
        "discharges_yoy_growth_pct",
        "total_los_yoy_growth_pct",
    ]

    for column in percentage_columns:
        if column in df.columns:
            df[column] = df[column].round(2)

    if "average_length_of_stay_days" in df.columns:
        df["average_length_of_stay_days"] = (
            df["average_length_of_stay_days"].round(2)
        )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------
    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nShape:")
    print(df.shape)

    print("\nYears:")
    print(
        f"{df['year'].min()}–{df['year'].max()}"
    )

    if "jurisdiction" in df.columns:
        print("\nJurisdictions:")
        print(df["jurisdiction"].nunique())

    if "age_group" in df.columns:
        print("\nAge groups:")
        print(df["age_group"].nunique())

    if "sex" in df.columns:
        print("\nSex:")
        print(df["sex"].unique())

    print("\nDerived metrics:")

    derived_columns = [
        "discharges_yoy_change",
        "discharges_yoy_growth_pct",
        "total_los_yoy_change",
        "total_los_yoy_growth_pct",
    ]

    for column in derived_columns:
        if column in df.columns:
            print(f"  - {column}")

    print("\n" + "=" * 70)
    print("CIHI HOSPITALIZATION DATA TRANSFORMATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()