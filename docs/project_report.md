# IPL Big Data Analytics — Project Report

**Department:** Computer Science / Information Technology
**Subject:** Big Data Analytics
**Tool Used:** Apache Hive (HiveQL) on Hadoop HDFS
**Dataset:** IPL Ball-by-Ball Data (2008–2019) — Kaggle

---

## 1. Introduction

The Indian Premier League (IPL) is one of the world's most data-rich cricket tournaments. This project applies Big Data technologies — specifically Apache Hadoop and Apache Hive — to analyse ball-by-ball IPL match data spanning over 10 seasons and approximately 180,000 deliveries.

### Objectives
- Store large-scale IPL data on HDFS
- Query it efficiently using HiveQL
- Extract 10 meaningful cricket analytics

---

## 2. Dataset Description

| File | Rows | Description |
|---|---|---|
| matches.csv | ~951 | One row per match — teams, venue, winner, season |
| deliveries.csv | ~179,078 | Ball-by-ball — batsman, bowler, runs, dismissals |

**Source:** https://www.kaggle.com/datasets/manasgarg/ipl

### Key Columns Used

**matches.csv:** id, season, team1, team2, winner, venue, toss_winner

**deliveries.csv:** match_id, inning, batting_team, bowling_team, over, ball, batsman, bowler, batsman_runs, extra_runs, total_runs, player_dismissed, dismissal_kind

---

## 3. System Architecture

```
CSV Files (Local)
      ↓
  HDFS Upload
      ↓
  Hive Tables (External)
      ↓
  HiveQL Queries → MapReduce Jobs
      ↓
  Output CSV Files (HDFS → Local)
```

---

## 4. Analyses Performed

### Analysis 1 — Top 20 Batsmen
**Goal:** Find the highest run-scorers and their strike rates.

**Logic:** Sum `batsman_runs` per player, excluding wide deliveries. Calculate strike rate as (runs / balls faced) × 100.

**Output Columns:** batsman, total_runs, balls_faced, strike_rate

---

### Analysis 2 — Top 20 Bowlers
**Goal:** Find bowlers with the most wickets in IPL history.

**Logic:** Count rows where `player_dismissed` is not null, excluding run-outs (not the bowler's credit).

**Output Columns:** bowler, wickets

---

### Analysis 3 — Team Batting Stats
**Goal:** Compare batting run rates across all IPL franchises.

**Logic:** Aggregate total runs and balls per team, compute run rate = (runs / valid balls) × 6.

**Output Columns:** batting_team, total_runs, extras, total_balls, run_rate

---

### Analysis 4 — Powerplay vs Death Phase
**Goal:** Compare how teams bat in different match phases.

**Logic:** Classify overs 1–6 as Powerplay, 7–15 as Middle, 16–20 as Death. Aggregate runs per phase per team.

**Output Columns:** batting_team, phase, runs_scored, balls_bowled, wickets_lost, run_rate

---

### Analysis 5 — Boundaries
**Goal:** Find who hits the most 4s and 6s.

**Logic:** Count rows where `batsman_runs = 4` (fours) or `batsman_runs = 6` (sixes).

**Output Columns:** batsman, fours, sixes, total_boundaries, boundary_runs

---

### Analysis 6 — Extras / Bowling Discipline
**Goal:** Find which team gives away fewest extras — best bowling discipline.

**Logic:** Sum all extra types (wides, no-balls, byes, leg-byes) per bowling team. Normalize by total balls to get extras per 100 balls.

**Output Columns:** bowling_team, wides, no_balls, byes, leg_byes, total_extras, total_balls, extras_per_100_balls

---

### Analysis 7 — Dismissal Types
**Goal:** Understand how batsmen get out most commonly.

**Logic:** Group by `dismissal_kind` where a wicket fell, calculate percentage share using window function.

**Output Columns:** dismissal_kind, total_dismissals, percentage

---

### Analysis 8 — Inning Scores
**Goal:** Find average, highest, and lowest team totals per innings.

**Logic:** Subquery sums runs per match per inning, outer query applies AVG/MAX/MIN.

**Output Columns:** inning, avg_score, max_score, min_score, total_innings_played

---

### Analysis 9 — Economy Rates
**Goal:** Find the most economical bowlers (minimum 100 overs bowled).

**Logic:** Filter to legal deliveries, group by bowler, compute economy = (runs / balls) × 6. Apply HAVING filter for minimum 600 balls.

**Output Columns:** bowler, legal_balls, overs_bowled, runs_conceded, economy_rate, wickets

---

### Analysis 10 — Head-to-Head
**Goal:** Compare how teams perform when batting against specific opponents.

**Logic:** Group deliveries by batting_team and bowling_team pair to compute runs and run rate in each matchup.

**Output Columns:** batting_team, bowling_team, matches_played, total_runs, run_rate

---

## 5. Tools & Technologies

| Tool | Version | Purpose |
|---|---|---|
| Apache Hadoop | 3.3.x | Distributed storage (HDFS) & processing (YARN) |
| Apache Hive | 3.1.x | SQL-like querying on HDFS data |
| Apache Pig | 0.17.x | Scripted data transformations |
| Java | 11 | Runtime for Hadoop/Hive |
| VS Code | Latest | Code editor |
| WSL (Ubuntu) | 20.04+ | Linux environment on Windows |

---

## 6. Results Summary

*(Fill in after running your queries)*

| Analysis | Key Finding |
|---|---|
| Top Batsman | _____________ with _____ runs |
| Top Bowler | _____________ with _____ wickets |
| Best Run Rate Team | _____________ at _____ RPO |
| Best Powerplay Team | _____________ at _____ RPO |
| Most Boundaries | _____________ with _____ boundaries |
| Best Discipline Team | _____________ with _____ extras/100 balls |
| Most Common Dismissal | _____________ (___%) |
| Avg 1st Innings Score | _____ runs |
| Best Economy Bowler | _____________ at _____ RPO |
| Best H2H Matchup | _____ vs _____ |

---

## 7. Conclusion

This project demonstrated the use of Apache Hive and Hadoop to efficiently process and query large-scale cricket data. The ball-by-ball dataset with ~180,000 rows would be slow to process in traditional tools, but Hive's distributed execution makes it fast and scalable. The 10 analyses provide comprehensive statistical insights into IPL batting, bowling, and team performance.

---

## 8. References

1. IPL Dataset — https://www.kaggle.com/datasets/manasgarg/ipl
2. Apache Hive Documentation — https://hive.apache.org/
3. Apache Hadoop Documentation — https://hadoop.apache.org/
4. Apache Pig Documentation — https://pig.apache.org/
