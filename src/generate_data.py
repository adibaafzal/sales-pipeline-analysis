"""Generate a reproducible, fully synthetic B2B sales pipeline dataset."""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
N_LEADS = 2000
rng = np.random.default_rng(SEED)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "leads.csv"

sources = {
    "LinkedIn Outreach": (0.25, 0.30),
    "Cold Email": (0.30, 0.14),
    "Cold Call": (0.20, 0.22),
    "Inbound Website": (0.15, 0.42),
    "Referral": (0.10, 0.55),
}
industries = ["SaaS", "Manufacturing", "E-commerce", "Fintech", "Logistics", "Healthcare"]
industry_lift = {"SaaS": 1.15, "Fintech": 1.10, "E-commerce": 1.0,
                 "Logistics": 0.95, "Manufacturing": 0.85, "Healthcare": 0.80}
company_sizes = ["1-50", "51-200", "201-1000", "1000+"]
size_weights = [0.35, 0.30, 0.22, 0.13]
size_deal = {"1-50": 6000, "51-200": 14000, "201-1000": 32000, "1000+": 65000}
reps = ["Rep A", "Rep B", "Rep C", "Rep D", "Rep E"]
rep_skill = {"Rep A": 1.20, "Rep B": 1.05, "Rep C": 1.00, "Rep D": 0.90, "Rep E": 0.80}
countries = ["Germany", "France", "Netherlands", "Spain", "Ireland", "Sweden", "Italy"]
stages = ["Lead", "Contacted", "Meeting", "Proposal", "Won", "Lost"]
source_names = list(sources)
source_probs = [sources[s][0] for s in source_names]
rows = []
start = np.datetime64("2024-01-01")
end = np.datetime64("2025-12-31")
days = int((end - start).astype("timedelta64[D]").astype(int))
for i in range(1, N_LEADS + 1):
    source = rng.choice(source_names, p=source_probs)
    industry = rng.choice(industries)
    company_size = rng.choice(company_sizes, p=size_weights)
    sales_rep = rng.choice(reps)
    created = start + np.timedelta64(int(rng.integers(0, days + 1)), "D")
    base = sources[source][1] * industry_lift[industry] * rep_skill[sales_rep]
    p_won = float(np.clip(base, 0.04, 0.78))
    outcome = rng.random()
    if outcome < p_won:
        stage = "Won"
        furthest = "Won"
        days_to_close = int(rng.integers(14, 121))
    elif outcome < p_won + 0.18:
        stage = "Proposal" if rng.random() < 0.5 else "Lost"
        furthest = "Proposal"
        days_to_close = int(rng.integers(20, 160))
    elif outcome < p_won + 0.40:
        stage = "Meeting" if rng.random() < 0.6 else "Lost"
        furthest = "Meeting"
        days_to_close = int(rng.integers(7, 130))
    elif outcome < p_won + 0.67:
        stage = "Contacted" if rng.random() < 0.65 else "Lost"
        furthest = "Contacted"
        days_to_close = int(rng.integers(1, 100))
    else:
        stage = "Lead"
        furthest = "Lead"
        days_to_close = int(rng.integers(0, 60))
    deal_value = int(max(1000, rng.normal(size_deal[company_size], size_deal[company_size] * 0.22)))
    rows.append({"lead_id": i, "created_date": str(created), "source": source,
                 "industry": industry, "company_size": company_size,
                 "country": rng.choice(countries), "sales_rep": sales_rep,
                 "stage": stage, "furthest_stage": furthest,
                 "deal_value_eur": deal_value,
                 "days_to_close": days_to_close})

ROOT.joinpath("data").mkdir(exist_ok=True)
pd.DataFrame(rows).to_csv(OUT, index=False)
print(f"Generated {N_LEADS:,} synthetic leads at {OUT}")
