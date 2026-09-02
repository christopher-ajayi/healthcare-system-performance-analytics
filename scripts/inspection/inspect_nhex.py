from pathlib import Path
from zipfile import ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "spending"
    / "cihi_nhex_2025_raw.zip"
)


if not RAW_FILE.exists():
    raise FileNotFoundError(
        f"NHEX raw file not found: {RAW_FILE}"
    )


print("=" * 70)
print("CIHI NHEX 2025 — STRUCTURAL INSPECTION")
print("=" * 70)

print(f"\nRaw file:")
print(RAW_FILE)

print(
    f"\nFile size: "
    f"{RAW_FILE.stat().st_size / (1024 ** 2):.2f} MB"
)


# ---------------------------------------------------------
# Inspect ZIP
# ---------------------------------------------------------

with ZipFile(RAW_FILE, "r") as zip_file:

    files = zip_file.namelist()

    print("\nFiles contained in ZIP:")
    print("-" * 70)

    for file_name in files:
        print(file_name)


# ---------------------------------------------------------
# File types
# ---------------------------------------------------------

print("\nFile counts by extension:")
print("-" * 70)

extensions = {}

for file_name in files:

    suffix = Path(file_name).suffix.lower()

    extensions[suffix] = (
        extensions.get(suffix, 0) + 1
    )

for extension, count in sorted(extensions.items()):

    print(f"{extension or '[no extension]'}: {count}")


print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)