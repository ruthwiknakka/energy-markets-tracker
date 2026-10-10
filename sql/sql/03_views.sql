CREATE OR REPLACE VIEW v_brent_wti_analysis AS
WITH wide AS (
    SELECT
        period,
        MAX(value) FILTER (WHERE series = 'RBRTE') AS brent,
        MAX(value) FILTER (WHERE series = 'RWTC')  AS wti
    FROM spot_prices
    GROUP BY period
),
spread AS (
    SELECT period, brent, wti, brent - wti AS spread
    FROM wide
    WHERE brent IS NOT NULL AND wti IS NOT NULL
)
SELECT
    period, brent, wti, spread,
    ROUND((wti / LAG(wti) OVER (ORDER BY period) - 1) * 100, 2) AS wti_daily_pct,
    ROUND(AVG(spread) OVER (
        ORDER BY period ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 2) AS spread_30d_avg,
    ROUND(PERCENT_RANK() OVER (ORDER BY spread)::numeric, 3) AS spread_percentile
FROM spread;