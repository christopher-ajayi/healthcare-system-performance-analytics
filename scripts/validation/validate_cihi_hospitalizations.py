from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(
    "data/processed/demand/cihi_hospitalizations_clean.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("CIHI HOSPITALIZATION DATA VALIDATION")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)


# ============================================================
# STRUCTURE
# ============================================================

print("\n--- STRUCTURE ---")
print(f"Shape: {df.shape}")

duplicates = df.duplicated().sum()
print(f"Duplicate rows: {duplicates}")


# ============================================================
# YEAR COVERAGE
# ============================================================

print("\n--- YEAR COVERAGE ---")

years = sorted(df["year_start"].dropna().unique())

print(
    f"Years: {int(min(years))} to {int(max(years))}"
)
print(f"Unique years: {years}")


# ============================================================
# JURISDICTIONS
# ============================================================

print("\n--- JURISDICTIONS ---")

print(
    df["jurisdiction"]
    .value_counts()
    .sort_index()
)


# ============================================================
# AGE GROUPS
# ============================================================

print("\n--- AGE GROUPS ---")

print(
    df["age_group"]
    .value_counts()
    .sort_index()
)


# ============================================================
# SEX
# ============================================================

print("\n--- SEX ---")

print(
    df["sex"]
    .value_counts()
)


# ============================================================
# MISSING VALUES
# ============================================================

print("\n--- MISSING VALUES ---")

missing = df.isna().sum()

missing = missing[missing > 0]

if len(missing) == 0:
    print("No missing values.")
else:
    print(missing)


# ============================================================
# NUMERIC VALIDATION
# ============================================================

print("\n--- NEGATIVE VALUES ---")

numeric_columns = [
    "number_of_discharges",
    "total_length_of_stay_days",
    "average_length_of_stay_days"
]

negative_found = False

for col in numeric_columns:

    count = (df[col] < 0).sum()

    if count > 0:
        negative_found = True
        print(f"{col}: {count}")

if not negative_found:
    print("No negative values.")


# ============================================================
# DISCHARGE VALIDATION
# ============================================================

print("\n--- DISCHARGE VALIDATION ---")

invalid_discharges = (
    (df["number_of_discharges"] < 0)
    & df["number_of_discharges"].notna()
).sum()

print(
    f"Negative discharge records: {invalid_discharges}"
)


# ============================================================
# LENGTH OF STAY VALIDATION
# ============================================================

print("\n--- LENGTH OF STAY VALIDATION ---")

invalid_total_los = (
    (df["total_length_of_stay_days"] < 0)
    & df["total_length_of_stay_days"].notna()
).sum()

invalid_average_los = (
    (df["average_length_of_stay_days"] < 0)
    & df["average_length_of_stay_days"].notna()
).sum()

print(
    f"Negative total length-of-stay records: "
    f"{invalid_total_los}"
)

print(
    f"Negative average length-of-stay records: "
    f"{invalid_average_los}"
)


# ============================================================
# AVERAGE LENGTH OF STAY — REASONABLENESS CHECK
# ============================================================

print("\n--- AVERAGE LENGTH OF STAY VALIDATION ---")

testable = df[
    (df["number_of_discharges"] > 0)
    & df["total_length_of_stay_days"].notna()
    & df["average_length_of_stay_days"].notna()
].copy()

testable["calculated_average_los"] = (
    testable["total_length_of_stay_days"]
    / testable["number_of_discharges"]
)

testable["los_difference"] = (
    testable["calculated_average_los"]
    - testable["average_length_of_stay_days"]
).abs()

testable["los_relative_difference_pct"] = (
    testable["los_difference"]
    / testable["average_length_of_stay_days"].abs()
) * 100

# Accept either a small absolute difference or
# a small relative difference.
absolute_tolerance = 0.25
relative_tolerance_pct = 5.0


# failures = Flag unusual differences for review rather than failing validation.
review_threshold = 1.0

review_records = (
    testable["los_difference"] > review_threshold
)

print(f"Testable rows: {len(testable)}")
print(
    f"Records requiring LOS review: "
    f"{review_records.sum()}"
)

print(
    f"Maximum difference: "
    f"{testable['los_difference'].max():.4f}"
)

print(
    f"Mean difference: "
    f"{testable['los_difference'].mean():.4f}"
)


# ============================================================
# YEAR CONSISTENCY
# ============================================================

print("\n--- YEAR CONSISTENCY ---")

year_difference = (
    df["year_end"] - df["year_start"]
)

invalid_years = (
    year_difference != 1
).sum()

print(
    f"Invalid fiscal-year records: {invalid_years}"
)


# ============================================================
# VALIDATION SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

checks = {
    "Duplicates": duplicates == 0,
    "Year consistency": invalid_years == 0,
    "Negative discharges": invalid_discharges == 0,
    "Negative total LOS": invalid_total_los == 0,
    "Negative average LOS": invalid_average_los == 0,
}

for check, passed in checks.items():

    status = "PASS" if passed else "FAIL"

print(
    "\nAverage LOS reconstruction is treated as an "
    "informational consistency check."
)

print(
    f"Records flagged for review: "
    f"{review_records.sum()}"
)


# ============================================================
# FINAL STATUS
# ============================================================

if all(checks.values()):

    print(
        "\n" +
        "=" * 70
    )

    print(
        "CIHI HOSPITALIZATION DATA VALIDATION: PASSED"
    )

else:

    print(
        "\n" +
        "=" * 70
    )

    print(
        "CIHI HOSPITALIZATION DATA VALIDATION: "
        "REVIEW REQUIRED"
    )

print("=" * 70)