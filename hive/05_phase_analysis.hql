-- ============================================================
--  Analysis 4: Powerplay vs Middle vs Death Phase
--  Finds: Run rate comparison across match phases per team
--  Run: hive -f hive/05_phase_analysis.hql
-- ============================================================

USE ipl_db;

-- Print to screen
SELECT
    batting_team,
    CASE
        WHEN over BETWEEN 1 AND 6   THEN '1_Powerplay (Overs 1-6)'
        WHEN over BETWEEN 7 AND 15  THEN '2_Middle    (Overs 7-15)'
        WHEN over BETWEEN 16 AND 20 THEN '3_Death     (Overs 16-20)'
    END                                           AS phase,
    SUM(total_runs)                               AS runs_scored,
    COUNT(*)                                      AS balls_bowled,
    -- Wickets fallen in this phase
    SUM(IF(player_dismissed IS NOT NULL
           AND player_dismissed <> '', 1, 0))     AS wickets_lost,
    ROUND(SUM(total_runs) * 6.0 / COUNT(*), 2)   AS run_rate
FROM deliveries
WHERE is_super_over = 0
GROUP BY
    batting_team,
    CASE
        WHEN over BETWEEN 1 AND 6   THEN '1_Powerplay (Overs 1-6)'
        WHEN over BETWEEN 7 AND 15  THEN '2_Middle    (Overs 7-15)'
        WHEN over BETWEEN 16 AND 20 THEN '3_Death     (Overs 16-20)'
    END
ORDER BY batting_team ASC, phase ASC;

-- Save output to HDFS
INSERT OVERWRITE DIRECTORY '/ipl/output/phase_analysis'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
    batting_team,
    CASE
        WHEN over BETWEEN 1 AND 6   THEN 'Powerplay'
        WHEN over BETWEEN 7 AND 15  THEN 'Middle'
        WHEN over BETWEEN 16 AND 20 THEN 'Death'
    END                                           AS phase,
    SUM(total_runs)                               AS runs_scored,
    COUNT(*)                                      AS balls_bowled,
    SUM(IF(player_dismissed IS NOT NULL
           AND player_dismissed <> '', 1, 0))     AS wickets_lost,
    ROUND(SUM(total_runs) * 6.0 / COUNT(*), 2)   AS run_rate
FROM deliveries
WHERE is_super_over = 0
GROUP BY batting_team,
    CASE
        WHEN over BETWEEN 1 AND 6   THEN 'Powerplay'
        WHEN over BETWEEN 7 AND 15  THEN 'Middle'
        WHEN over BETWEEN 16 AND 20 THEN 'Death'
    END
ORDER BY batting_team, phase;
