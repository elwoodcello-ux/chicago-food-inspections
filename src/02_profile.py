"""Quick profile of the raw inspections CSV. Throwaway analysis, not a deliverable."""
import pandas as pd

df = pd.read_csv("data/raw/food_inspections.csv", dtype=str, low_memory=False)

print("Shape:", df.shape)
print("\nColumns:", list(df.columns))
print("\nNull counts:\n", df.isna().sum())
print("\nDuplicate Inspection IDs:", df["Inspection ID"].duplicated().sum())

for col in ["City", "Facility Type", "Risk", "Results", "State"]:
    print(f"\n--- {col} ({df[col].nunique()} distinct) ---")
    print(df[col].value_counts(dropna=False).head(20))

print("\nSample Violations value:\n", df["Violations"].dropna().iloc[0][:600])
