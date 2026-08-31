from pathlib import Path
import pandas as pd


# ============================================================================
# CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs
# DATA ACQUISITION
# ============================================================================


# ============================================================================
# [1] INITIALIZE
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "cihi_indicator_library.xlsx"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "avoidable_hospitalizations_acscs_raw.csv"
)


def main():

    print("=" * 75)
    print("CIHI — AVOIDABLE HOSPITALIZATIONS / ACSCs")
    print("DATA ACQUISITION")
    print("=" * 75)


    # =========================================================================
    # [2] LOAD CIHI INDICATOR LIBRARY
    # =========================================================================

    print("\n[2] LOAD CIHI INDICATOR LIBRARY")

    print(f"Input: {INPUT_FILE}")

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="Sheet1",
        dtype=str
    )

    print(f"Source sheet: Sheet1")
    print(f"Source rows: {len(df):,}")
    print(f"Source columns: {len(df.columns):,}")


    # =========================================================================
    # [3] SEARCH AVOIDABLE HOSPITALIZATION / ACSC INDICATORS
    # =========================================================================

    print("\n[3] SEARCH AVOIDABLE HOSPITALIZATION / ACSC INDICATORS")

    search_terms = [
        "ambulatory care sensitive",
        "avoidable hospitalization",
        "avoidable hospital",
        "ACSC",
        "hospitalization"
    ]

    search_mask = pd.Series(False, index=df.index)

    for column in df.columns:

        column_text = (
            df[column]
            .fillna("")
            .astype(str)
        )

        for term in search_terms:

            search_mask |= column_text.str.contains(
                term,
                case=False,
                na=False,
                regex=False
            )

    matches = df.loc[search_mask].copy()

    if matches.empty:

        print("\nNo relevant indicators found.")

        raise SystemExit(1)

    indicator_counts = (
        matches["Indicator"]
        .dropna()
        .value_counts()
    )

    print("\nCandidate indicators:")

    for indicator, count in indicator_counts.items():

        print(f"  - {indicator}: {count:,}")


    # =========================================================================
    # [4] EXACT INDICATOR SELECTION
    # =========================================================================

    print("\n[4] EXACT INDICATOR SELECTION")

    SELECTED_INDICATOR = (
        "Ambulatory Care Sensitive Conditions Hospitalizations"
    )

    print(f"Expected: {SELECTED_INDICATOR}")

    exact_matches = df[
        df["Indicator"].eq(SELECTED_INDICATOR)
    ].copy()

    if exact_matches.empty:

        print("\nEXACT INDICATOR NOT FOUND.")
        print(f"Expected: {SELECTED_INDICATOR}")

        print("\nAvailable candidates:")

        for indicator, count in indicator_counts.items():

            print(f"  - {indicator}: {count:,}")

        raise SystemExit(1)


    # =========================================================================
    # [5] ACQUIRE RECORDS
    # =========================================================================

    print("\n[5] ACQUIRE RECORDS")

    acquired = exact_matches.copy()

    print(f"Selected indicator: {SELECTED_INDICATOR}")
    print(f"Acquired rows: {len(acquired):,}")
    print(f"Columns: {len(acquired.columns):,}")


    # =========================================================================
    # [6] SAVE RAW DATA
    # =========================================================================

    print("\n[6] SAVE RAW DATA")

    acquired.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nAcquisition complete.")
    print("=" * 75)


# ============================================================================
# [7] RUN
# ============================================================================

if __name__ == "__main__":
    main()