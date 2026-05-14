-- ============================================================
--  Analysis 9: Economy Rates — Best Bowlers
--  Finds: Best economy among bowlers who bowled min 100 overs
--  Run: hive -f hive/10_economy.hql
-- ============================================================

USE ipl_db;

-- Print to screen
SELECT
    bowler,
    COUNT(*)                                         AS legal_balls,
    ROUND(COUNT(*) / 6.0, 1)                         AS overs_bowled,
    SUM(total_runs)                                  AS runs_conceded,
    -- Economy = runs per over = (runs / balls) * 6
    ROUND(SUM(total_runs) * 6.0 / COUNT(*), 2)       AS economy_rate,
    -- Wickets for context
    SUM(
        IF(player_dismissed IS NOT NULL
           AND player_dismissed <> ''
           AND dismissal_kind NOT IN ('run out','retired hurt'),
        1, 0)
    )                                                AS wickets
FROM deliveries
WHERE is_super_over = 0
  AND wide_runs = 0              -- legal deliveries only for economy calc
GROUP BY bowler
HAVING COUNT(*) >= 600           -- minimum 100 overs (600 legal balls)
ORDER BY economy_rate ASC
LIMIT 20;

-- Save output to HDFS
INSERT OVERWRITE DIRECTORY '/ipl/output/economy'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
    bowler,
    COUNT(*)                                                       AS legal_balls,
    ROUND(COUNT(*) / 6.0, 1)                                       AS overs_bowled,
    SUM(total_runs)                                                AS runs_conceded,
    ROUND(SUM(total_runs) * 6.0 / COUNT(*), 2)                     AS economy_rate,
    SUM(IF(player_dismissed IS NOT NULL
           AND player_dismissed <> ''
           AND dismissal_kind NOT IN ('run out','retired hurt'), 1, 0)) AS wickets
FROM deliveries
WHERE is_super_over = 0
  AND wide_runs = 0
GROUP BY bowler
HAVING COUNT(*) >= 600
ORDER BY economy_rate ASC
LIMIT 20;
