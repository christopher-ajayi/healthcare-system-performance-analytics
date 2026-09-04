from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "capacity"
    / "cihi_hospital_beds_clean.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"File not found:\n{INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)


# ============================================================
# VALIDATION SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CIHI HOSPITAL BEDS VALIDATION")
print("=" * 70)

print(f"\nRows: {len(df):,}")
print(f"Columns: {list(df.columns)}")


# ============================================================
# 1. REQUIRED COLUMNS
# ============================================================

required_columns = {
    "year",
    "fiscal_year",
    "province",
    "total_beds",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {sorted(missing_columns)}"
    )

print("\n[PASS] Required columns present.")


# ============================================================
# 2. YEAR VALIDATION
# ============================================================

expected_years = set(range(2009, 2023))
actual_years = set(df["year"].dropna().astype(int))

unexpected_years = actual_years - expected_years
missing_years = expected_years - actual_years

if unexpected_years:
    raise ValueError(
        f"Unexpected years found: {sorted(unexpected_years)}"
    )

if missing_years:
    print(
        f"[WARNING] Missing years from dataset: "
        f"{sorted(missing_years)}"
    )
else:
    print("[PASS] Year range is 2009–2022.")


# ============================================================
# 3. FISCAL YEAR VALIDATION
# ============================================================

invalid_fiscal_years = df[
    ~df["fiscal_year"].astype(str).str.match(
        r"^\d{4}–\d{4}$",
        na=False
    )
]

if not invalid_fiscal_years.empty:
    raise ValueError(
        "Invalid fiscal-year values detected."
    )

print("[PASS] Fiscal-year format is valid.")


# ============================================================
# 4. YEAR / FISCAL YEAR CONSISTENCY
# ============================================================

expected_fiscal_year = (
    df["year"].astype(int).astype(str)
    + "–"
    + (df["year"].astype(int) + 1).astype(str)
)

inconsistent_years = df[
    df["fiscal_year"] != expected_fiscal_year
]

if not inconsistent_years.empty:
    raise ValueError(
        "Year and fiscal_year are inconsistent."
    )

print("[PASS] Year and fiscal-year values are consistent.")


# ============================================================
# 5. DUPLICATE CHECK
# ============================================================

duplicates = df[
    df.duplicated(
        subset=["province", "year"],
        keep=False
    )
]

if not duplicates.empty:
    raise ValueError(
        "Duplicate province-year combinations detected:\n"
        f"{duplicates.to_string(index=False)}"
    )

print("[PASS] No duplicate province-year combinations.")


# ============================================================
# 6. JURISDICTION COVERAGE
# ============================================================

expected_jurisdictions = {
    "Alberta",
    "British Columbia",
    "Manitoba",
    "New Brunswick",
    "Newfoundland and Labrador",
    "Nova Scotia",
    "Ontario",
    "Prince Edward Island",
    "Quebec",
    "Saskatchewan",
    "Yukon",
    "Northwest Territories",
    "Canada",
}

actual_jurisdictions = set(df["province"].unique())

missing_jurisdictions = (
    expected_jurisdictions - actual_jurisdictions
)

unexpected_jurisdictions = (
    actual_jurisdictions - expected_jurisdictions
)

if missing_jurisdictions:
    raise ValueError(
        f"Missing jurisdictions: {sorted(missing_jurisdictions)}"
    )

if unexpected_jurisdictions:
    raise ValueError(
        f"Unexpected jurisdictions: {sorted(unexpected_jurisdictions)}"
    )

print("[PASS] Expected jurisdictions are present.")


# ============================================================
# 7. OBSERVATION COUNTS
# ============================================================

observation_counts = (
    df.groupby("province")["year"]
    .nunique()
)

print("\nObservations per jurisdiction:")
print(observation_counts.to_string())

if (observation_counts != 14).any():
    print(
        "\n[WARNING] One or more jurisdictions do not "
        "have all 14 years."
    )
else:
    print("[PASS] Each jurisdiction has 14 years.")


# ============================================================
# 8. MISSING BED VALUES
# ============================================================

missing_beds = df[df["total_beds"].isna()]

print(
    f"\nMissing total_beds values: "
    f"{len(missing_beds)}"
)

if not missing_beds.empty:
    print("\nMissing observations:")
    print(
        missing_beds[
            ["year", "fiscal_year", "province"]
        ].to_string(index=False)
    )


# ============================================================
# 9. NEGATIVE BED VALUES
# ============================================================

negative_beds = df[
    df["total_beds"].notna()
    & (df["total_beds"] < 0)
]

if not negative_beds.empty:
    raise ValueError(
        "Negative bed counts detected."
    )

print("[PASS] No negative bed counts.")


# ============================================================
# 10. DATA TYPES
# ============================================================

if not pd.api.types.is_numeric_dtype(df["year"]):
    raise ValueError("year is not numeric.")

if not pd.api.types.is_numeric_dtype(df["total_beds"]):
    raise ValueError("total_beds is not numeric.")

print("[PASS] Numeric fields have valid data types.")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)

if missing_beds.empty:
    print("VALIDATION STATUS: PASSED")
else:
    print(
        "VALIDATION STATUS: PASSED WITH "
        "MISSING VALUES REQUIRING REVIEW"
    )

print("=" * 70)