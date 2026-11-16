# Sales Pipeline Analysis

SQL + Python analysis of a synthetic B2B sales pipeline dataset. The project explores lead funnel conversion, revenue, sales-representative performance, lead sources, industries, company sizes and monthly trends.

## Project structure

```text
sales-pipeline-analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── charts/
├── data/
├── results/
├── sql/
└── src/
```

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Reproduce the analysis

From the repository root:

```bash
python src/generate_data.py
python src/analyse.py
```

The dataset is fully synthetic; no real company or customer data is used.
