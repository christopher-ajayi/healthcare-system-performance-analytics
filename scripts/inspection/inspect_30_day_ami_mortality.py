from pathlib import Path
import pandas as pd


# ============================================================
# [1] CIHI — 30-DAY AMI MORTALITY
# INDICATOR DIAGNOSTIC
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "cihi_indicator_library.xlsx"
)


def main():

    print("=" * 75)
    print("CIHI — 30-DAY AMI MORTALITY")
    print("INDICATOR DIAGNOSTIC")
    print("=" * 75)

    # --------------------------------------------------------
    # [2] LOAD CIHI INDICATOR LIBRARY
    # --------------------------------------------------------

    print("\n[2] LOAD CIHI INDICATOR LIBRARY")

    print(f"Input: {INPUT_FILE}")

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="Sheet1",
        dtype=str
    )

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    # --------------------------------------------------------
    # [3] SEARCH ALL COLUMNS
    # --------------------------------------------------------

    print("\n[3] SEARCH ALL COLUMNS")

    search_terms = [
        "myocardial",
        "infarction",
        "ami",
        "mortality",
    ]

    mask = pd.Series(False, index=df.index)

    for term in search_terms:

        term_mask = (
            df.astype(str)
            .apply(
                lambda col: col.str.contains(
                    term,
                    case=False,
                    na=False,
                    regex=False
                )
            )
            .any(axis=1)
        )

        mask = mask | term_mask

    matches = df.loc[mask].copy()

    print(f"Matching rows: {len(matches):,}")

    # --------------------------------------------------------
    # [4] INDICATOR VALUES
    # --------------------------------------------------------

    print("\n[4] INDICATOR VALUES")

    indicator_counts = (
        matches["Indicator"]
        .value_counts()
    )

    if indicator_counts.empty:
        print("No matching indicators found.")
    else:
        for indicator, count in indicator_counts.items():
            print(f"  - {indicator}: {count:,}")

    # --------------------------------------------------------
    # [5] MORTALITY-RELATED INDICATORS
    # --------------------------------------------------------

    print("\n[5] MORTALITY-RELATED INDICATORS")

    mortality = (
        df["Indicator"]
        .dropna()
        .loc[
            df["Indicator"]
            .str.contains(
                "mortality|death|fatal",
                case=False,
                na=False,
                regex=True
            )
        ]
        .value_counts()
    )

    for indicator, count in mortality.items():
        print(f"  - {indicator}: {count:,}")

    # --------------------------------------------------------
    # [6] AMI-RELATED RECORDS
    # --------------------------------------------------------

    print("\n[6] AMI-RELATED INDICATORS")

    ami = (
        df["Indicator"]
        .dropna()
        .loc[
            df["Indicator"]
            .str.contains(
                "myocardial|infarction|AMI",
                case=False,
                na=False,
                regex=True
            )
        ]
        .value_counts()
    )

    for indicator, count in ami.items():
        print(f"  - {indicator}: {count:,}")

    print("\n" + "=" * 75)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()