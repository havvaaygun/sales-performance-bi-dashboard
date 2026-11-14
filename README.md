 Sales Performance Analysis

Sales analysis for a retail company with five regions in Northern Cyprus:
revenue, profit, monthly trend, product and category performance, and
regional results against targets.

![Dashboard](dashboard/dashboard_sales_performance.png)

## Data

6,000 orders between January 2023 and December 2025, plus monthly revenue
targets per region. The data is synthetic and comes from
`python/01_generate_data.py`.

## Results

| KPI | Value |
|---|---|
| Revenue | ₺7.70M |
| Profit | ₺1.67M |
| Profit margin | 21.6% |
| Orders | 6,000 |
| Average order value | ₺1,284 |
| Revenue growth | +14.0% (2024), +7.2% (2025) |

- Elektronik brings in 72% of revenue but has a 17% margin. Giyim has the
  highest margin (45%) with only 7% of revenue, so it is the main room for
  margin growth.
- Market has the fewest orders and the lowest margin (13%).
- All five regions are above target (101–104%). Lefkoşa is the largest
  region, Güzelyurt has the highest attainment.

## Files

- `sql/analysis_queries.sql`: KPIs, monthly growth with `LAG`, top products,
  target vs actual, year-over-year growth, sales rep ranking (PostgreSQL)
- `python/02_analysis.py`: the same metrics in pandas, saved to `reports/`
- `reports/charts/`: charts for each analysis

## Run

```bash
pip install -r requirements.txt
python python/01_generate_data.py
python python/02_analysis.py
```
