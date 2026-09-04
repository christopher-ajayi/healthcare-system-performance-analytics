from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "capacity"
    / "cihi_hospital_beds_current_transformed.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "capacity"
    / "cihi_hospital_beds_current_validation.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"File not found:\n{INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)


print("=" * 70)
print("CIHI CURRENT HOSPITAL BEDS VALIDATION")
print("=" * 70)

print(f"\nInput:")
print(INPUT_FILE)

print(f"\nRows: {len(df):,}")


# ============================================================
# COLUMNS
# ============================================================

print("\n" + "-" * 70)
print("COLUMNS")
print("-" * 70)

print(df.columns.tolist())


# ============================================================
# MISSING VALUES
# ============================================================

print("\n" + "-" * 70)
print("MISSING VALUES")
print("-" * 70)

print(df.isna().sum())


# ============================================================
# DUPLICATES
# ============================================================

print("\n" + "-" * 70)
print("DUPLICATES")
print("-" * 70)

duplicate_count = df.duplicated().sum()

print(
    f"Duplicate rows: {duplicate_count:,}"
)


# ============================================================
# NEGATIVE NUMERIC VALUES
# ============================================================

print("\n" + "-" * 70)
print("NEGATIVE VALUES")
print("-" * 70)

numeric_columns = df.select_dtypes(
    include="number"
).columns

negative_counts = (
    df[numeric_columns]
    .lt(0)
    .sum()
)

print(
    negative_counts[
        negative_counts > 0
    ]
)


# ============================================================
# JURISDICTION COVERAGE
# ============================================================

print("\n" + "-" * 70)
print("JURISDICTION COVERAGE")
print("-" * 70)

print(
    df["province"]
    .value_counts()
    .sort_index()
)

print(
    f"\nProvinces/territories: "
    f"{df['province'].nunique()}"
)


# ============================================================
# YEAR COVERAGE
# ============================================================

print("\n" + "-" * 70)
print("YEAR COVERAGE")
print("-" * 70)

print(
    f"Year range: "
    f"{df['year'].min()}–{df['year'].max()}"
)

print(
    f"Years: "
    f"{sorted(df['year'].dropna().unique())}"
)


# ============================================================
# ZERO VALUES
# ============================================================

print("\n" + "-" * 70)
print("ZERO VALUES")
print("-" * 70)

zero_counts = (
    df[numeric_columns]
    .eq(0)
    .sum()
)

print(
    zero_counts[
        zero_counts > 0
    ]
)


# ============================================================
# VALIDATION RESULT
# ============================================================

negative_count = (
    negative_counts.sum()
)

print("\n" + "=" * 70)
print("VALIDATION RESULT")
print("=" * 70)

if duplicate_count > 0:

    validation_status = (
        "FAILED — duplicate rows detected."
    )

elif negative_count > 0:

    validation_status = (
        "FAILED — negative numeric values detected."
    )

else:

    validation_status = (
        "PASSED WITH MISSING VALUES REQUIRING REVIEW"
    )

print(validation_status)


# ============================================================
# SAVE VALIDATION OUTPUT
# ============================================================

validation_output = pd.DataFrame(
    {
        "validation": [
            "rows",
            "year_min",
            "year_max",
            "provinces_territories",
            "duplicate_rows",
            "negative_values",
            "validation_status",
        ],
        "result": [
            len(df),
            df["year"].min(),
            df["year"].max(),
            df["province"].nunique(),
            duplicate_count,
            negative_count,
            validation_status,
        ],
    }
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

validation_output.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nOutput:")
print(OUTPUT_FILE)

print("\n" + "=" * 70)