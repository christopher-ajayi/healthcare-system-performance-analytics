from pathlib import Path
import pandas as pd


# ============================================================
# CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS
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
    / "hip_fracture_surgery_within_48_hours_raw.csv"
)

TARGET_INDICATOR = "Hip Fracture Surgery Within 48 Hours"


def find_target_sheet():
    """Locate the workbook sheet containing the target indicator."""

    sheets = pd.read_excel(
        INPUT_FILE,
        sheet_name=None,
        dtype=object
    )

    matches = []

    for sheet_name, df in sheets.items():

        if df.empty:
            continue

        # Prefer an explicit indicator column
        indicator_columns = [
            col for col in df.columns
            if str(col).strip().lower() == "indicator"
        ]

        if indicator_columns:

            col = indicator_columns[0]

            mask = (
                df[col]
                .astype("string")
                .str.strip()
                .str.casefold()
                == TARGET_INDICATOR.casefold()
            )

            if mask.any():
                matches.append((sheet_name, df, mask))

    if not matches:
        raise ValueError(
            f"Could not locate '{TARGET_INDICATOR}' "
            f"in the CIHI Indicator Library workbook."
        )

    return matches[0]


def main():

    print("=" * 70)
    print("CIHI — HIP FRACTURE SURGERY WITHIN 48 HOURS")
    print("DATA ACQUISITION")
    print("=" * 70)

    print(f"\nInput:")
    print(INPUT_FILE)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input workbook not found:\n{INPUT_FILE}"
        )

    sheet_name, df, mask = find_target_sheet()

    print(f"\nSource sheet:")
    print(sheet_name)

    acquired = df.loc[mask].copy()

    print(f"\nAcquired rows: {len(acquired):,}")
    print(f"Columns: {len(acquired.columns):,}")

    print("\nColumns:")
    for column in acquired.columns:
        print(f"  - {column}")

    # --------------------------------------------------------
    # Basic acquisition-level checks
    # --------------------------------------------------------

    indicator_column = next(
        col for col in acquired.columns
        if str(col).strip().lower() == "indicator"
    )

    indicators = (
        acquired[indicator_column]
        .astype("string")
        .str.strip()
        .dropna()
        .unique()
    )

    if len(indicators) != 1:
        raise ValueError(
            "Acquisition contains unexpected indicators: "
            f"{list(indicators)}"
        )

    # --------------------------------------------------------
    # Save without analytical transformation
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    acquired.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nOutput:")
    print(OUTPUT_FILE)

    print("\nAcquisition complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()