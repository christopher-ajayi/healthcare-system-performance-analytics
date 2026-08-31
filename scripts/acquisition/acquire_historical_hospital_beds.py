from pathlib import Path
from datetime import datetime, timezone
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "capacity"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "cihi_hospital_beds_2023_2024.xlsx": (
        "https://www.cihi.ca/sites/default/files/document/"
        "beds-staffed-and-in-operation-2023-2024-data-tables-en.xlsx"
    ),
}


def download_file(filename, url):
    output_path = OUTPUT_DIR / filename

    print(f"\nDownloading: {filename}")
    print(f"Source: {url}")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    output_path.write_bytes(response.content)

    print(f"PASS — {output_path}")
    print(f"Size: {output_path.stat().st_size / (1024 * 1024):.2f} MB")


print("=" * 70)
print("CIHI HISTORICAL HOSPITAL BEDS — ACQUISITION")
print("=" * 70)

for filename, url in SOURCES.items():
    try:
        download_file(filename, url)
    except Exception as exc:
        print(f"FAIL — {filename}")
        print(f"Reason: {exc}")

print("\n" + "=" * 70)
print("ACQUISITION COMPLETE")
print("=" * 70)
print(
    f"Acquisition timestamp (UTC): "
    f"{datetime.now(timezone.utc).isoformat()}"
)