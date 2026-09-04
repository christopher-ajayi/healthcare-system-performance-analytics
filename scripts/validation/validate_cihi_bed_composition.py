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
    / "cihi_hospital_bed_composition_transformed.csv"
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
# EXPECTED STRUCTURE
# ============================================================

EXPECTED_COLUMNS = [
    "year",
    "fiscal_year",
    "province",
    "icu_beds",
    "obstetrics_beds",
    "pediatrics_beds",
    "mental_health_addictions_beds",
    "rehabilitation_beds",
    "long_term_care_beds",
    "other_acute_care_beds",
    "rated_bed_capacity",
]

JURISDICTIONS = [
    "Alberta",
    "British Columbia",
    "Manitoba",
    "New Brunswick",
    "Newfoundland and Labrador",
    "Northwest Territories",
    "Nova Scotia",
    "Ontario",
    "Prince Edward Island",
    "Quebec",
    "Saskatchewan",
    "Yukon",
]

BED_COLUMNS = [
    "icu_beds",
    "obstetrics_beds",
    "pediatrics_beds",
    "mental_health_addictions_beds",
    "rehabilitation_beds",
    "long_term_care_beds",
    "other_acute_care_beds",
    "rated_bed_capacity",
]


# ============================================================
# VALIDATION STATUS
# ============================================================

passed = True
review_items = []


# ============================================================
# 1. COLUMN VALIDATION
# ============================================================

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in df.columns
]

unexpected_columns = [
    column
    for column in df.columns
    if column not in EXPECTED_COLUMNS
]

if missing_columns:
    passed = False
    review_items.append(
        f"Missing expected columns: {missing_columns}"
    )

if unexpected_columns:
    review_items.append(
        f"Unexpected columns: {unexpected_columns}"
    )


# ============================================================
# 2. ROW COUNT
# ============================================================

if len(df) != 166:
    passed = False
    review_items.append(
        f"Expected 166 rows, found {len(df)}"
    )


# ============================================================
# 3. JURISDICTION COVERAGE
# ============================================================

actual_jurisdictions = sorted(
    df["province"].dropna().unique()
)

unexpected_jurisdictions = sorted(
    set(actual_jurisdictions)
    - set(JURISDICTIONS)
)

missing_jurisdictions = sorted(
    set(JURISDICTIONS)
    - set(actual_jurisdictions)
)

if unexpected_jurisdictions:
    passed = False
    review_items.append(
        f"Unexpected jurisdictions: {unexpected_jurisdictions}"
    )

if missing_jurisdictions:
    passed = False
    review_items.append(
        f"Missing jurisdictions: {missing_jurisdictions}"
    )


# ============================================================
# 4. YEAR RANGE
# ============================================================

if df["year"].min() != 2009:
    passed = False
    review_items.append(
        f"Unexpected minimum year: {df['year'].min()}"
    )

if df["year"].max() != 2022:
    passed = False
    review_items.append(
        f"Unexpected maximum year: {df['year'].max()}"
    )


# ============================================================
# 5. DUPLICATE PROVINCE-YEAR RECORDS
# ============================================================

duplicates = df[
    df.duplicated(
        subset=["province", "year"],
        keep=False
    )
]

if not duplicates.empty:
    passed = False
    review_items.append(
        f"Duplicate province-year records: "
        f"{len(duplicates)} rows"
    )


# ============================================================
# 6. YEAR SEQUENCE BY JURISDICTION
# ============================================================

sequence_issues = []

for province, group in df.groupby("province"):

    years = sorted(group["year"].tolist())

    expected = list(
        range(
            min(years),
            max(years) + 1
        )
    )

    if years != expected:
        sequence_issues.append(
            {
                "province": province,
                "years": years,
                "missing_years": sorted(
                    set(expected) - set(years)
                ),
            }
        )

if sequence_issues:
    review_items.append(
        f"Year sequence issues detected: "
        f"{len(sequence_issues)} jurisdictions"
    )


# ============================================================
# 7. NEGATIVE BED VALUES
# ============================================================

negative_values = {}

for column in BED_COLUMNS:

    count = (
        df[column]
        .lt(0)
        .sum()
    )

    if count > 0:
        negative_values[column] = int(count)

if negative_values:
    passed = False
    review_items.append(
        f"Negative bed values found: "
        f"{negative_values}"
    )


# ============================================================
# 8. ZERO VALUES
# ============================================================

zero_values = {}

for column in BED_COLUMNS:

    count = (
        df[column]
        .eq(0)
        .sum()
    )

    if count > 0:
        zero_values[column] = int(count)


# ============================================================
# 9. MISSING VALUES
# ============================================================

missing_values = (
    df[EXPECTED_COLUMNS]
    .isna()
    .sum()
)


# ============================================================
# 10. MISSING VALUES BY JURISDICTION
# ============================================================

missing_by_province = (
    df.groupby("province")[BED_COLUMNS]
    .apply(lambda x: x.isna().sum())
)


# ============================================================
# 11. RATED BED CAPACITY REVIEW
# ============================================================

rated_missing = int(
    df["rated_bed_capacity"].isna().sum()
)

rated_available = int(
    df["rated_bed_capacity"].notna().sum()
)


# ============================================================
# 12. ROW COUNT BY JURISDICTION
# ============================================================

rows_by_province = (
    df.groupby("province")
    .size()
    .sort_index()
)


# ============================================================
# OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("CIHI HOSPITAL BED COMPOSITION VALIDATION")
print("=" * 70)

print(f"\nInput:")
print(INPUT_FILE)

print(f"\nRows: {len(df)}")

print(
    f"Year range: "
    f"{df['year'].min()}–{df['year'].max()}"
)

print(
    f"Jurisdictions: "
    f"{df['province'].nunique()}"
)


print("\n" + "-" * 70)
print("ROWS BY JURISDICTION")
print("-" * 70)

print(rows_by_province.to_string())


print("\n" + "-" * 70)
print("MISSING VALUES")
print("-" * 70)

print(missing_values.to_string())


print("\n" + "-" * 70)
print("MISSING VALUES BY JURISDICTION")
print("-" * 70)

print(missing_by_province.to_string())


print("\n" + "-" * 70)
print("ZERO VALUES")
print("-" * 70)

if zero_values:
    print(pd.Series(zero_values).to_string())
else:
    print("None")


print("\n" + "-" * 70)
print("RATED BED CAPACITY")
print("-" * 70)

print(f"Available: {rated_available}")
print(f"Missing:   {rated_missing}")


print("\n" + "-" * 70)
print("DUPLICATES")
print("-" * 70)

print(
    f"Duplicate province-year rows: "
    f"{len(duplicates)}"
)


print("\n" + "-" * 70)
print("VALIDATION RESULT")
print("-" * 70)

if passed and not review_items:

    print("PASSED")

else:

    print("PASSED WITH REVIEW ITEMS")

    for item in review_items:
        print(f"- {item}")


print("\n" + "=" * 70)