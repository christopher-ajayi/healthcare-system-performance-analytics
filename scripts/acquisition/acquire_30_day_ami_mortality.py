from pathlib import Path
import pandas as pd


# ============================================================
# [1] CIHI — 30-DAY AMI MORTALITY
# DATA ACQUISITION
# ============================================================

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
    / "30_day_ami_mortality_raw.csv"
)

SELECTED_INDICATOR = (
    "30-Day Acute Myocardial Infarction In-Hospital Mortality"
)


def main():

    print("=" * 75)
    print("CIHI — 30-DAY AMI MORTALITY")
    print("DATA ACQUISITION")
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

    print("Source sheet: Sheet1")
    print(f"Source rows: {len(df):,}")
    print(f"Source columns: {len(df.columns):,}")

    # --------------------------------------------------------
    # [3] EXACT INDICATOR SELECTION
    # --------------------------------------------------------

    print("\n[3] EXACT INDICATOR SELECTION")

    acquired = df[
        df["Indicator"].eq(SELECTED_INDICATOR)
    ].copy()

    if acquired.empty:
        raise ValueError(
            f"\nEXACT INDICATOR NOT FOUND.\n"
            f"Expected: {SELECTED_INDICATOR}\n"
            f"\nCheck the CIHI Indicator Library for the "
            f"current indicator name."
        )

    print(f"Selected indicator: {SELECTED_INDICATOR}")
    print(f"Acquired rows: {len(acquired):,}")
    print(f"Columns: {len(acquired.columns):,}")

    # --------------------------------------------------------
    # [4] VERIFY INDICATOR
    # --------------------------------------------------------

    print("\n[4] VERIFY INDICATOR")

    indicators = (
        acquired["Indicator"]
        .dropna()
        .unique()
    )

    print("Indicators acquired:")

    for indicator in indicators:
        print(f"  - {indicator}")

    if len(indicators) != 1:
        raise ValueError(
            "Acquisition contains more than one indicator."
        )

    if indicators[0] != SELECTED_INDICATOR:
        raise ValueError(
            "Acquired indicator does not match the "
            "selected indicator."
        )

    print("PASS — exact indicator confirmed.")

    # --------------------------------------------------------
    # [5] SAVE RAW DATA
    # --------------------------------------------------------

    print("\n[5] SAVE RAW DATA")

    acquired.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("Output:")
    print(OUTPUT_FILE)

    print("\nAcquisition complete.")
    print("=" * 75)


if __name__ == "__main__":
    main()