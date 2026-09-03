import pandas as pd
from pathlib import Path


INPUT = Path("data/processed/workforce/cihi_nursing_clean.csv")
OUTPUT = Path("data/processed/workforce/cihi_nursing_transformed.csv")


df = pd.read_csv(INPUT)


# ---------------------------------------------------------
# 1. Standardize column names
# ---------------------------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)


# ---------------------------------------------------------
# 2. Derived workforce measures
# ---------------------------------------------------------

df["female_share_pct"] = (
    df["female"] / df["total_workforce"] * 100
)

df["international_graduate_share_pct"] = (
    df["international_graduates"] / df["total_workforce"] * 100
)

df["age_65_plus"] = (
    df["age_65_69"].fillna(0)
    + df["age_70_plus"].fillna(0)
)

df["age_65_plus_share_pct"] = (
    df["age_65_plus"] / df["total_workforce"] * 100
)

df["rural_share_pct"] = (
    df["rural"] / df["total_workforce"] * 100
)

df["direct_care_share_pct"] = (
    df["direct_care"] / df["total_workforce"] * 100
)


# ---------------------------------------------------------
# 3. Year-over-year workforce change
# ---------------------------------------------------------

df = df.sort_values(
    ["jurisdiction", "profession", "workplace", "year"]
)

group_cols = [
    "jurisdiction",
    "profession",
    "workplace"
]

df["workforce_yoy_change"] = (
    df.groupby(group_cols)["total_workforce"]
    .diff()
)

previous_workforce = (
    df.groupby(group_cols)["total_workforce"]
    .shift(1)
)

df["workforce_yoy_growth_pct"] = (
    df["workforce_yoy_change"]
    / previous_workforce
    * 100
)


# ---------------------------------------------------------
# 4. Reorder columns
# ---------------------------------------------------------

preferred = [
    "year",
    "jurisdiction",
    "profession",
    "workplace",
    "total_workforce",

    "workforce_yoy_change",
    "workforce_yoy_growth_pct",

    "female",
    "male",
    "sex_unknown",
    "female_share_pct",

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
    "age_65_plus",
    "age_65_plus_share_pct",
    "age_unknown",

    "canadian_graduates",
    "international_graduates",
    "graduation_location_unknown",
    "international_graduate_share_pct",

    "full_time",
    "part_time",
    "casual",
    "employment_status_unknown",

    "manager",
    "staff_nurse",
    "position_not_stated",
    "other_position",

    "administration",
    "direct_care",
    "direct_care_share_pct",
    "education",
    "research",
    "responsibility_not_stated",

    "rural",
    "urban",
    "geography_unknown",
    "rural_share_pct",
]

remaining = [
    col for col in df.columns
    if col not in preferred
]

df = df[preferred + remaining]


# ---------------------------------------------------------
# 5. Save
# ---------------------------------------------------------

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(
    OUTPUT,
    index=False
)


# ---------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------

print("=" * 70)
print("CIHI NURSING DATA TRANSFORMATION")
print("=" * 70)

print("\nInput:")
print(INPUT)

print("\nOutput:")
print(OUTPUT)

print("\nShape:")
print(df.shape)

print("\nYears:")
print(f"{df['year'].min()}–{df['year'].max()}")

print("\nProfessions:")
print(df["profession"].value_counts().to_string())

print("\nJurisdictions:")
print(df["jurisdiction"].nunique())

print("\nWorkplaces:")
print(df["workplace"].value_counts().to_string())

print("\nDerived metrics:")
derived = [
    "female_share_pct",
    "international_graduate_share_pct",
    "age_65_plus",
    "age_65_plus_share_pct",
    "rural_share_pct",
    "direct_care_share_pct",
    "workforce_yoy_change",
    "workforce_yoy_growth_pct",
]

print("\n".join(f"  - {x}" for x in derived))

print("\n" + "=" * 70)
print("CIHI NURSING DATA TRANSFORMATION COMPLETE")
print("=" * 70)