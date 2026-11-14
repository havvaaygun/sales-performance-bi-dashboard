-- =====================================================================
-- Sales Performance BI Dashboard - SQL analysis layer (PostgreSQL)
-- =====================================================================
-- These queries reproduce the KPIs that the Python/Power BI layer shows.
-- Load data/sales_data.csv and data/targets.csv into the tables below.
-- =====================================================================

-- ---------- Schema ---------------------------------------------------
DROP TABLE IF EXISTS sales;
CREATE TABLE sales (
    order_id      TEXT,
    order_date    DATE,
    region        TEXT,
    category      TEXT,
    product_name  TEXT,
    quantity      INT,
    unit_price    NUMERIC(10,2),
    unit_cost     NUMERIC(10,2),
    sales_rep     TEXT,
    customer_id   TEXT,
    revenue       NUMERIC(12,2),
    profit        NUMERIC(12,2)
);

DROP TABLE IF EXISTS targets;
CREATE TABLE targets (
    month           TEXT,       -- 'YYYY-MM'
    region          TEXT,
    target_revenue  NUMERIC(14,2)
);

-- \copy sales   FROM 'data/sales_data.csv' CSV HEADER;
-- \copy targets FROM 'data/targets.csv'    CSV HEADER;


-- ---------- 1. Headline KPIs ----------------------------------------
SELECT
    ROUND(SUM(revenue), 2)                           AS total_revenue,
    ROUND(SUM(profit), 2)                            AS total_profit,
    ROUND(100.0 * SUM(profit) / SUM(revenue), 2)     AS profit_margin_pct,
    COUNT(DISTINCT order_id)                          AS total_orders,
    COUNT(DISTINCT customer_id)                       AS unique_customers,
    ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
    ROUND(SUM(revenue) / COUNT(DISTINCT customer_id), 2) AS revenue_per_customer
FROM sales;


-- ---------- 2. Monthly revenue, profit and MoM growth ---------------
WITH monthly AS (
    SELECT
        to_char(order_date, 'YYYY-MM') AS month,
        SUM(revenue)                   AS revenue,
        SUM(profit)                    AS profit
    FROM sales
    GROUP BY 1
)
SELECT
    month,
    revenue,
    profit,
    ROUND(100.0 * profit / revenue, 2) AS profit_margin_pct,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
          / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2) AS mom_growth_pct
FROM monthly
ORDER BY month;


-- ---------- 3. Top 10 products by revenue ---------------------------
SELECT
    category,
    product_name,
    SUM(quantity)        AS units_sold,
    ROUND(SUM(revenue),2) AS revenue,
    ROUND(SUM(profit),2)  AS profit
FROM sales
GROUP BY category, product_name
ORDER BY revenue DESC
LIMIT 10;


-- ---------- 4. Region performance: target vs actual -----------------
WITH actual AS (
    SELECT region,
           SUM(revenue) AS revenue,
           SUM(profit)  AS profit
    FROM sales
    GROUP BY region
),
tgt AS (
    SELECT region, SUM(target_revenue) AS target_revenue
    FROM targets
    GROUP BY region
)
SELECT
    a.region,
    a.revenue,
    t.target_revenue,
    ROUND(100.0 * a.revenue / NULLIF(t.target_revenue, 0), 1) AS attainment_pct,
    ROUND(100.0 * a.profit / a.revenue, 1)                    AS profit_margin_pct
FROM actual a
JOIN tgt t USING (region)
ORDER BY a.revenue DESC;


-- ---------- 5. Year-over-year growth --------------------------------
WITH yearly AS (
    SELECT EXTRACT(YEAR FROM order_date)::INT AS year,
           SUM(revenue)                       AS revenue
    FROM sales
    GROUP BY 1
)
SELECT
    year,
    ROUND(revenue, 2) AS revenue,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year))
          / NULLIF(LAG(revenue) OVER (ORDER BY year), 0), 1) AS yoy_growth_pct
FROM yearly
ORDER BY year;


-- ---------- 6. Sales rep leaderboard --------------------------------
SELECT
    sales_rep,
    COUNT(DISTINCT order_id)      AS orders,
    ROUND(SUM(revenue), 2)        AS revenue,
    ROUND(AVG(revenue), 2)        AS avg_order_value
FROM sales
GROUP BY sales_rep
ORDER BY revenue DESC;
