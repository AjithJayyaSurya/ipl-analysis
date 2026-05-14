"""
IPL Big Data Analytics - Apache Spark Edition (PySpark)

All 10 analyses using Apache Spark (works on Windows without Linux/Docker)

Auto-installs Spark on first run.

Run: python run_all_spark.py
"""
import sys
import subprocess
import os
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_pyspark():
    """Check if PySpark is installed, install if not"""
    try:
        import pyspark
        print(f"[OK] PySpark {pyspark.__version__} found")
        return True
    except ImportError:
        print("[INFO] PySpark not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyspark>=3.5.0'])
        print("[OK] PySpark installed successfully\n")
        return True

def check_datasets():
    """Verify CSV files exist"""
    if not Path('datasets/matches.csv').exists():
        print("[ERROR] datasets/matches.csv not found!")
        print("   Download from: https://www.kaggle.com/datasets/manasgarg/ipl")
        return False

    if not Path('datasets/deliveries.csv').exists():
        print("[ERROR] datasets/deliveries.csv not found!")
        return False

    print("[OK] datasets/matches.csv found")
    print("[OK] datasets/deliveries.csv found")
    return True

def create_output_dir():
    """Create output directory"""
    Path('output').mkdir(exist_ok=True)
    print("[OK] Output directory ready")

def run_spark_analyses():
    """Run all analyses using Spark"""
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import sum as spark_sum, count, when, round as spark_round, col, desc
    import time

    # Create Spark Session
    spark = SparkSession.builder \
        .appName("IPL_Analytics") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

    print("\n" + "="*60)
    print("  IPL Big Data Analytics - Apache Spark Edition")
    print("="*60 + "\n")

    # Load data
    print("[INFO] Loading datasets..."
)
    matches_df = spark.read.csv("datasets/matches.csv", header=True, inferSchema=True)
    deliveries_df = spark.read.csv("datasets/deliveries.csv", header=True, inferSchema=True)
    print("[OK] Data loaded\n")

    # Analysis 1: Top 20 Batsmen
    print("[1/10] Top 20 Batsmen...")
    batsmen = deliveries_df.filter((col("wide_runs") == 0) & (col("is_super_over") == 0)) \
        .groupBy("batsman") \
        .agg(
            spark_sum("batsman_runs").alias("total_runs"),
            count("*").alias("balls_faced")
        ) \
        .filter(col("balls_faced") >= 100) \
        .withColumn("strike_rate", spark_round(col("total_runs") * 100.0 / col("balls_faced"), 2)) \
        .sort(desc("total_runs")) \
        .limit(20)

    batsmen.coalesce(1).write.mode("overwrite").csv("output/spark_01_top_batsmen", header=True)
    print("  [Done]\n")

    # Analysis 2: Top 20 Bowlers
    print("[2/10] Top 20 Bowlers...")
    bowlers = deliveries_df.filter(
        (col("player_dismissed").isNotNull()) &
        (col("player_dismissed") != "") &
        (~col("dismissal_kind").isin(["run out", "retired hurt", "obstructing the field"])) &
        (col("is_super_over") == 0)
    ) \
        .groupBy("bowler") \
        .agg(count("*").alias("wickets")) \
        .sort(desc("wickets")) \
        .limit(20)

    bowlers.coalesce(1).write.mode("overwrite").csv("output/spark_02_top_bowlers", header=True)
    print("  [Done]\n")

    # Analysis 3: Team Batting Stats
    print("[3/10] Team Batting Stats...")
    team_stats = deliveries_df.filter(col("is_super_over") == 0) \
        .groupBy("batting_team") \
        .agg(
            spark_sum("total_runs").alias("total_runs"),
            spark_sum("batsman_runs").alias("bat_runs"),
            spark_sum("extra_runs").alias("extras"),
            count("*").alias("total_balls"),
            spark_sum(when(col("wide_runs") > 0, 1).otherwise(0)).alias("wide_count")
        ) \
        .withColumn("run_rate", spark_round(
            col("total_runs") * 6.0 / (col("total_balls") - col("wide_count")), 2
        )) \
        .sort(desc("run_rate"))

    team_stats.coalesce(1).write.mode("overwrite").csv("output/spark_03_team_batting", header=True)
    print("  [Done]\n")

    # Analysis 4: Phase Analysis
    print("[4/10] Phase Analysis...")
    from pyspark.sql.functions import when as spark_when

    phase_df = deliveries_df.filter(col("is_super_over") == 0) \
        .withColumn("phase",
            spark_when((col("over") >= 1) & (col("over") <= 6), "Powerplay")
            .when((col("over") >= 7) & (col("over") <= 15), "Middle")
            .otherwise("Death")
        ) \
        .groupBy("batting_team", "phase") \
        .agg(
            spark_sum("total_runs").alias("runs_scored"),
            count("*").alias("balls_bowled"),
            spark_sum(when((col("player_dismissed").isNotNull()) & (col("player_dismissed") != ""), 1).otherwise(0)).alias("wickets_lost")
        ) \
        .withColumn("run_rate", spark_round(col("runs_scored") * 6.0 / col("balls_bowled"), 2)) \
        .sort("batting_team", "phase")

    phase_df.coalesce(1).write.mode("overwrite").csv("output/spark_04_phase_analysis", header=True)
    print("  [Done]\n")

    # Analysis 5: Boundaries
    print("[5/10] Boundaries...")
    boundaries = deliveries_df.filter(col("is_super_over") == 0) \
        .groupBy("batsman") \
        .agg(
            spark_sum(when(col("batsman_runs") == 4, 1).otherwise(0)).alias("fours"),
            spark_sum(when(col("batsman_runs") == 6, 1).otherwise(0)).alias("sixes"),
            spark_sum(when((col("batsman_runs") == 4) | (col("batsman_runs") == 6), 1).otherwise(0)).alias("total_boundaries"),
            (spark_sum(when(col("batsman_runs") == 4, 4).otherwise(0)) +
             spark_sum(when(col("batsman_runs") == 6, 6).otherwise(0))).alias("boundary_runs")
        ) \
        .sort(desc("total_boundaries")) \
        .limit(20)

    boundaries.coalesce(1).write.mode("overwrite").csv("output/spark_05_boundaries", header=True)
    print("  [Done]\n")

    # Analysis 6: Extras
    print("[6/10] Extras - Bowling Discipline...")
    extras = deliveries_df.filter(col("is_super_over") == 0) \
        .groupBy("bowling_team") \
        .agg(
            spark_sum("wide_runs").alias("total_wides"),
            spark_sum("noball_runs").alias("total_no_balls"),
            spark_sum("bye_runs").alias("total_byes"),
            spark_sum("legbye_runs").alias("total_leg_byes"),
            spark_sum("extra_runs").alias("total_extras"),
            count("*").alias("total_balls_bowled")
        ) \
        .withColumn("extras_per_100_balls", spark_round(col("total_extras") * 100.0 / col("total_balls_bowled"), 2)) \
        .sort("extras_per_100_balls")

    extras.coalesce(1).write.mode("overwrite").csv("output/spark_06_extras", header=True)
    print("  [Done]\n")

    # Analysis 7: Dismissals
    print("[7/10] Dismissals...")
    dismissals = deliveries_df.filter(
        (col("player_dismissed").isNotNull()) & (col("player_dismissed") != "")
    ) \
        .groupBy("dismissal_kind") \
        .agg(count("*").alias("total_dismissals")) \
        .sort(desc("total_dismissals"))

    dismissals.coalesce(1).write.mode("overwrite").csv("output/spark_07_dismissals", header=True)
    print("  [Done]\n")

    # Analysis 8: Inning Scores
    print("[8/10] Inning Scores...")
    inning_stats = deliveries_df.filter(col("is_super_over") == 0) \
        .groupBy("match_id", "inning") \
        .agg(spark_sum("total_runs").alias("inning_total")) \
        .groupBy("inning") \
        .agg(
            spark_round(col("avg(inning_total)"), 2).alias("avg_score"),
            col("max(inning_total)").alias("max_score"),
            col("min(inning_total)").alias("min_score"),
            count("*").alias("total_innings_played")
        ) \
        .sort("inning")

    inning_stats.coalesce(1).write.mode("overwrite").csv("output/spark_08_inning_scores", header=True)
    print("  [Done]\n")

    # Analysis 9: Economy Rates
    print("[9/10] Economy Rates...")
    economy = deliveries_df.filter((col("is_super_over") == 0) & (col("wide_runs") == 0)) \
        .groupBy("bowler") \
        .agg(
            count("*").alias("legal_balls"),
            spark_sum("total_runs").alias("runs_conceded"),
            spark_sum(when(
                (col("player_dismissed").isNotNull()) &
                (col("player_dismissed") != "") &
                (~col("dismissal_kind").isin(["run out", "retired hurt"])), 1
            ).otherwise(0)).alias("wickets")
        ) \
        .filter(col("legal_balls") >= 600) \
        .withColumn("overs_bowled", spark_round(col("legal_balls") / 6.0, 1)) \
        .withColumn("economy_rate", spark_round(col("runs_conceded") * 6.0 / col("legal_balls"), 2)) \
        .sort("economy_rate") \
        .limit(20)

    economy.coalesce(1).write.mode("overwrite").csv("output/spark_09_economy", header=True)
    print("  [Done]\n")

    # Analysis 10: Head-to-Head
    print("[10/10] Head-to-Head...")
    h2h = deliveries_df.filter(col("is_super_over") == 0) \
        .groupBy("batting_team", "bowling_team") \
        .agg(
            count("*").alias("balls"),
            spark_sum("total_runs").alias("total_runs_scored")
        ) \
        .withColumn("run_rate", spark_round(col("total_runs_scored") * 6.0 / col("balls"), 2)) \
        .select("batting_team", "bowling_team", "total_runs_scored", "run_rate") \
        .sort("batting_team", desc("run_rate"))

    h2h.coalesce(1).write.mode("overwrite").csv("output/spark_10_head_to_head", header=True)
    print("  [Done]\n")

    spark.stop()
    print("="*60)
    print("  ALL ANALYSES COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    # Check Spark
    if not check_pyspark():
        sys.exit(1)

    print()

    # Check datasets
    if not check_datasets():
        sys.exit(1)

    print()

    # Create output dir
    create_output_dir()

    print()

    # Run analyses
    try:
        run_spark_analyses()
        print("\n[OK] Results saved to output/ folder")
        print("[INFO] Open CSV files in VS Code\n")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
