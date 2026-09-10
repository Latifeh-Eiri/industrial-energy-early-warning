-- =========================================================
-- Operational Energy Risk Intelligence
-- SQL Analysis
-- =========================================================
-- Purpose:
-- Explore industrial energy-demand patterns and identify
-- operational conditions associated with future high demand.
-- =========================================================

CREATE TABLE IF NOT EXISTS energy_ml_ready (
    window_start_utc TIMESTAMP,
    demand_kw DOUBLE PRECISION,
    demand_15m_ago DOUBLE PRECISION,
    demand_30m_ago DOUBLE PRECISION,
    demand_45m_ago DOUBLE PRECISION,
    demand_60m_ago DOUBLE PRECISION,
    change_15m DOUBLE PRECISION,
    change_60m DOUBLE PRECISION,
    rolling_mean_1h DOUBLE PRECISION,
    rolling_std_1h DOUBLE PRECISION,
    demand_threshold_ratio DOUBLE PRECISION,
    hour INTEGER,
    day_of_week INTEGER,
    is_weekend INTEGER,
    asset_id VARCHAR(50),
    asset_type VARCHAR(100),
    extreme_1h_ahead INTEGER
);

-- =========================================================
-- Data Validation
-- =========================================================

SELECT COUNT(*) AS total_rows
FROM energy_ml_ready;

-- Date range
SELECT
    MIN(window_start_utc) AS start_date,
    MAX(window_start_utc) AS end_date
FROM energy_ml_ready;


-- Number of assets and system types
SELECT
    COUNT(DISTINCT asset_id) AS number_of_assets,
    COUNT(DISTINCT asset_type) AS number_of_system_types
FROM energy_ml_ready;


-- Target distribution
SELECT
    extreme_1h_ahead,
    COUNT(*) AS observations,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM energy_ml_ready
GROUP BY extreme_1h_ahead
ORDER BY extreme_1h_ahead;


-- =========================================================
-- 1. Average Energy Demand by Asset Type
-- =========================================================

SELECT
    asset_type,
    COUNT(*) AS observations,
    ROUND(AVG(demand_kw)::numeric, 2) AS avg_demand_kw,
    ROUND(MAX(demand_kw)::numeric, 2) AS max_demand_kw
FROM energy_ml_ready
GROUP BY asset_type
ORDER BY avg_demand_kw DESC;


-- =========================================================
-- 2. High-Demand Risk by Asset Type
-- =========================================================

SELECT
    asset_type,
    COUNT(*) AS observations,
    SUM(extreme_1h_ahead) AS high_demand_observations,
    ROUND(
        100.0 * AVG(extreme_1h_ahead),
        2
    ) AS high_demand_rate_pct
FROM energy_ml_ready
GROUP BY asset_type
ORDER BY high_demand_rate_pct DESC;

-- =========================================================
-- 3. High-Demand Risk: Weekday vs Weekend
-- =========================================================

SELECT
    CASE
        WHEN is_weekend = 0 THEN 'Weekday'
        WHEN is_weekend = 1 THEN 'Weekend'
    END AS day_type,
    COUNT(*) AS observations,
    SUM(extreme_1h_ahead) AS high_demand_observations,
    ROUND(
        100.0 * AVG(extreme_1h_ahead),
        2
    ) AS high_demand_rate_pct
FROM energy_ml_ready
GROUP BY is_weekend
ORDER BY is_weekend;

-- =========================================================
-- 4. High-Demand Risk by Time of Day
-- =========================================================

SELECT
    CASE
        WHEN hour BETWEEN 0 AND 5 THEN 'Night'
        WHEN hour BETWEEN 6 AND 11 THEN 'Morning'
        WHEN hour BETWEEN 12 AND 17 THEN 'Afternoon'
        ELSE 'Evening'
    END AS time_of_day,

    COUNT(*) AS observations,

    ROUND(
        100.0 * AVG(extreme_1h_ahead),
        2
    ) AS high_demand_rate_pct

