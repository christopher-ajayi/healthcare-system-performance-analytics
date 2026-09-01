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

OUTPUT_FILE = OUTPUT_DIR / "cihi_hospital_beds_clean.csv"


# ============================================================
# VALIDATE INPUT
# ============================================================

if not RAW_FILE.exists():
    raise FileNotFoundError(
        f"File not found:\n{RAW_FILE}"
    )

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD WORKBOOK
# ============================================================

excel = pd.ExcelFile(RAW_FILE)

print("Workbook loaded successfully.")
print(f"Sheets found: {len(excel.sheet_names)}")


# ============================================================
# READ BSIO SUMMARY
# TABLE D.1.1
# ============================================================

df = pd.read_excel(
    RAW_FILE,
    sheet_name="BSIO summary",
    header=None
)

# Table D.1.1:
# A4:M18
#
# Row 4 = header
# Rows 5–18 = fiscal-year observations

total_beds = df.iloc[3:18].copy()

total_beds.columns = total_beds.iloc[0]

total_beds = total_beds.iloc[1:].copy()

total_beds = total_beds[
    total_beds.iloc[:, 0]
    .astype(str)
    .str.match(r"^\d{4}–\d{4}$")
].copy()


# ============================================================
# STANDARDIZE COLUMN NAMES
# ============================================================

province_map = {
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
    "Canada (excluding Nun.)": "Canada",
}

total_beds = total_beds.rename(columns=province_map)

total_beds = total_beds.rename(
    columns={total_beds.columns[0]: "fiscal_year"}
)


# ============================================================
# WIDE → LONG
# ============================================================

total_beds = total_beds.melt(
    id_vars="fiscal_year",
    var_name="province",
    value_name="total_beds"
)


# ============================================================
# CLEAN VALUES
# ============================================================

total_beds["total_beds"] = pd.to_numeric(
    total_beds["total_beds"],
    errors="coerce"
)


# ============================================================
# CREATE YEAR
# ============================================================

total_beds["year"] = (
    total_beds["fiscal_year"]
    .str.extract(r"^(\d{4})")
    .astype("Int64")
)


# ============================================================
# ORDER COLUMNS
# ============================================================

total_beds = total_beds[
    [
        "year",
        "fiscal_year",
        "province",
        "total_beds",
    ]
]


# ============================================================
# SORT
# ============================================================

total_beds = total_beds.sort_values(
    ["province", "year"]
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

total_beds.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("CIHI HOSPITAL BEDS CLEANING COMPLETE")
print("=" * 60)

print(f"\nOutput file:")
print(OUTPUT_FILE)

print(f"\nRows: {len(total_beds):,}")

print(
    f"Year range: "
    f"{total_beds['year'].min()}–"
    f"{total_beds['year'].max()}"
)

print(
    f"Provinces/territories: "
    f"{total_beds['province'].nunique()}"
)

print("\nMissing values:")
print(total_beds.isna().sum())

print("\nProvince coverage:")
print(
    total_beds.groupby("province")["year"]
    .agg(["min", "max", "count"])
)

print("\nFirst 10 rows:")
print(total_beds.head(10).to_string(index=False))

print("\n" + "=" * 60)