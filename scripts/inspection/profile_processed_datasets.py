from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# DATASETS
# ============================================================

DATASETS = [
    ("access", "cihi_wait_times_transformed.csv"),
    
    ("capacity", "cihi_hospital_beds_transformed.csv"),
    ("capacity", "cihi_hospital_beds_current_transformed.csv"),
    ("capacity", "cihi_hospital_bed_composition_transformed.csv"),
    
    ("demand", "cihi_hospitalizations_transformed.csv"),
    ("demand", "cihi_standardized_rates_transformed.csv"),
    
    ("demographics", "provincial_population_annual_transformed.csv"),
    
    ("outcomes", "30_day_hospital_readmission_transformed.csv"),
    ("outcomes", "avoidable_hospitalizations_acscs_transformed.csv"),
    ("outcomes", "cihi_joint_replacement_wait_times_transformed.csv"),
    ("outcomes", "hip_fracture_surgery_within_48_hours_transformed.csv"),
    
    ("spending", "nhex_health_expenditure_transformed.csv"),
    
    ("workforce", "cihi_nursing_transformed.csv"),
    ("workforce", "cihi_physicians_transformed.csv"),
]


# ============================================================
# HELPERS
# ============================================================

def inspect_dataset(domain: str, filename: str):

    path = PROCESSED_DIR / domain / filename

    print("\n" + "=" * 90)
    print(f"DATASET: {domain}/{filename}")
    print("=" * 90)

    if not path.exists():
        print(f"ERROR: File not found: {path}")
        return

    df = pd.read_csv(path)

    print(f"\nPath:")
    print(path)

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns and pandas dtypes:")
    for column in df.columns:
        print(
            f"  {column:<40} "
            f"{str(df[column].dtype):<15} "
            f"missing={df[column].isna().sum():,}"
        )

    print("\nYear-related columns:")

    year_columns = [
        column
        for column in df.columns
        if "year" in column.lower()
    ]

    if year_columns:

        for column in year_columns:

            print(f"\n  {column}")

            print(
                df[column]
                .dropna()
                .astype(str)
                .drop_duplicates()
                .head(20)
                .tolist()
            )

    else:
        print("  None")

    print("\nProvince/jurisdiction columns:")

    jurisdiction_columns = [
        column
        for column in df.columns
        if any(
            keyword in column.lower()
            for keyword in [
                "province",
                "territory",
                "jurisdiction",
                "region",
            ]
        )
    ]

    if jurisdiction_columns:

        for column in jurisdiction_columns:

            values = (
                df[column]
                .dropna()
                .astype(str)
                .str.strip()
                .drop_duplicates()
                .sort_values()
                .tolist()
            )

            print(f"\n  {column}: {len(values)} unique values")

            print(values)

    else:
        print("  None")

    print("\nDuplicate rows:")

    print(
        f"  {df.duplicated().sum():,}"
    )

    print("\nSample:")
    print(
        df.head(5).to_string(index=False)
    )


# ============================================================
# RUN
# ============================================================

print("\n" + "#" * 90)
print("PROCESSED DATASET PROFILE")
print("#" * 90)

print(f"\nProject root:")
print(PROJECT_ROOT)

print(f"\nProcessed directory:")
print(PROCESSED_DIR)

print(f"\nDatasets expected: {len(DATASETS)}")

for domain, filename in DATASETS:
    inspect_dataset(domain, filename)

print("\n" + "#" * 90)
print("PROFILE COMPLETE")
print("#" * 90)