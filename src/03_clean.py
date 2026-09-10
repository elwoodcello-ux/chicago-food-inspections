"""Clean the raw inspections CSV into two tidy tables."""
import pandas as pd
from pathlib import Path

RAW = Path("data/raw/food_inspections.csv")
OUT = Path("data/processed")


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW, dtype=str, low_memory=False)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def clean_inspections(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["inspection_date"] = pd.to_datetime(df["inspection_date"], errors="coerce")
        bad_dates = df["inspection_date"].isna().sum()
        print(f"Unparseable dates dropped: {bad_dates:,}")
        df = df.dropna(subset=["inspection_date"])
        df = df[df["inspection_date"].dt.year >= 2020]
        df["risk_level"] = df["risk"].str.extract(r"(\d)").astype("Int64")
        df["license"] = pd.to_numeric(df["license"], errors="coerce")
        df.loc[df["license"] == 0, "license"] = pd.NA
        print(f"Null licenses after cleaning: {df['license'].isna().sum():,}")
        print(df["risk_level"].value_counts(dropna=False))
        print(f"After 2020 filter: {len(df):,}")
        df["city"] = df["city"].str.upper().str.strip()
        df.loc[df["city"].str.contains("CHICAGO", na=False), "city"] = "CHICAGO"
        print(df["city"].value_counts(dropna=False).head(10))
        df["dba_name"] = df["dba_name"].str.upper().str.replace(r"\s+", " ", regex=True).str.strip()
        keep = ["inspection_id", "dba_name", "license", "facility_type", "risk_level",
        "risk", "city", "zip", "inspection_date", "inspection_type", "results",
        "latitude", "longitude", "violations"]
        df = df[keep]
        return df

def explode_violations(df: pd.DataFrame) -> pd.DataFrame:
    v = df[["inspection_id", "violations"]].dropna(subset=["violations"])
    v = v.assign(violation=v["violations"].str.split(r"\s*\|\s*", regex=True))
    v = v.explode("violation")
    v["violation_code"] = v["violation"].str.extract(r"^\s*(\d+)\.").astype("Int64")
    v["violation_desc"] = v["violation"].str.extract(r"^\s*\d+\.\s*(.*?)\s*-\s*Comments:")
    v["comments"] = v["violation"].str.extract(r"-\s*Comments:\s*(.*)$")
    no_comment = v["violation_desc"].isna()
    v.loc[no_comment, "violation_desc"] = v.loc[no_comment, "violation"].str.extract(r"^\s*\d+\.\s*(.*)$")[0]
    print(f"Missing desc: {v['violation_desc'].isna().sum():,}")
    print(f"Missing comments: {v['comments'].isna().sum():,}")
    print(v[["violation_code", "violation_desc"]].dropna().sample(5).to_string())
    print(f"Failed code extraction: {v['violation_code'].isna().sum():,}")
    print(v["violation_code"].value_counts().head(10))
    print(f"Violation rows after split: {len(v):,}")
    v = v[["inspection_id", "violation_code", "violation_desc", "comments"]]
    return v

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    print(f"Raw rows: {len(raw):,}")
    inspections = clean_inspections(raw)
    print(f"Clean rows: {len(inspections):,}")
    violations = explode_violations(inspections)
    print(f"Violation rows: {len(violations):,}")
    violations.to_parquet(OUT / "violations.parquet", index=False)
    inspections = inspections.drop(columns=["violations"])
    inspections.to_parquet(OUT / "inspections.parquet", index=False)


if __name__ == "__main__":
    main()
