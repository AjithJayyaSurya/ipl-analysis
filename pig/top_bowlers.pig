-- ============================================================
--  Apache Pig: Top 20 Bowlers by Wickets
--  Run: pig -f pig/top_bowlers.pig
-- ============================================================

-- Load deliveries data from HDFS
deliveries = LOAD '/ipl/data/deliveries/deliveries.csv'
    USING PigStorage(',')
    AS (
        match_id:int,
        inning:int,
        batting_team:chararray,
        bowling_team:chararray,
        over:int,
        ball:int,
        batsman:chararray,
        non_striker:chararray,
        bowler:chararray,
        is_super_over:int,
        wide_runs:int,
        bye_runs:int,
        legbye_runs:int,
        noball_runs:int,
        penalty_runs:int,
        batsman_runs:int,
        extra_runs:int,
        total_runs:int,
        player_dismissed:chararray,
        dismissal_kind:chararray,
        fielder:chararray
    );

-- Filter: only balls where a wicket fell (not run out, not super over)
wickets = FILTER deliveries BY
    player_dismissed IS NOT NULL
    AND player_dismissed != ''
    AND dismissal_kind != 'run out'
    AND dismissal_kind != 'retired hurt'
    AND dismissal_kind != 'obstructing the field'
    AND is_super_over == 0;

-- Group by bowler
bowler_group = GROUP wickets BY bowler;

-- Count wickets per bowler
bowler_stats = FOREACH bowler_group GENERATE
    group           AS bowler,
    COUNT(wickets)  AS wickets;

-- Sort by wickets descending
sorted = ORDER bowler_stats BY wickets DESC;

-- Get top 20
top20 = LIMIT sorted 20;

-- Print to screen
DUMP top20;

-- Store to HDFS
STORE top20 INTO '/ipl/output/pig_top_bowlers'
    USING PigStorage(',');
