from pathlib import Path
import pandas as pd


# -------------------------------------------------------------------
# FILE CONFIGURATION
# -------------------------------------------------------------------

INPUT_FILE = Path(
    "data/raw/workforce/cihi_health_workforce_quick_stats.xlsx"
)

OUTPUT_FILE = Path(
    "data/processed/workforce/cihi_nursing_clean.csv"
)

SHEET_NAME = "NursProfileData"


# -------------------------------------------------------------------
# COLUMN MAPPING
# -------------------------------------------------------------------

COLUMN_RENAME = {
    "ID": "record_id",
    "provider - THIS TAB IS FOR NURSING ONLY": "profession",
    "registration_location_code": "jurisdiction",
    "workplace": "workplace",
    "data_year": "year",
    "female": "female",
    "male ": "male",
    "unk_sex": "sex_unknown",
    "25-29": "age_25_29",
    "30-34": "age_30_34",
    "35-39": "age_35_39",
    "40-44": "age_40_44",
    "45-49": "age_45_49",
    "50-54": "age_50_54",
    "55-59": "age_55_59",
    "60-64": "age_60_64",
    "65-69": "age_65_69",
    "70+": "age_70_plus",
    "<25": "age_under_25",
    "age_unk": "age_unknown",
    "Canadian grads": "canadian_graduates",
    "Interntl grads": "international_graduates",
    "Grad location UNK": "graduation_location_unknown",
    "Full-time": "full_time",
    "Part-time": "part_time",
    "Casual": "casual",
    "empl. status UNK": "employment_status_unknown",
    "manager": "manager",
    "staff nurse": "staff_nurse",
    "position not stated": "position_not_stated",
    "other position": "other_position",
    "Admin": "administration",
    "direct care": "direct_care",
    "education": "education",
    "research": "research",
    "not stated responsibility": "responsibility_not_stated",
    "rural": "rural",
    "urban": "urban",
    "geo_unk": "geography_unknown",
    "Total workforce": "total_workforce",
    "ID2": "record_id_2",
}


# -------------------------------------------------------------------
# NUMERIC COLUMNS
# -------------------------------------------------------------------

NUMERIC_COLUMNS = [
    "year",
    "female",
    "male",
    "sex_unknown",
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
    "age_under_25",
    "age_unknown",
    "canadian_graduates",
    "international_graduates",
    "graduation_location_unknown",
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
    "education",
    "research",
    "responsibility_not_stated",
    "rural",
    "urban",
    "geography_unknown",
    "total_workforce",
]


# -------------------------------------------------------------------
# MAIN CLEANING FUNCTION
# -------------------------------------------------------------------

def main():

    print("=" * 70)
    print("CIHI NURSING DATA CLEANING")
    print("=" * 70)

    # ---------------------------------------------------------------
    # Load
    # ---------------------------------------------------------------

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name=SHEET_NAME,
        header=1,
    )

    print("\nRaw shape:", df.shape)

    # ---------------------------------------------------------------
    # Rename columns
    # ---------------------------------------------------------------

    df = df.rename(columns=COLUMN_RENAME)

    # ---------------------------------------------------------------
    # Remove source identifiers
    # ---------------------------------------------------------------

    df = df.drop(
        columns=[
            "record_id",
            "record_id_2",
        ],
        errors="ignore",
    )

    # ---------------------------------------------------------------
    # Standardize text fields
    # ---------------------------------------------------------------

    text_columns = [
        "profession",
        "jurisdiction",
        "workplace",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # ---------------------------------------------------------------
    # Standardize profession names
    # ---------------------------------------------------------------

    profession_mapping = {
        "Licensed practical nurses":
            "Licensed practical nurses",
        "Nurse practitioners":
            "Nurse practitioners",
        "Registered nurses":
            "Registered nurses",
        "Registered psychiatric nurses":
            "Registered psychiatric nurses",
    }

    df["profession"] = df["profession"].replace(
        profession_mapping
    )

    # ---------------------------------------------------------------
    # Convert numeric columns
    # ---------------------------------------------------------------

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # ---------------------------------------------------------------
    # Year validation
    # ---------------------------------------------------------------

    invalid_years = df.loc[
        ~df["year"].between(2015, 2024),
        "year",
    ].dropna().unique()

    if len(invalid_years) > 0:
        raise ValueError(
            f"Unexpected years found: {invalid_years}"
        )

    # ---------------------------------------------------------------
    # Duplicate validation
    # ---------------------------------------------------------------

    key_columns = [
        "year",
        "profession",
        "jurisdiction",
        "workplace",
    ]

    duplicate_count = df.duplicated(
        subset=key_columns
    ).sum()

    print("\nDuplicate records:", duplicate_count)

    if duplicate_count > 0:
        raise ValueError(
            "Duplicate records detected."
        )

    # ---------------------------------------------------------------
    # Sort
    # ---------------------------------------------------------------

    df = df.sort_values(
        [
            "year",
            "jurisdiction",
            "profession",
            "workplace",
        ]
    ).reset_index(drop=True)

    # ---------------------------------------------------------------
    # Final column ordering
    # ---------------------------------------------------------------

    first_columns = [
        "year",
        "jurisdiction",
        "profession",
        "workplace",
        "total_workforce",
    ]

    remaining_columns = [
        column
        for column in df.columns
        if column not in first_columns
    ]

    df = df[
        first_columns + remaining_columns
    ]

    # ---------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------

    print("\n--- CLEANED DATA ---")
    print("Shape:", df.shape)

    print("\nYears:")
    print(
        f"{int(df['year'].min())}"
        f"–"
        f"{int(df['year'].max())}"
    )

    print("\nProfessions:")
    print(
        df["profession"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nJurisdictions:")
    print(
        df["jurisdiction"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nWorkplaces:")
    print(
        df["workplace"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nMissing values:")
    print(
        df.isna()
        .sum()
        .to_string()
    )

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\n" + "=" * 70)
    print("CIHI NURSING DATA CLEANING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()