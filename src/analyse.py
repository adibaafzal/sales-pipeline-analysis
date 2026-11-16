"""Load leads into SQLite, run the SQL analysis, and export result tables/charts."""
from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "leads.csv"
SQL = ROOT / "sql" / "analysis.sql"
CHARTS = ROOT / "charts"
RESULTS = ROOT / "results"
CHARTS.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

BLUE, GREY = "#2E5A88", "#B8C4D0"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})

df = pd.read_csv(DATA)
con = sqlite3.connect(":memory:")
df.to_sql("leads", con, index=False)
blocks = [b.strip() for b in SQL.read_text(encoding="utf-8").split("\n-- ") if "SELECT" in b.upper()]
names = ["funnel", "by_source", "by_company_size", "by_rep", "by_industry", "monthly"]
results = {}
for name, block in zip(names, blocks):
    query = block[block.upper().find("SELECT"):] if not block.lstrip().upper().startswith("SELECT") else block
    results[name] = pd.read_sql_query(query.rstrip(";"), con)
    results[name].to_csv(RESULTS / f"{name}.csv", index=False)

# Funnel chart
f = results["funnel"]
fig, ax = plt.subplots(figsize=(7, 3.6))
bars = ax.bar(f["stage"], f["leads"], color=BLUE)
for bar, value in zip(bars, f["leads"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()+15,
            f"{value:,}", ha="center")
ax.set_title("Sales funnel: leads reaching each stage", loc="left", fontweight="bold")
ax.set_ylabel("Number of leads")
fig.tight_layout(); fig.savefig(CHARTS / "1_funnel.png", dpi=150); plt.close(fig)

# Win rate by source
s = results["by_source"].sort_values("win_rate_pct")
fig, ax = plt.subplots(figsize=(7, 3.6))
bars = ax.barh(s["source"], s["win_rate_pct"], color=[BLUE if i >= len(s)-2 else GREY for i in range(len(s))])
for bar, value in zip(bars, s["win_rate_pct"]):
    ax.text(value + 0.3, bar.get_y()+bar.get_height()/2, f"{value:.1f}%", va="center")
ax.set_title("Win rate by lead source", loc="left", fontweight="bold")
ax.set_xlabel("Leads that became won deals (%)")
fig.tight_layout(); fig.savefig(CHARTS / "2_win_rate_by_source.png", dpi=150); plt.close(fig)

# Revenue by sales rep
r = results["by_rep"].sort_values("revenue_eur")
fig, ax = plt.subplots(figsize=(7, 3.6))
bars = ax.barh(r["sales_rep"], r["revenue_eur"] / 1000, color=BLUE)
for bar, value, rate in zip(bars, r["revenue_eur"] / 1000, r["win_rate_pct"]):
    ax.text(value + 10, bar.get_y()+bar.get_height()/2,
            f"€{value:,.1f}k ({rate:.1f}% win rate)", va="center")
ax.set_title("Revenue won by sales rep", loc="left", fontweight="bold")
ax.set_xlabel("Revenue (€ thousands)")
ax.set_xlim(0, max(r["revenue_eur"] / 1000) * 1.45)
fig.tight_layout(); fig.savefig(CHARTS / "3_revenue_by_rep.png", dpi=150); plt.close(fig)

# Monthly revenue trend
m = results["monthly"]
fig, ax = plt.subplots(figsize=(8, 3.6))
ax.plot(m["month"], m["revenue_eur"] / 1000, color=BLUE, marker="o")
ax.set_title("Revenue won by month of lead creation", loc="left", fontweight="bold")
ax.set_ylabel("€ thousands")
ax.tick_params(axis="x", rotation=45)
ax.set_ylim(bottom=0)
fig.tight_layout(); fig.savefig(CHARTS / "4_monthly_revenue.png", dpi=150); plt.close(fig)

for name, table in results.items():
    print(f"\n=== {name} ===")
    print(table.to_string(index=False))
