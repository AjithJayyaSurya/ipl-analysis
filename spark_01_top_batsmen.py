"""
Analysis 1: Top 20 Batsmen - Using Apache Spark (PySpark)
Auto-installs Spark if not present

Run: python spark_01_top_batsmen.py
"""
import sys
import subprocess
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def ensure_pyspark():
    """Install PySpark if not present"""
    try:
        import pyspark
        return True
    except ImportError:
        print("[INFO] Installing PySpark...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyspark>=3.5.0', '-q'])
        return True

def analyze_with_spark():
    """Find top 20 batsmen using Spark"""
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import sum as spark_sum, count, col, desc, round as spark_round

    # Create Spark session
    spark = SparkSession.builder \
        .appName("Top_Batsmen") \
        .master("local[*]") \
        .config("spark.driver.memory", "1g") \
        .getOrCreate()

    # Load data
    deliveries = spark.read.csv("datasets/deliveries.csv", header=True, inferSchema=True)

    # Filter and analyze
    result = deliveries.filter(
        (col("wide_runs") == 0) & (col("is_super_over") == 0)
    ).groupBy("batsman").agg(
        spark_sum("batsman_runs").alias("total_runs"),
        count("*").alias("balls_faced")
    ).filter(
        col("balls_faced") >= 100
    ).withColumn(
        "strike_rate",
        spark_round(col("total_runs") * 100.0 / col("balls_faced"), 2)
    ).sort(
        desc("total_runs")
    ).limit(20)

    # Show results
    print("\n=== Top 20 Batsmen (Using Apache Spark) ===\n")
    result.show(truncate=False)

    # Save to CSV
    result.coalesce(1).write.mode("overwrite").csv("output/spark_01_top_batsmen", header=True)
    print("\n[OK] Saved to output/spark_01_top_batsmen/\n")

    spark.stop()

if __name__ == "__main__":
    ensure_pyspark()
    analyze_with_spark()
