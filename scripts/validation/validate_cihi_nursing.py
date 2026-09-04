import pandas as pd
from pathlib import Path


INPUT = Path("data/processed/workforce/cihi_nursing_transformed.csv")
TOLERANCE = 0.01

df = pd.read_csv(INPUT)

print("=" * 70)
print("CIHI NURSING DATA VALIDATION")
print("=" * 70)


# =========================================================
# HELPERS
# =========================================================

results = {}


def validate_reconciliation(name, calculated, actual):
    valid = calculated.notna() & actual.notna()

    if valid.sum() == 0:
        print(f"{name:<35} NOT TESTABLE")
        results[name] = True
        return

    difference = (calculated[valid] - actual[valid]).abs()

    failures = (difference > TOLERANCE).sum()

    print(
        f"{name:<35}"
        f"{'PASS' if failures == 0 else 'REVIEW'}"
    )
    print(f"  Testable rows: {valid.sum()}")
    print(f"  Failures: {failures}")
    print(f"  Maximum difference: {difference.max()}")

    results[name] = failures == 0


def validate_derived(name, expected, actual):
    valid = expected.notna() & actual.notna()

    if valid.sum() == 0:
        print(f"{name:<35} NOT TESTABLE")
        results[name] = True
        return

    difference = (expected[valid] - actual[valid]).abs()

    failures = (difference > TOLERANCE).sum()

    print(
        f"{name:<35}"
        f"{'PASS' if failures == 0 else 'REVIEW'}"
    )
    print(f"  Testable rows: {valid.sum()}")
    print(f"  Failures: {failures}")
    print(f"  Maximum difference: {difference.max()}")

    results[name] = failures == 0


# =========================================================
# 1. STRUCTURE
# =========================================================

print("\n--- STRUCTURE ---")

print("Shape:", df.shape)

duplicates = df.duplicated().sum()
print("Duplicate rows:", duplicates)

results["Duplicates"] = duplicates == 0


# =========================================================
# 2. YEAR COVERAGE
# =========================================================

print("\n--- YEAR COVERAGE ---")

print("Years:", df["year"].min(), "to", df["year"].max())
print("Unique years:", sorted(df["year"].dropna().unique()))


# =========================================================
# 3. PROFESSIONS
# =========================================================

print("\n--- PROFESSIONS ---")

