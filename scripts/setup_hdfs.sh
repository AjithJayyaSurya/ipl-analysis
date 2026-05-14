#!/bin/bash
# ============================================================
#  setup_hdfs.sh — Upload IPL datasets to HDFS
#  Run this ONCE before running any Hive queries
#  Usage: bash scripts/setup_hdfs.sh
# ============================================================

set -e   # Exit immediately on any error

echo ""
echo "=================================================="
echo "  IPL Big Data Project — HDFS Setup"
echo "=================================================="

# ── Check Hadoop is running ──────────────────────────────────
echo ""
echo "▶ Checking Hadoop services..."
RUNNING=$(jps | grep -c "NameNode\|DataNode" || true)
if [ "$RUNNING" -lt 2 ]; then
    echo "❌ Hadoop is not running! Starting now..."
    start-dfs.sh
    start-yarn.sh
    sleep 5
    echo "✅ Hadoop started."
else
    echo "✅ Hadoop is already running."
fi

# ── Check CSV files exist locally ────────────────────────────
echo ""
echo "▶ Checking dataset files..."

if [ ! -f "datasets/matches.csv" ]; then
    echo "❌ ERROR: datasets/matches.csv not found!"
    echo "   Please download from: https://www.kaggle.com/datasets/manasgarg/ipl"
    echo "   and place both CSV files in the datasets/ folder."
    exit 1
fi

if [ ! -f "datasets/deliveries.csv" ]; then
    echo "❌ ERROR: datasets/deliveries.csv not found!"
    echo "   Please download from: https://www.kaggle.com/datasets/manasgarg/ipl"
    exit 1
fi

echo "✅ matches.csv   found ($(wc -l < datasets/matches.csv) rows)"
echo "✅ deliveries.csv found ($(wc -l < datasets/deliveries.csv) rows)"

# ── Create HDFS directories ───────────────────────────────────
echo ""
echo "▶ Creating HDFS directory structure..."

hdfs dfs -mkdir -p /ipl/data/matches
hdfs dfs -mkdir -p /ipl/data/deliveries
hdfs dfs -mkdir -p /ipl/output
hdfs dfs -chmod -R 777 /ipl

echo "✅ HDFS directories created."

# ── Upload CSV files ─────────────────────────────────────────
echo ""
echo "▶ Uploading matches.csv to HDFS..."
hdfs dfs -put -f datasets/matches.csv /ipl/data/matches/
echo "✅ matches.csv uploaded."

echo ""
echo "▶ Uploading deliveries.csv to HDFS..."
hdfs dfs -put -f datasets/deliveries.csv /ipl/data/deliveries/
echo "✅ deliveries.csv uploaded."

# ── Verify upload ─────────────────────────────────────────────
echo ""
echo "▶ Verifying HDFS upload..."
hdfs dfs -ls /ipl/data/matches/
hdfs dfs -ls /ipl/data/deliveries/

echo ""
echo "=================================================="
echo "  ✅ HDFS Setup Complete!"
echo "  Next step: Run 'bash scripts/run_all.sh'"
echo "=================================================="
