from pathlib import Path
from zipfile import ZipFile

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "demographics"
    / "statcan_17100005_raw.zip"
)


# ---------------------------------------------------------
# Validate raw file
# ---------------------------------------------------------

if not RAW_FILE.exists():
    raise FileNotFoundError(
        f"Raw population file not found: {RAW_FILE}"
    )

print("=" * 70)
print("STATISTICS CANADA POPULATION DATA — STRUCTURAL INSPECTION")
print("=" * 70)

print(f"\nRaw file:")
print(RAW_FILE)

print(f"\nFile size:")
print(f"{RAW_FILE.stat().st_size / (1024 ** 2):.2f} MB")


# ---------------------------------------------------------
# Inspect ZIP contents
# ---------------------------------------------------------

with ZipFile(RAW_FILE, "r") as zip_file:

    files = zip_file.namelist()

    print("\nFiles contained in ZIP:")
    print("-" * 70)

    for file_name in files:
        print(file_name)


# ---------------------------------------------------------
# Identify CSV files
# ---------------------------------------------------------

csv_files = [
    file_name
    for file_name in files
    if file_name.lower().endswith(".csv")
]

if not csv_files:
    raise ValueError("No CSV files found in the Statistics Canada ZIP.")

print("\nCSV files:")
print("-" * 70)

for file_name in csv_files:
    print(file_name)


# ---------------------------------------------------------
# Inspect first CSV
# ---------------------------------------------------------

data_file = csv_files[0]

print("\nInspecting:")
print(data_file)

with ZipFile(RAW_FILE, "r") as zip_file:

    with zip_file.open(data_file) as file:

        df = pd.read_csv(
            file,
            nrows=1000
        )


# ---------------------------------------------------------
# Basic structure
# ---------------------------------------------------------

print("\nDataset shape for inspection sample:")
print(df.shape)

print("\nColumns:")
print("-" * 70)

for column in df.columns:
    print(column)


# ---------------------------------------------------------
# Data types
# ---------------------------------------------------------

print("\nData types:")
print("-" * 70)

print(df.dtypes)


# ---------------------------------------------------------
# Sample records
# ---------------------------------------------------------

print("\nFirst 5 records:")
print("-" * 70)

print(df.head())


# ---------------------------------------------------------
# Missing values
# ---------------------------------------------------------

print("\nMissing values:")
print("-" * 70)

print(df.isna().sum())


print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)