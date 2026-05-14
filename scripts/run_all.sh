#!/bin/bash
# ============================================================
#  run_all.sh — Run all 10 IPL analyses in sequence
#  Usage: bash scripts/run_all.sh
#  (Run setup_hdfs.sh first if you haven't already)
# ============================================================

set -e

# Track start time
START_TIME=$(date +%s)

echo ""
echo "=================================================="
echo "  🏏 IPL Big Data Analytics — Running All Queries"
echo "=================================================="
echo ""

# ── Helper function ──────────────────────────────────────────
run_query() {
    local step=$1
    local label=$2
    local file=$3

    echo "──────────────────────────────────────────────────"
    echo "  [$step/11] $label"
    echo "──────────────────────────────────────────────────"
    hive -f "$file"
    echo "  ✅ Done: $label"
    echo ""
}

# ── Step 1: Create Tables ─────────────────────────────────────
run_query "1" "Create Database & Tables"   "hive/01_create_tables.hql"

# ── Steps 2-11: Run Each Analysis ────────────────────────────
run_query "2"  "Top 20 Batsmen"            "hive/02_top_batsmen.hql"
run_query "3"  "Top 20 Bowlers"            "hive/03_top_bowlers.hql"
run_query "4"  "Team Batting Stats"        "hive/04_team_batting.hql"
run_query "5"  "Powerplay vs Death Phase"  "hive/05_phase_analysis.hql"
run_query "6"  "Boundaries (4s & 6s)"      "hive/06_boundaries.hql"
run_query "7"  "Extras / Discipline"       "hive/07_extras.hql"
run_query "8"  "Dismissal Types"           "hive/08_dismissals.hql"
run_query "9"  "Inning Scores"             "hive/09_inning_scores.hql"
run_query "10" "Economy Rates"             "hive/10_economy.hql"
run_query "11" "Head-to-Head"              "hive/11_head_to_head.hql"

# ── Copy HDFS Results to Local output/ folder ─────────────────
echo "──────────────────────────────────────────────────"
echo "  Saving results to output/ folder..."
echo "──────────────────────────────────────────────────"

mkdir -p output

hdfs dfs -getmerge /ipl/output/top_batsmen    output/top_batsmen.csv
hdfs dfs -getmerge /ipl/output/top_bowlers    output/top_bowlers.csv
hdfs dfs -getmerge /ipl/output/team_batting   output/team_batting.csv
hdfs dfs -getmerge /ipl/output/phase_analysis output/phase_analysis.csv
hdfs dfs -getmerge /ipl/output/boundaries     output/boundaries.csv
hdfs dfs -getmerge /ipl/output/extras         output/extras.csv
hdfs dfs -getmerge /ipl/output/dismissals     output/dismissals.csv
hdfs dfs -getmerge /ipl/output/inning_scores  output/inning_scores.csv
hdfs dfs -getmerge /ipl/output/economy        output/economy.csv
hdfs dfs -getmerge /ipl/output/head_to_head   output/head_to_head.csv

# ── Summary ───────────────────────────────────────────────────
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo "=================================================="
echo "  ✅ ALL ANALYSES COMPLETE!"
echo "  Total time: ${ELAPSED} seconds"
echo ""
echo "  Output files:"
ls -lh output/*.csv 2>/dev/null | awk '{print "   " $5 "  " $9}'
echo ""
echo "  Open any CSV in VS Code to view results."
echo "  (Install 'Rainbow CSV' extension for nice formatting)"
echo "=================================================="
