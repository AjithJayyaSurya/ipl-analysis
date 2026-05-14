-- ============================================================
--  Apache Pig: Top 20 Batsmen
--  Run: pig -f pig/top_batsmen.pig
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

-- Filter: remove wides and super overs
filtered = FILTER deliveries BY wide_runs == 0 AND is_super_over == 0;

-- Group by batsman
batsman_group = GROUP filtered BY batsman;

-- Compute total runs and balls faced per batsman
batsman_stats = FOREACH batsman_group GENERATE
    group                          AS batsman,
    SUM(filtered.batsman_runs)     AS total_runs,
    COUNT(filtered)                AS balls_faced;

-- Filter: only batsmen who faced at least 100 balls
qualified = FILTER batsman_stats BY balls_faced >= 100;

-- Sort by total runs descending
sorted = ORDER qualified BY total_runs DESC;

-- Get top 20
top20 = LIMIT sorted 20;

-- Print to screen
DUMP top20;

-- Store to HDFS
STORE top20 INTO '/ipl/output/pig_top_batsmen'
    USING PigStorage(',');
