-- ============================================================
--  Analysis 5: Boundaries — Most 4s and 6s per Batsman
--  Finds: Total fours, sixes, and combined boundaries per player
--  Run: hive -f hive/06_boundaries.hql
-- ============================================================

USE ipl_db;

-- Print to screen
SELECT
    batsman,
    SUM(IF(batsman_runs = 4, 1, 0))            AS fours,
    SUM(IF(batsman_runs = 6, 1, 0))            AS sixes,
    SUM(IF(batsman_runs IN (4, 6), 1, 0))      AS total_boundaries,
    -- Boundary runs (4s contribute 4, 6s contribute 6)
    SUM(IF(batsman_runs = 4, 4, 0)) +
    SUM(IF(batsman_runs = 6, 6, 0))            AS boundary_runs
FROM deliveries
WHERE is_super_over = 0
GROUP BY batsman
ORDER BY total_boundaries DESC
LIMIT 20;

-- Save output to HDFS
INSERT OVERWRITE DIRECTORY '/ipl/output/boundaries'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
    batsman,
    SUM(IF(batsman_runs = 4, 1, 0))            AS fours,
    SUM(IF(batsman_runs = 6, 1, 0))            AS sixes,
    SUM(IF(batsman_runs IN (4, 6), 1, 0))      AS total_boundaries,
    SUM(IF(batsman_runs = 4, 4, 0)) +
    SUM(IF(batsman_runs = 6, 6, 0))            AS boundary_runs
FROM deliveries
WHERE is_super_over = 0
GROUP BY batsman
ORDER BY total_boundaries DESC
LIMIT 20;
