-- ============================================================
--  Analysis 8: Inning Scores — Avg / Max / Min
--  Finds: Score statistics for 1st and 2nd innings separately
--  Run: hive -f hive/09_inning_scores.hql
-- ============================================================

USE ipl_db;

-- Print to screen
SELECT
    inning,
    ROUND(AVG(inning_total), 2)  AS avg_score,
    MAX(inning_total)            AS max_score,
    MIN(inning_total)            AS min_score,
    COUNT(*)                     AS total_innings_played
FROM (
    -- Inner query: calculate total runs per innings per match
    SELECT
        match_id,
        inning,
        SUM(total_runs) AS inning_total
    FROM deliveries
    WHERE is_super_over = 0
    GROUP BY match_id, inning
) inning_scores
GROUP BY inning
ORDER BY inning;

-- BONUS: Top 10 highest team innings scores ever
SELECT
    match_id,
    inning,
    batting_team,
    SUM(total_runs) AS total_score
FROM deliveries
WHERE is_super_over = 0
GROUP BY match_id, inning, batting_team
ORDER BY total_score DESC
LIMIT 10;

-- Save output to HDFS
INSERT OVERWRITE DIRECTORY '/ipl/output/inning_scores'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
    inning,
    ROUND(AVG(inning_total), 2) AS avg_score,
    MAX(inning_total)           AS max_score,
    MIN(inning_total)           AS min_score,
    COUNT(*)                    AS total_innings_played
FROM (
    SELECT match_id, inning, SUM(total_runs) AS inning_total
    FROM deliveries
    WHERE is_super_over = 0
    GROUP BY match_id, inning
) t
GROUP BY inning
ORDER BY inning;
