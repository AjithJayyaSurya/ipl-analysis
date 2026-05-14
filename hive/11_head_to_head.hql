-- ============================================================
--  Analysis 10: Head-to-Head Team Comparison
--  Finds: Runs scored by each team against every other team
--  Run: hive -f hive/11_head_to_head.hql
-- ============================================================

USE ipl_db;

-- Part A: Run rate of each team vs each opponent
SELECT
    batting_team                                        AS team,
    bowling_team                                        AS opponent,
    COUNT(DISTINCT match_id)                            AS matches_played,
    SUM(total_runs)                                     AS total_runs_scored,
    ROUND(SUM(total_runs) * 6.0 / COUNT(*), 2)          AS run_rate_against_opponent
FROM deliveries
WHERE is_super_over = 0
GROUP BY batting_team, bowling_team
ORDER BY batting_team ASC, run_rate_against_opponent DESC;

-- Part B: Win count from matches table (who beats whom more)
SELECT
    team1,
    team2,
    winner,
    COUNT(*) AS wins
FROM matches
WHERE result = 'normal'
GROUP BY team1, team2, winner
ORDER BY team1 ASC, wins DESC;

-- Part C: Overall wins per team (season-wise)
SELECT
    season,
    winner,
    COUNT(*) AS wins
FROM matches
WHERE winner IS NOT NULL
  AND winner <> ''
GROUP BY season, winner
ORDER BY season ASC, wins DESC;

-- Save head-to-head run rates to HDFS
INSERT OVERWRITE DIRECTORY '/ipl/output/head_to_head'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT
    batting_team,
    bowling_team,
    COUNT(DISTINCT match_id)                    AS matches_played,
    SUM(total_runs)                             AS total_runs_scored,
    ROUND(SUM(total_runs) * 6.0 / COUNT(*), 2) AS run_rate
FROM deliveries
WHERE is_super_over = 0
GROUP BY batting_team, bowling_team
ORDER BY batting_team, bowling_team;
