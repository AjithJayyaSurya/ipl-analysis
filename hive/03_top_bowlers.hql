-- ============================================================
--  Analysis 2: Top 20 Bowlers by Wickets
--  Finds: Wicket count (run-outs excluded — not bowler's credit)
--  Run: hive -f hive/03_top_bowlers.hql
-- ============================================================

USE ipl_db;

-- Print to screen
SELECT
    bowler,
    COUNT(*) AS wickets
FROM deliveries
WHERE player_dismissed IS NOT NULL
  AND player_dismissed <> ''
  AND dismissal_kind NOT IN (
      'run out',
      'retired hurt',
      'obstructing the field'
  )
  AND is_super_over = 0
GROUP BY bowler
ORDER BY wickets DESC
LIMIT 20;

-- Save output to HDFS
INSERT OVERWRITE DIRECTORY '/ipl/output/top_bowlers'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
    bowler,
    COUNT(*) AS wickets
FROM deliveries
WHERE player_dismissed IS NOT NULL
  AND player_dismissed <> ''
  AND dismissal_kind NOT IN ('run out','retired hurt','obstructing the field')
  AND is_super_over = 0
GROUP BY bowler
ORDER BY wickets DESC
LIMIT 20;
