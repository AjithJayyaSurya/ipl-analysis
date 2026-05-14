-- ============================================================
--  Analysis 3: Team Batting Stats
--  Finds: Total runs, balls, and run rate per team
--  Run: hive -f hive/04_team_batting.hql
-- ============================================================

USE ipl_db;

-- Print to screen
SELECT
    batting_team,
    SUM(total_runs)                                                         AS total_runs,
    SUM(batsman_runs)                                                       AS bat_runs,
    SUM(extra_runs)                                                         AS extras,
    COUNT(*)                                                                AS total_balls,
    -- Run rate = (total runs / valid balls) * 6
    ROUND(
        SUM(total_runs) * 6.0 / (COUNT(*) - SUM(IF(wide_runs > 0, 1, 0))),
    2)                                                                      AS run_rate
FROM deliveries
WHERE is_super_over = 0
GROUP BY batting_team
ORDER BY run_rate DESC;

-- Save output to HDFS
INSERT OVERWRITE DIRECTORY '/ipl/output/team_batting'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
    batting_team,
    SUM(total_runs)   AS total_runs,
    SUM(batsman_runs) AS bat_runs,
    SUM(extra_runs)   AS extras,
    COUNT(*)          AS total_balls,
    ROUND(SUM(total_runs) * 6.0 / (COUNT(*) - SUM(IF(wide_runs > 0, 1, 0))), 2) AS run_rate
FROM deliveries
WHERE is_super_over = 0
GROUP BY batting_team
ORDER BY run_rate DESC;