print(
    df["profession"]
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# 4. JURISDICTIONS
# =========================================================

print("\n--- JURISDICTIONS ---")

print(
    df["jurisdiction"]
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# 5. WORKPLACES
# =========================================================

print("\n--- WORKPLACES ---")

print(
    df["workplace"]
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# 6. MISSING VALUES
# =========================================================

print("\n--- MISSING VALUES ---")

missing = df.isna().sum()
missing = missing[missing > 0]

print(
    missing.to_string()
    if not missing.empty
    else "None"
)


# =========================================================
# 7. NEGATIVE VALUES
# =========================================================

print("\n--- NEGATIVE VALUES ---")

numeric = df.select_dtypes(include="number")

negative = numeric.lt(0).sum()
negative = negative[negative > 0]

print(
    negative.to_string()
    if not negative.empty
    else "None"
)


# =========================================================
# 8. SEX TOTALS
# =========================================================

print("\n--- SEX TOTALS ---")

sex_total = (
    df["female"]
    + df["male"]
    + df["sex_unknown"]
)

validate_reconciliation(
    "Sex totals",
    sex_total,
    df["total_workforce"],
)


# =========================================================
# 9. AGE TOTALS
# =========================================================

print("\n--- AGE TOTALS ---")

age_columns = [
    "age_under_25",
    "age_25_29",
    "age_30_34",
    "age_35_39",
    "age_40_44",
    "age_45_49",
    "age_50_54",
    "age_55_59",
    "age_60_64",
    "age_65_69",
    "age_70_plus",
    "age_unknown",
]

age_total = df[age_columns].sum(
    axis=1,
    min_count=len(age_columns),
)

validate_reconciliation(
    "Age totals",
    age_total,
    df["total_workforce"],
)


# =========================================================
# 10. GRADUATION TOTALS
# =========================================================

print("\n--- GRADUATION TOTALS ---")

graduation_total = df[
    [
        "canadian_graduates",
        "international_graduates",
        "graduation_location_unknown",
    ]
].sum(
    axis=1,
    min_count=3,
)

validate_reconciliation(
    "Graduation totals",
    graduation_total,
    df["total_workforce"],
)


# =========================================================
# 11. EMPLOYMENT STATUS
# =========================================================

print("\n--- EMPLOYMENT STATUS ---")

employment_total = df[
    [
        "full_time",
        "part_time",
        "casual",
        "employment_status_unknown",
    ]
].sum(
    axis=1,
    min_count=4,
)

validate_reconciliation(
    "Employment totals",
    employment_total,
    df["total_workforce"],
)


# =========================================================
# 12. POSITION
# =========================================================

print("\n--- POSITION ---")

position_total = df[
    [
        "manager",
        "staff_nurse",
        "position_not_stated",
        "other_position",
    ]
].sum(
    axis=1,
    min_count=4,
)

validate_reconciliation(
    "Position totals",
    position_total,
    df["total_workforce"],
)


# =========================================================
# 13. RESPONSIBILITY
# =========================================================

print("\n--- RESPONSIBILITY ---")

responsibility_total = df[
    [
        "administration",
        "direct_care",
        "education",
        "research",
        "responsibility_not_stated",
    ]
].sum(
    axis=1,
    min_count=5,
)

validate_reconciliation(
    "Responsibility totals",
    responsibility_total,
    df["total_workforce"],
)


# =========================================================
# 14. LOCATION
# =========================================================

print("\n--- RURAL / URBAN ---")

location_total = df[
    [
        "rural",
        "urban",
        "geography_unknown",
    ]
].sum(
    axis=1,
    min_count=3,
)

validate_reconciliation(
    "Location totals",
    location_total,
    df["total_workforce"],
)


# =========================================================
# 15. FEMALE SHARE
# =========================================================

print("\n--- DERIVED METRICS ---")

female_share = (
    df["female"]
    / df["total_workforce"]
    * 100
)

validate_derived(
    "Female share",
    female_share,
    df["female_share_pct"],
)


# =========================================================
# 16. INTERNATIONAL GRADUATE SHARE
# =========================================================

international_share = (
    df["international_graduates"]
    / df["total_workforce"]
    * 100
)

validate_derived(
    "International graduate share",
    international_share,
    df["international_graduate_share_pct"],
)


# =========================================================
# 17. AGE 65+ SHARE
# =========================================================

age_65_plus_share = (
    df["age_65_plus"]
    / df["total_workforce"]
    * 100
)

validate_derived(
    "65+ share",
    age_65_plus_share,
    df["age_65_plus_share_pct"],
)


# =========================================================
# 18. RURAL SHARE
# =========================================================

rural_share = (
    df["rural"]
    / df["total_workforce"]
    * 100
)

validate_derived(
    "Rural share",
    rural_share,
    df["rural_share_pct"],
)


# =========================================================
# 19. DIRECT CARE SHARE
# =========================================================

direct_care_share = (
    df["direct_care"]
    / df["total_workforce"]
    * 100
)

validate_derived(
    "Direct care share",
    direct_care_share,
    df["direct_care_share_pct"],
)


# =========================================================
# 20. YOY VALIDATION
# =========================================================

print("\n--- YOY VALIDATION ---")

sort_columns = [
    "jurisdiction",
    "profession",
    "workplace",
    "year",
]

df = df.sort_values(sort_columns)

group_columns = [
    "jurisdiction",
    "profession",
    "workplace",
]

expected_yoy = (
    df.groupby(group_columns)["total_workforce"]
    .diff()
)

validate_derived(
    "YoY workforce change",
    expected_yoy,
    df["workforce_yoy_change"],
)


# =========================================================
# 21. YOY GROWTH %
# =========================================================

previous_workforce = (
    df.groupby(group_columns)["total_workforce"]
    .shift(1)
)

expected_growth = (
    expected_yoy
    / previous_workforce
    * 100
)

validate_derived(
    "YoY workforce growth",
    expected_growth,
    df["workforce_yoy_growth_pct"],
)


# =========================================================
# 22. FINAL SUMMARY
# =========================================================

print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

for name, passed in results.items():
    print(
        f"{name:<35}"
        f"{'PASS' if passed else 'REVIEW'}"
    )

print("\n" + "=" * 70)

if all(results.values()):
    print("CIHI NURSING DATA VALIDATION: PASSED")
else:
    print("CIHI NURSING DATA VALIDATION: REVIEW REQUIRED")

print("=" * 70)