FROM energy_ml_ready

GROUP BY
    CASE
        WHEN hour BETWEEN 0 AND 5 THEN 'Night'
        WHEN hour BETWEEN 6 AND 11 THEN 'Morning'
        WHEN hour BETWEEN 12 AND 17 THEN 'Afternoon'
        ELSE 'Evening'
    END

ORDER BY high_demand_rate_pct DESC;

-- =========================================================
-- 5. Rank Assets by High-Demand Risk
-- =========================================================

WITH asset_risk AS (
    SELECT
        asset_id,
        asset_type,
        COUNT(*) AS observations,
        ROUND(
            100.0 * AVG(extreme_1h_ahead),
            2
        ) AS high_demand_rate_pct
    FROM energy_ml_ready
    GROUP BY asset_id, asset_type
)

SELECT
    RANK() OVER (
        ORDER BY high_demand_rate_pct DESC
    ) AS risk_rank,
    asset_id,
    asset_type,
    observations,
    high_demand_rate_pct
FROM asset_risk
ORDER BY risk_rank
LIMIT 10;

-- =========================================================
-- 6. Demand Behaviour Before Future High-Demand Conditions
-- =========================================================

SELECT
    CASE
        WHEN extreme_1h_ahead = 1 THEN 'High demand in 1 hour'
        ELSE 'Normal in 1 hour'
    END AS future_status,

    ROUND(AVG(demand_kw)::numeric, 2) AS avg_current_demand_kw,

    ROUND(AVG(change_60m)::numeric, 2) AS avg_change_last_60m_kw,

    ROUND(AVG(demand_threshold_ratio)::numeric, 2) AS avg_threshold_ratio

FROM energy_ml_ready
GROUP BY extreme_1h_ahead
ORDER BY extreme_1h_ahead DESC;

-- =========================================================
-- 7. Detect Large 1-Hour Demand Increases
-- =========================================================

WITH demand_history AS (
    SELECT
        asset_id,
        window_start_utc,
        demand_kw,

        LAG(demand_kw, 4) OVER (
            PARTITION BY asset_id
            ORDER BY window_start_utc
        ) AS demand_1h_before

    FROM energy_ml_ready
),

demand_changes AS (
    SELECT
        asset_id,
        window_start_utc,
        demand_kw,
        demand_1h_before,
        demand_kw - demand_1h_before AS demand_change_1h
    FROM demand_history
    WHERE demand_1h_before IS NOT NULL
)

SELECT
    asset_id,
    ROUND(AVG(demand_change_1h)::numeric, 2) AS avg_change_1h_kw,
    ROUND(MAX(demand_change_1h)::numeric, 2) AS max_increase_1h_kw
FROM demand_changes
GROUP BY asset_id
ORDER BY max_increase_1h_kw DESC
LIMIT 10;

-- =========================================================
-- 8. Tableau-Ready Operational Energy View
-- =========================================================

CREATE OR REPLACE VIEW vw_energy_dashboard AS

SELECT
    window_start_utc,
    asset_id,
    asset_type,
    demand_kw,
    demand_15m_ago,
    demand_60m_ago,
    change_15m,
    change_60m,
    rolling_mean_1h,
    rolling_std_1h,
    demand_threshold_ratio,
    hour,
    day_of_week,
    is_weekend,
    extreme_1h_ahead,

    CASE
        WHEN is_weekend = 0 THEN 'Weekday'
        ELSE 'Weekend'
    END AS day_type,

    CASE
        WHEN hour BETWEEN 0 AND 5 THEN 'Night'
        WHEN hour BETWEEN 6 AND 11 THEN 'Morning'
        WHEN hour BETWEEN 12 AND 17 THEN 'Afternoon'
        ELSE 'Evening'
    END AS time_of_day

FROM energy_ml_ready;

SELECT *
FROM vw_energy_dashboard
LIMIT 10;


