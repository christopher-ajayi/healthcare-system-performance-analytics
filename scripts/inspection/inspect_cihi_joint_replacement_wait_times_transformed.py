import pandas as pd

FILE = r"D:\DaytaScape_Workspace\healthcare-system-performance-analytics\data\processed\outcomes\cihi_joint_replacement_wait_times_transformed.csv"

print("=" * 78)
print("CIHI JOINT REPLACEMENT WAIT TIMES — TRANSFORMATION INSPECTION")
print("=" * 78)

df = pd.read_csv(FILE)

print("\nOverall:")
print(f"Records: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\nIndicator-result availability:")
print(df["indicator_result_available"].value_counts())

print("\nAvailability by metric:")
print(
    pd.crosstab(
        df["metric"],
        df["indicator_result_available"]
    )
)

print("\nRaw metric value by metric:")
print(
    df.groupby("metric")["metric_value_raw"]
    .value_counts()
    .head(30)
)

print("\nNumeric indicator results by metric:")
print(
    df.groupby("metric")["indicator_result"]
    .apply(lambda x: x.notna().sum())
)

print("\nProcedure-volume availability:")
print(
    df["procedure_volume"].notna().value_counts()
)

print("\nBenchmark availability:")
print(
    df["benchmark_pct"].notna().value_counts()
)

print("\nRows where raw value is numeric but indicator_result is missing:")

raw_numeric = pd.to_numeric(
    df["metric_value_raw"],
    errors="coerce"
).notna()

transformed_missing = df["indicator_result"].isna()

problem_rows = df[
    raw_numeric & transformed_missing
]

print(f"Count: {len(problem_rows)}")

if len(problem_rows) > 0:
    print(
        problem_rows[
            [
                "place_or_organization",
                "province",
                "region",
                "reporting_level",
                "metric",
                "metric_value_raw",
                "indicator_result",
                "indicator_result_available"
            ]
        ].head(20).to_string(index=False)
    )

print("\n" + "=" * 78)
print("INSPECTION COMPLETE")
print("=" * 78)