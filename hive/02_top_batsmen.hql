-- ============================================================
--  Analysis 1: Top 20 Batsmen
--  Finds: Total runs scored + Strike rate
--  Run: hive -f hive/02_top_batsmen.hql
-- ============================================================

USE ipl_db;

-- Print to screen
SELECT
    batsman,
    SUM(batsman_runs)                                AS total_runs,
    COUNT(*)                                         AS balls_faced,
    ROUND(SUM(batsman_runs) * 100.0 / COUNT(*), 2)  AS strike_rate
FROM deliveries
WHERE wide_runs = 0          -- exclude wides (batsman doesn't face those balls)
  AND is_super_over = 0      -- exclude super over deliveries
GROUP BY batsman
HAVING COUNT(*) >= 100       -- only players who faced at least 100 balls
ORDER BY total_runs DESC
LIMIT 20;

-- Save output to HDFS
INSERT OVERWRITE DIRECTORY '/ipl/output/top_batsmen'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
    batsman,
    SUM(batsman_runs)                                AS total_runs,
    COUNT(*)                                         AS balls_faced,
    ROUND(SUM(batsman_runs) * 100.0 / COUNT(*), 2)  AS strike_rate
FROM deliveries
WHERE wide_runs = 0
  AND is_super_over = 0
GROUP BY batsman
HAVING COUNT(*) >= 100
ORDER BY total_runs DESC
LIMIT 20;
