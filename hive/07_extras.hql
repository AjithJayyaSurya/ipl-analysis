-- ============================================================
--  Analysis 6: Extras / Bowling Discipline per Team
--  Finds: Teams with fewest extras — best disciplined bowling
--  Run: hive -f hive/07_extras.hql
-- ============================================================

USE ipl_db;

-- Print to screen
SELECT
    bowling_team,
    SUM(wide_runs)                               AS total_wides,
    SUM(noball_runs)                             AS total_no_balls,
    SUM(bye_runs)                                AS total_byes,
    SUM(legbye_runs)                             AS total_leg_byes,
    SUM(extra_runs)                              AS total_extras,
    COUNT(*)                                     AS total_balls_bowled,
    -- Extras per 100 balls = discipline metric (lower is better)
    ROUND(SUM(extra_runs) * 100.0 / COUNT(*), 2) AS extras_per_100_balls
FROM deliveries
WHERE is_super_over = 0
GROUP BY bowling_team
ORDER BY extras_per_100_balls ASC;   -- ASC = best discipline at top

-- Save output to HDFS
INSERT OVERWRITE DIRECTORY '/ipl/output/extras'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
    bowling_team,
    SUM(wide_runs)   AS total_wides,
    SUM(noball_runs) AS total_no_balls,
    SUM(bye_runs)    AS total_byes,
    SUM(legbye_runs) AS total_leg_byes,
    SUM(extra_runs)  AS total_extras,
    COUNT(*)         AS total_balls_bowled,
    ROUND(SUM(extra_runs) * 100.0 / COUNT(*), 2) AS extras_per_100_balls
FROM deliveries
WHERE is_super_over = 0
GROUP BY bowling_team
ORDER BY extras_per_100_balls ASC;
