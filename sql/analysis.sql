-- Sales Pipeline Analysis (SQLite)
-- Input table: leads
-- Fields: lead_id, created_date, source, industry, company_size, country,
-- sales_rep, stage, furthest_stage, deal_value_eur, days_to_close.

-- 1. Funnel: count leads that reached each stage.
SELECT 'Lead' AS stage, COUNT(*) AS leads FROM leads
UNION ALL
SELECT 'Contacted', COUNT(*) FROM leads WHERE furthest_stage IN ('Contacted','Meeting','Proposal','Won')
UNION ALL
SELECT 'Meeting', COUNT(*) FROM leads WHERE furthest_stage IN ('Meeting','Proposal','Won')
UNION ALL
SELECT 'Proposal', COUNT(*) FROM leads WHERE furthest_stage IN ('Proposal','Won')
UNION ALL
SELECT 'Won', COUNT(*) FROM leads WHERE stage = 'Won';

-- 2. Conversion and revenue by lead source.
SELECT source, COUNT(*) AS leads,
       SUM(stage = 'Won') AS deals_won,
       ROUND(100.0 * SUM(stage = 'Won') / COUNT(*), 1) AS win_rate_pct,
       ROUND(SUM(CASE WHEN stage = 'Won' THEN deal_value_eur END), 0) AS revenue_eur,
       ROUND(AVG(CASE WHEN stage = 'Won' THEN days_to_close END), 0) AS avg_days_to_close
FROM leads GROUP BY source ORDER BY win_rate_pct DESC;

-- 3. Win rate and average deal size by company size.
SELECT company_size, COUNT(*) AS leads,
       ROUND(100.0 * SUM(stage = 'Won') / COUNT(*), 1) AS win_rate_pct,
       ROUND(AVG(CASE WHEN stage = 'Won' THEN deal_value_eur END), 0) AS avg_deal_eur
FROM leads GROUP BY company_size ORDER BY avg_deal_eur DESC;

-- 4. Sales rep performance.
SELECT sales_rep, COUNT(*) AS leads, SUM(stage = 'Won') AS deals_won,
       ROUND(100.0 * SUM(stage = 'Won') / COUNT(*), 1) AS win_rate_pct,
       ROUND(SUM(CASE WHEN stage = 'Won' THEN deal_value_eur END), 0) AS revenue_eur
FROM leads GROUP BY sales_rep ORDER BY revenue_eur DESC;

-- 5. Industry performance.
SELECT industry, COUNT(*) AS leads,
       ROUND(100.0 * SUM(stage = 'Won') / COUNT(*), 1) AS win_rate_pct,
       ROUND(SUM(CASE WHEN stage = 'Won' THEN deal_value_eur END), 0) AS revenue_eur
FROM leads GROUP BY industry ORDER BY win_rate_pct DESC;

-- 6. Monthly new leads and revenue won (by lead creation month).
SELECT substr(created_date, 1, 7) AS month, COUNT(*) AS new_leads,
       ROUND(SUM(CASE WHEN stage = 'Won' THEN deal_value_eur END), 0) AS revenue_eur
FROM leads GROUP BY month ORDER BY month;
