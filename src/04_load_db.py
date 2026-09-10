"""Load the cleaned tables into a SQLite database."""
import sqlite3
from pathlib import Path
import pandas as pd

PROC = Path("data/processed")
DB = PROC / "inspections.db"


def main():
    inspections = pd.read_parquet(PROC / "inspections.parquet")
    violations = pd.read_parquet(PROC / "violations.parquet")

    # SQLite has no date type, so store ISO strings that sort correctly.
    inspections["inspection_date"] = inspections["inspection_date"].dt.strftime("%Y-%m-%d")

    con = sqlite3.connect(DB)
    inspections.to_sql("inspections", con, if_exists="replace", index=False)
    violations.to_sql("violations", con, if_exists="replace", index=False)

    cur = con.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_insp_license ON inspections(license)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_insp_date ON inspections(inspection_date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_viol_insp ON violations(inspection_id)")
    con.commit()

    for t in ("inspections", "violations"):
        n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"{t}: {n:,} rows")
    con.close()


if __name__ == "__main__":
    main()
