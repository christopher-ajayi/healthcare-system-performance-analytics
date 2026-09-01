from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "capacity"
    / "cihi_hospital_beds_2024_2025.xlsx"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "capacity"
    / "cihi_hospital_beds_current_clean.csv"
)


# ============================================================
# LOAD WORKBOOK
# ============================================================

if not RAW_FILE.exists():
    raise FileNotFoundError(
        f"File not found:\n{RAW_FILE}"
    )

xls = pd.ExcelFile(RAW_FILE)

print("=" * 70)
print("CIHI CURRENT HOSPITAL BEDS CLEANING")
print("=" * 70)

print(f"\nInput:")
print(RAW_FILE)

print(f"\nSheets found: {len(xls.sheet_names)}")
print(xls.sheet_names)


# ============================================================
# READ RELEVANT TABLE
# ============================================================

frames = []

for sheet_name in xls.sheet_names:

    df = pd.read_excel(
        RAW_FILE,
        sheet_name=sheet_name,
        header=None
    )

    df = df.dropna(
        axis=0,
        how="all"
    )

    df = df.dropna(
        axis=1,
        how="all"
    )

    if df.empty:
        continue

    # Locate rows containing province/jurisdiction information.
    # Current CIHI files may use different labels such as:
    # Province, Territory, Jurisdiction, or Canada.

    text = df.astype(str)

    mask = text.apply(
        lambda row: row.str.contains(
            "Alberta|British Columbia|Manitoba|Ontario|Quebec|"
            "Saskatchewan|Nova Scotia|New Brunswick|"
            "Newfoundland|Prince Edward Island|Yukon|"
            "Northwest Territories|Nunavut|Canada",
            case=False,
            regex=True
        ).any(),
        axis=1
    )

    candidate = df.loc[mask].copy()

    if not candidate.empty:
        candidate["source_sheet"] = sheet_name
        frames.append(candidate)


if not frames:
    raise ValueError(
        "No province/territory hospital-bed records were found "
        "in the workbook."
    )


# ============================================================
# COMBINE CANDIDATE DATA
# ============================================================

clean_df = pd.concat(
    frames,
    ignore_index=True
)


# ============================================================
# REMOVE COMPLETELY EMPTY ROWS/COLUMNS
# ============================================================

clean_df = clean_df.dropna(
    axis=0,
    how="all"
)

clean_df = clean_df.dropna(
    axis=1,
    how="all"
)


# ============================================================
# STANDARDIZE TEXT
# ============================================================

for column in clean_df.columns:

    if clean_df[column].dtype == "object":

        clean_df[column] = (
            clean_df[column]
            .astype(str)
            .str.strip()
            .replace(
                {
                    "nan": pd.NA,
                    "NaN": pd.NA,
                    "": pd.NA,
                    "—": pd.NA,
                    "..": pd.NA,
                }
            )
        )


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

clean_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 70)
print("CIHI CURRENT HOSPITAL BEDS CLEANING COMPLETE")
print("=" * 70)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(f"\nRows: {len(clean_df):,}")

print("\nColumns:")
print(clean_df.columns.tolist())

print("\nMissing values:")
print(clean_df.isna().sum())