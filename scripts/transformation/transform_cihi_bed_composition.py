from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "capacity"
    / "cihi_hospital_beds_2009_2023_series_d.xlsx"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "capacity"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "cihi_hospital_bed_composition_transformed.csv"
)


# ============================================================
# JURISDICTIONS
# ============================================================

SHEETS = {
    "N.L.": "Newfoundland and Labrador",
    "P.E.I.": "Prince Edward Island",
    "N.S.": "Nova Scotia",
    "N.B.": "New Brunswick",
    "Que.": "Quebec",
    "Ont.": "Ontario",
    "Man.": "Manitoba",
    "Sask.": "Saskatchewan",
    "Alta.": "Alberta",
    "B.C.": "British Columbia",
    "Y.T.": "Yukon",
    "N.W.T.": "Northwest Territories",
}


# ============================================================
# EXPECTED COLUMNS
# ============================================================

COLUMNS = [
    "fiscal_year",
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
# VALIDATE INPUT
# ============================================================

if not RAW_FILE.exists():
    raise FileNotFoundError(
        f"File not found:\n{RAW_FILE}"
    )

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# EXTRACT D.x.1 TABLES
# ============================================================

all_data = []


for sheet_name, province in SHEETS.items():

    raw = pd.read_excel(
        RAW_FILE,
        sheet_name=sheet_name,
        header=None
    )

    # --------------------------------------------------------
    # D.x.1 begins at Excel row 4.
    #
    # Excel row 4 = pandas index 3
    # Excel row 5 = pandas index 4
    #
    # We take the actual header from row 4 and the annual
    # observations immediately below it.
    # --------------------------------------------------------

    header = raw.iloc[3].tolist()

    data = raw.iloc[4:18].copy()

    # Some sheets contain one additional trailing column.
    # Keep only the first 9 analytical columns.
    data = data.iloc[:, :9].copy()

    data.columns = COLUMNS

    # --------------------------------------------------------
    # Remove rows that are not fiscal-year observations.
    # --------------------------------------------------------

    data["fiscal_year"] = (
        data["fiscal_year"]
        .astype(str)
        .str.strip()
    )

    data = data[
        data["fiscal_year"]
        .str.match(
            r"^\d{4}–\d{4}$",
            na=False
        )
    ].copy()

    # --------------------------------------------------------
    # Add province
    # --------------------------------------------------------

    data["province"] = province

    all_data.append(data)


# ============================================================
# COMBINE
# ============================================================

composition = pd.concat(
    all_data,
    ignore_index=True
)


# ============================================================
# YEAR
# ============================================================

composition["year"] = (
    composition["fiscal_year"]
    .str.extract(r"^(\d{4})")[0]
    .astype(int)
)


# ============================================================
# NUMERIC CONVERSION
# ============================================================

numeric_columns = [
    "icu_beds",
    "obstetrics_beds",
    "pediatrics_beds",
    "mental_health_addictions_beds",
    "rehabilitation_beds",
    "long_term_care_beds",
    "other_acute_care_beds",
    "rated_bed_capacity",
]

for column in numeric_columns:

    composition[column] = pd.to_numeric(
        composition[column],
        errors="coerce"
    )


# ============================================================
# COLUMN ORDER
# ============================================================

composition = composition[
    [
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
]


# ============================================================
# SORT
# ============================================================

composition = composition.sort_values(
    ["province", "year"]
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

composition.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("CIHI HOSPITAL BED COMPOSITION TRANSFORMATION COMPLETE")
print("=" * 70)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(f"\nRows: {len(composition):,}")

print(
    f"Year range: "
    f"{composition['year'].min()}–"
    f"{composition['year'].max()}"
)

print(
    f"Jurisdictions: "
    f"{composition['province'].nunique()}"
)

print("\nRows by province:")

print(
    composition
    .groupby("province")
    .size()
    .to_string()
)

print("\nMissing values:")

print(
    composition.isna().sum()
)

print("\nFirst 10 rows:")

print(
    composition
    .head(10)
    .to_string(index=False)
)

print("\n" + "=" * 70)