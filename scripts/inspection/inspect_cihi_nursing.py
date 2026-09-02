from pathlib import Path
import pandas as pd


INPUT_FILE = Path(
    "data/raw/workforce/cihi_health_workforce_quick_stats.xlsx"
)

SHEET_NAME = "NursProfileData"


def main():
    print("=" * 70)
    print("CIHI NURSING DATA INSPECTION")
    print("=" * 70)

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name=SHEET_NAME,
        header=1
    )

    print("\n--- SHAPE ---")
    print(df.shape)

    print("\n--- COLUMNS ---")
    for i, col in enumerate(df.columns, start=1):
        print(f"{i:>3}. {col}")

    print("\n--- YEARS ---")
    print(sorted(df["data_year"].dropna().unique()))

    print("\n--- PROFESSIONS ---")
    print(
        df[
            "provider - THIS TAB IS FOR NURSING ONLY"
        ].dropna().unique()
    )

    print("\n--- JURISDICTIONS ---")
    print(
        sorted(
            df["registration_location_code"]
            .dropna()
            .unique()
        )
    )

    print("\n--- WORKPLACES ---")
    print(
        sorted(
            df["workplace"]
            .dropna()
            .unique()
        )
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()