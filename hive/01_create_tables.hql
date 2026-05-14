-- ============================================================
--  IPL Big Data Project — Step 1: Create Database & Tables
--  Run: hive -f hive/01_create_tables.hql
-- ============================================================

-- Create and select database
CREATE DATABASE IF NOT EXISTS ipl_db
COMMENT 'IPL Cricket Analytics Database';

USE ipl_db;

-- ------------------------------------------------------------
-- Drop tables if they already exist (safe re-run)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS deliveries;

-- ------------------------------------------------------------
-- TABLE 1: matches
-- One row per IPL match (2008 onwards)
-- ------------------------------------------------------------
CREATE EXTERNAL TABLE matches (
    id                INT        COMMENT 'Unique match ID',
    season            INT        COMMENT 'IPL season year',
    city              STRING     COMMENT 'City where match was played',
    match_date        STRING     COMMENT 'Date of match',
    team1             STRING     COMMENT 'First team',
    team2             STRING     COMMENT 'Second team',
    toss_winner       STRING     COMMENT 'Team that won the toss',
    toss_decision     STRING     COMMENT 'bat or field',
    result            STRING     COMMENT 'normal / tie / no result',
    dl_applied        INT        COMMENT '1 if Duckworth-Lewis applied',
    winner            STRING     COMMENT 'Winning team name',
    win_by_runs       INT        COMMENT 'Win margin in runs (0 if won by wickets)',
    win_by_wickets    INT        COMMENT 'Win margin in wickets (0 if won by runs)',
    player_of_match   STRING     COMMENT 'Player of the match',
    venue             STRING     COMMENT 'Stadium name',
    umpire1           STRING     COMMENT 'On-field umpire 1',
    umpire2           STRING     COMMENT 'On-field umpire 2',
    umpire3           STRING     COMMENT 'Third umpire'
)
COMMENT 'IPL match-level data'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/ipl/data/matches/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- ------------------------------------------------------------
-- TABLE 2: deliveries
-- Ball-by-ball data for every delivery bowled
-- ------------------------------------------------------------
CREATE EXTERNAL TABLE deliveries (
    match_id          INT        COMMENT 'FK -> matches.id',
    inning            INT        COMMENT '1 = first innings, 2 = second innings',
    batting_team      STRING     COMMENT 'Team currently batting',
    bowling_team      STRING     COMMENT 'Team currently bowling',
    over              INT        COMMENT 'Over number (1-20)',
    ball              INT        COMMENT 'Ball number within the over',
    batsman           STRING     COMMENT 'Batsman on strike',
    non_striker       STRING     COMMENT 'Batsman at non-striker end',
    bowler            STRING     COMMENT 'Bowler bowling this delivery',
    is_super_over     INT        COMMENT '1 if this is a super over delivery',
    wide_runs         INT        COMMENT 'Wide runs conceded',
    bye_runs          INT        COMMENT 'Bye runs conceded',
    legbye_runs       INT        COMMENT 'Leg bye runs conceded',
    noball_runs       INT        COMMENT 'No ball runs conceded',
    penalty_runs      INT        COMMENT 'Penalty runs',
    batsman_runs      INT        COMMENT 'Runs scored off the bat',
    extra_runs        INT        COMMENT 'Total extra runs this ball',
    total_runs        INT        COMMENT 'Total runs this delivery',
    player_dismissed  STRING     COMMENT 'Name of dismissed player (NULL if no wicket)',
    dismissal_kind    STRING     COMMENT 'Type: caught/bowled/lbw/run out/stumped etc.',
    fielder           STRING     COMMENT 'Fielder involved in dismissal'
)
COMMENT 'IPL ball-by-ball delivery data'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/ipl/data/deliveries/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- ------------------------------------------------------------
-- Verify: Print row counts
-- ------------------------------------------------------------
SELECT 'matches count'   AS label, COUNT(*) AS total FROM matches
UNION ALL
SELECT 'deliveries count' AS label, COUNT(*) AS total FROM deliveries;
