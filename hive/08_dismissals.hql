-- ============================================================
--  Analysis 7: Dismissal Type Distribution
--  Finds: How batsmen get out — caught, bowled, lbw, etc.
--  Run: hive -f hive/08_dismissals.hql
-- ============================================================

USE ipl_db;

-- Print to screen
SELECT
    dismissal_kind,
    COUNT(*)                                           AS total_dismissals,
    -- Percentage share of each dismissal type
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM deliveries
WHERE player_dismissed IS NOT NULL
  AND player_dismissed <> ''
GROUP BY dismissal_kind
ORDER BY total_dismissals DESC;

-- Save output to HDFS
INSERT OVERWRITE DIRECTORY '/ipl/output/dismissals'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
    dismissal_kind,
    COUNT(*) AS total_dismissals,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM deliveries
WHERE player_dismissed IS NOT NULL
  AND player_dismissed <> ''
GROUP BY dismissal_kind
ORDER BY total_dismissals DESC;

-- BONUS: Most catches taken by fielders
SELECT
    fielder,
    COUNT(*) AS catches_taken
FROM deliveries
WHERE dismissal_kind = 'caught'
  AND fielder IS NOT NULL
  AND fielder <> ''
GROUP BY fielder
ORDER BY catches_taken DESC
LIMIT 15;
