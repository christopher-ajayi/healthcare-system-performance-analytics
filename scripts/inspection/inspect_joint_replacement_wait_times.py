from pathlib import Path
import pandas as pd


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(
    r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics"
)

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "outcomes"
    / "cihi_indicator_library.xlsx"
)

SHEET_NAME = "Sheet1"

TARGET_INDICATOR = "Joint Replacement Wait Times"


# ============================================================================
# HEADER
# ============================================================================

print("=" * 78)
print("CIHI JOINT REPLACEMENT WAIT TIMES — SUBSET INSPECTION")
print("=" * 78)

print(f"\nInput file:\n{INPUT_FILE}")
print(f"Sheet: {SHEET_NAME}")
print(f"Target indicator: {TARGET_INDICATOR}")


# ============================================================================
# LOAD
# ============================================================================

df = pd.read_excel(
    INPUT_FILE,
    sheet_name=SHEET_NAME,
    dtype=str
)

print("\n" + "-" * 78)
print("1. RAW DATA")
print("-" * 78)

print(f"Raw shape: {df.shape}")


# ============================================================================
# FILTER TARGET INDICATOR
# ============================================================================

subset = df[
    df["Indicator"].astype(str).str.strip()
    == TARGET_INDICATOR
].copy()

print("\n" + "-" * 78)
print("2. TARGET INDICATOR")
print("-" * 78)

print(f"Records: {len(subset):,}")

if subset.empty:
    raise ValueError(
        f"No records found for indicator: {TARGET_INDICATOR}"
    )


# ============================================================================
# BASIC STRUCTURE
# ============================================================================

print("\n" + "-" * 78)
print("3. REPORTING LEVEL")
print("-" * 78)

print(subset["Reporting level"].value_counts(dropna=False))


print("\n" + "-" * 78)
print("4. PROVINCE / TERRITORY")
print("-" * 78)

print(subset["Province/territory"].value_counts(dropna=False))


print("\n" + "-" * 78)
print("5. REGIONS")
print("-" * 78)

print(
    f"Unique regions: "
    f"{subset['Region'].nunique(dropna=False)}"
)


print("\n" + "-" * 78)
print("6. TIME SCALE")
print("-" * 78)

print(subset["Time scale"].value_counts(dropna=False))


print("\n" + "-" * 78)
print("7. TIME FRAME")
print("-" * 78)

print(subset["Time frame"].value_counts(dropna=False).sort_index())


# ============================================================================
# SEGMENTS
# ============================================================================

print("\n" + "-" * 78)
print("8. INDICATOR SEGMENT")
print("-" * 78)

print(subset["Indicator segment"].value_counts(dropna=False))


print("\n" + "-" * 78)
print("9. SEGMENT VALUE")
print("-" * 78)

print(subset["Segment value"].value_counts(dropna=False))


# ============================================================================
# BREAKDOWNS
# ============================================================================

for level in [
    "Level 1 breakdown",
    "Level 1 breakdown value",
    "Level 2 breakdown",
    "Level 2 breakdown value",
    "Level 3 breakdown",
    "Level 3 breakdown value",
]:
    print("\n" + "-" * 78)
    print(level.upper())
    print("-" * 78)
    print(subset[level].value_counts(dropna=False).head(50))


# ============================================================================
# METRICS
# ============================================================================

print("\n" + "-" * 78)
print("10. METRICS")
print("-" * 78)

print(subset["Metric"].value_counts(dropna=False))


print("\n" + "-" * 78)
print("11. MAIN METRIC")
print("-" * 78)

print(subset["Main metric"].value_counts(dropna=False))


# ============================================================================
# UNITS
# ============================================================================

print("\n" + "-" * 78)
print("12. UNITS OF MEASURE")
print("-" * 78)

print(subset["Unit of measure"].value_counts(dropna=False))


# ============================================================================
# SUPPRESSION / VALUES
# ============================================================================

print("\n" + "-" * 78)
print("13. METRIC VALUE")
print("-" * 78)

print(f"Non-null values: {subset['Metric value'].notna().sum():,}")
print(
    f"Suppressed values: "
    f"{(subset['Metric value'].astype(str).str.strip() == 'Suppressed').sum():,}"
)

print("\nSample metric values:")
print(
    subset["Metric value"]
    .value_counts(dropna=False)
    .head(30)
)


# ============================================================================
# CONFIDENCE INTERVALS
# ============================================================================

print("\n" + "-" * 78)
print("14. CONFIDENCE INTERVALS")
print("-" * 78)

print(
    f"Lower limit available: "
    f"{subset['Confidence interval lower limit'].notna().sum():,}"
)

print(
    f"Upper limit available: "
    f"{subset['Confidence interval upper limit'].notna().sum():,}"
)


# ============================================================================
# UNIQUE STRUCTURAL COMBINATIONS
# ============================================================================

print("\n" + "-" * 78)
print("15. STRUCTURAL UNIQUENESS")
print("-" * 78)

key_columns = [
    "Place or organization",
    "Province/territory",
    "Region",
    "Reporting level",
    "Indicator",
    "Indicator segment",
    "Segment value",
    "Time scale",
    "Time frame",
    "Level 1 breakdown",
    "Level 1 breakdown value",
    "Level 2 breakdown",
    "Level 2 breakdown value",
    "Level 3 breakdown",
    "Level 3 breakdown value",
    "Metric",
]

duplicates = subset.duplicated(
    subset=key_columns,
    keep=False
)

print(f"Duplicate structural records: {duplicates.sum():,}")


# ============================================================================
# SAMPLE
# ============================================================================

print("\n" + "-" * 78)
print("16. SAMPLE RECORDS")
print("-" * 78)

print(
    subset[
        [
            "Place or organization",
            "Province/territory",
            "Region",
            "Reporting level",
            "Indicator",
            "Indicator segment",
            "Segment value",
            "Time frame",
            "Level 1 breakdown",
            "Level 1 breakdown value",
            "Metric",
            "Main metric",
            "Metric value",
            "Unit of measure",
        ]
    ].head(20).to_string(index=False)
)


# ============================================================================
# COMPLETE
# ============================================================================

print("\n" + "=" * 78)
print("JOINT REPLACEMENT WAIT TIMES SUBSET INSPECTION COMPLETE")
print("=" * 78)