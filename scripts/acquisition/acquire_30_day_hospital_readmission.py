from pathlib import Path
import pandas as pd


# ============================================================
# CIHI — 30-DAY HOSPITAL READMISSION
# DATA ACQUISITION
# ============================================================


# ============================================================
# 1. CONFIGURATION
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
    / "30_day_hospital_readmission_raw.csv"
)

SELECTED_INDICATOR = "All Patients Readmitted to Hospital"


# ============================================================
# 2. LOAD SOURCE DATA
# ============================================================

def load_source_data():

    print("=" * 75)
    print("CIHI — 30-DAY HOSPITAL READMISSION")
    print("DATA ACQUISITION")
    print("=" * 75)

    print("\nInput:")
    print(INPUT_FILE)

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="Sheet1",
        dtype=str
    )

    print("\nSource sheet: Sheet1")
    print(f"Source rows: {len(df):,}")
    print(f"Source columns: {len(df.columns):,}")

    return df


# ============================================================
# 3. SELECT INDICATOR
# ============================================================

def select_indicator(df):

    acquired = df[
        df["Indicator"].eq(SELECTED_INDICATOR)
    ].copy()

    if acquired.empty:
        raise ValueError(
            f"Indicator not found: {SELECTED_INDICATOR}"
        )

    print("\nSelected indicator:")
    print(f"  {SELECTED_INDICATOR}")

    return acquired


# ============================================================
# 4. ACQUIRE DATA
# ============================================================

def acquire_data(df):

    print(f"\nAcquired rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    return df


# ============================================================
# 5. SAVE OUTPUT
# ============================================================

def save_output(df):

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nAcquisition complete.")
    print("=" * 75)


# ============================================================
# 6. MAIN EXECUTION
# ============================================================

def main():

    source_data = load_source_data()

    acquired_data = select_indicator(
        source_data
    )

    acquired_data = acquire_data(
        acquired_data
    )

    save_output(
        acquired_data
    )


if __name__ == "__main__":
    main()