"""Run the saved SQL files, write result tables, and produce figures."""
import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DB = Path("data/processed/inspections.db")
SQL = Path("sql")
FIGS = Path("outputs/figures")
TABLES = Path("outputs/tables")


def run_sql(con, filename: str) -> pd.DataFrame:
    query = (SQL / filename).read_text()
    return pd.read_sql_query(query, con)


def main():
    FIGS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)

    results = {}
    for f in sorted(SQL.glob("*.sql")):
        df = run_sql(con, f.name)
        df.to_csv(TABLES / f"{f.stem}.csv", index=False)
        results[f.stem] = df
        print(f"{f.name}: {len(df)} rows")

    con.close()

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Calibri", "Arial", "DejaVu Sans"]
    INK = "#1a1a1a"
    MUTED = "#6b6b6b"
    ACCENT = "#8c1d40"
    GREY = "#b8b8b8"

    def style(ax):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color("#d4d4d4")
            ax.spines[s].set_linewidth(0.8)
        ax.tick_params(colors=MUTED, labelsize=9.5, length=0)
        ax.set_axisbelow(True)

    # Chart 1: frequency vs severity, split at the medians
    v = results["02_top_violations_on_failures"].copy()
    mx, my = v["times_cited"].median(), v["pct_on_fail"].median()
    v["hot"] = (v["times_cited"] > mx) & (v["pct_on_fail"] > my)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.axvline(mx, color="#dddddd", linewidth=1, zorder=0)
    ax.axhline(my, color="#dddddd", linewidth=1, zorder=0)
    for hot, grp in v.groupby("hot"):
        ax.scatter(grp["times_cited"], grp["pct_on_fail"], s=90,
                   color=ACCENT if hot else GREY,
                   alpha=0.85 if hot else 0.55,
                   edgecolor="white", linewidth=1.2, zorder=3,
                   label="Frequent and predictive" if hot else "Everything else")
    ax.set_xscale("log")

    offsets = {55: (0, -22), 38: (12, 8), 59: (14, -4), 48: (12, 6)}
    for code, (dx, dy) in offsets.items():
        row = v[v["violation_code"] == code]
        if len(row):
            ax.annotate(f"Code {code}",
                        (row["times_cited"].iloc[0], row["pct_on_fail"].iloc[0]),
                        textcoords="offset points", xytext=(dx, dy),
                        fontsize=9.5, color=INK, weight="semibold")

    ax.text(0.985, 0.03, "common, but weakly predictive", transform=ax.transAxes,
            ha="right", fontsize=9, color=MUTED, style="italic")
    ax.set_xlabel("Times cited  (log scale)", fontsize=10.5, color=MUTED, labelpad=10)
    ax.set_ylabel("Share of citations on a failed inspection (%)", fontsize=10.5, color=MUTED, labelpad=10)
    ax.set_title("How often a violation is cited says little about how serious it is",
                 fontsize=14, color=INK, pad=18, loc="left")
    ax.legend(frameon=False, fontsize=9.5, labelcolor=MUTED, loc="upper right")
    style(ax)
    ax.grid(axis="y", color="#f2f2f2", linewidth=0.9)
    plt.tight_layout()
    plt.savefig(FIGS / "violation_frequency_vs_severity.png", dpi=220)
    plt.close()

        # Chart 2: failure rate by facility type, coloured by risk tier
    f = results["01_pass_fail_by_facility_type"].sort_values("fail_pct").reset_index(drop=True)
    palette = {1: "#8c1d40", 2: "#c2778a", 3: "#e6c3cc"}
    colors = [palette.get(r, GREY) for r in f["risk_level"]]
    ypos = range(len(f))

    fig, ax = plt.subplots(figsize=(9.5, 7.5))
    ax.barh(ypos, f["fail_pct"], color=colors, height=0.68, zorder=3)
    ax.set_yticks(list(ypos))
    ax.set_yticklabels(f["facility_type"])
    ax.set_ylim(-0.7, len(f) - 0.3)
    for i, val in enumerate(f["fail_pct"]):
        ax.text(val + 0.35, i, f"{val}", va="center", fontsize=9, color=MUTED)
    handles = [plt.Rectangle((0, 0), 1, 1, color=palette[k]) for k in (1, 2, 3)]
    ax.legend(handles, ["Risk 1 (highest)", "Risk 2", "Risk 3 (lowest)"],
              frameon=False, fontsize=9.5, labelcolor=MUTED, loc="lower right")
    ax.set_xlabel("Failure rate (%)", fontsize=10.5, color=MUTED, labelpad=10)
    ax.set_title("Establishment type separates failure rates more than risk tier does",
                 fontsize=14, color=INK, pad=18, loc="left")
    ax.tick_params(axis="y", labelsize=10)
    style(ax)
    ax.grid(axis="x", color="#f2f2f2", linewidth=0.9)
    plt.tight_layout()
    plt.savefig(FIGS / "fail_rate_by_facility_type.png", dpi=220)
    plt.close()

if __name__ == "__main__":
    main()
